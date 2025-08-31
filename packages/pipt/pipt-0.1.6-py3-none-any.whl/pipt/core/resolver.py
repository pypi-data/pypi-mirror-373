from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from .errors import (
    ResolutionConflictError,
    ResolutionTimeoutError,
    MetadataError,
    PipSubprocessError,
    OldPipError,
    EnvironmentCompatibilityError,
    SourceBuildError,
)
from .index import fetch_package_metadata, get_vmax_for_package
from .options import Options


@dataclass
class ResolutionResult:
    constraints: Dict[str, SpecifierSet]
    plan_versions: Dict[str, Version]


def _py_version_str(options: Options) -> str:
    return options.python_version or f"{sys.version_info.major}.{sys.version_info.minor}"


def _releases_support_python(meta: dict, up_to: Version, py_ver: str) -> bool:
    try:
        from packaging.version import Version as V
    except Exception:
        return True
    rels = (meta or {}).get("releases", {}) or {}
    for ver_str, files in rels.items():
        try:
            if V(ver_str) > up_to:
                continue
        except Exception:
            continue
        # If any file for this release has compatible Requires-Python (or none), accept
        files = files or []
        if not files:
            # No file info; assume possibly compatible
            return True
        for f in files:
            req = (f or {}).get("requires_python")
            if not req:
                return True
            try:
                spec = SpecifierSet(req)
                if spec.contains(py_ver, prereleases=True):
                    return True
            except Exception:
                # Be permissive on parse errors
                return True
    return False


def _extract_conflict_summary(stderr: str) -> str:
    lines = (stderr or "").splitlines()
    keep: List[str] = []
    capture = False
    for ln in lines:
        low = ln.lower().strip()
        if "the conflict is caused by" in low or "because" in low and "depends on" in low:
            capture = True
        if capture:
            # stop at empty separator or a common end marker
            if not ln.strip():
                if keep:
                    break
            keep.append(ln)
        # also capture common requirement lines
        if ("requires" in low and "python" in low) or ("depends on" in low and "<" in low):
            keep.append(ln)
    if not keep:
        # fallback to last ~15 lines of stderr
        keep = lines[-15:]
    return "\n".join(keep).strip()


def _parse_vmax_from_constraint(spec_str: Optional[str]) -> Optional[Version]:
    if not spec_str:
        return None
    try:
        ss = SpecifierSet(spec_str)
        # Try to find a single <=X.Y.Z constraint
        for sp in ss:
            if sp.operator in ("<=", "=="):
                try:
                    return Version(sp.version)
                except Exception:
                    continue
    except Exception:
        return None
    return None


def _requires_python_for_version(meta: dict, ver: Version) -> List[str]:
    rels = (meta or {}).get("releases", {}) or {}
    specs: List[str] = []
    files = rels.get(str(ver), []) or []
    for f in files:
        rp = (f or {}).get("requires_python")
        if rp and rp not in specs:
            specs.append(rp)
    return specs


def _wheel_python_tags_for_version(meta: dict, ver: Version) -> List[str]:
    import re as _re

    rels = (meta or {}).get("releases", {}) or {}
    files = rels.get(str(ver), []) or []
    tags: List[str] = []
    for f in files:
        fn = (f or {}).get("filename") or ""
        # Wheel filename segments: name-version(-build)?-pyver-abi-plat.whl
        # Extract python tag segment heuristically
        parts = fn.split("-")
        if len(parts) >= 4:
            pyseg = parts[-3]
        else:
            # fallback: search cp3x in whole filename
            pyseg = fn
        for m in _re.findall(r"cp3(\d{1,2})", pyseg):
            ver_minor = int(m)
            tag = f"3.{ver_minor if ver_minor < 10 else int(str(ver_minor))}"
            # Fix cp310+ mapping correctly (cp310 -> 3.10 etc.)
            if ver_minor >= 10 and len(m) == 2:
                tag = f"3.{m}"
            if tag not in tags:
                tags.append(tag)
        if "py3" in pyseg and "3" not in tags:
            tags.append("3")
    # Sort ascending semantic
    def _key(v: str) -> tuple:
        try:
            major, minor = v.split(".")
            return (int(major), int(minor))
        except Exception:
            return (9_999, 9_999)
    return sorted(tags, key=_key)


def _suggest_python_from_specs(specs_or_meta, ver: Optional[Version] = None) -> Optional[str]:
    # Accept both (list of spec strings) or (meta dict plus version)
    if isinstance(specs_or_meta, dict) and ver is not None:
        meta = specs_or_meta
        wheel_pys = _wheel_python_tags_for_version(meta, ver)
        for cand in wheel_pys:
            if cand in ("3",):
                continue
            return cand
        specs = _requires_python_for_version(meta, ver)
    else:
        specs = specs_or_meta  # type: ignore
    from packaging.specifiers import SpecifierSet as _SS

    mins: List[str] = []
    for s in specs:
        try:
            ss = _SS(s)
        except Exception:
            continue
        # try to extract minimal allowed 3.x
        minv: Optional[Tuple[int, int]] = None
        for sp in ss:
            if sp.operator in (">=", ">="):
                try:
                    parts = sp.version.split(".")
                    if len(parts) >= 2 and parts[0] == "3":
                        cand = (3, int(parts[1]))
                        if minv is None or cand > minv:
                            minv = cand
                except Exception:
                    continue
        if minv:
            mins.append(f"{minv[0]}.{minv[1]}")
    # Choose smallest suggested
    if mins:
        try:
            return sorted(mins, key=lambda v: (int(v.split('.')[0]), int(v.split('.')[1])))[0]
        except Exception:
            return mins[0]
    return None


def _suggest_python_from_specs_or_wheels(meta: dict, ver: Version) -> Optional[str]:
    wheel_pys = _wheel_python_tags_for_version(meta, ver)
    for cand in wheel_pys:
        if cand in ("3",):
            continue
        return cand
    specs = _requires_python_for_version(meta, ver)
    return _suggest_python_from_specs(specs)


def _suggestions_for_conflict(target_pkg: Optional[str], constraint_str: Optional[str], options: Options) -> str:
    pyv, plat = _environment_summary(options)
    tips = [
        "- Move the cutoff date forward to include newer compatible releases.",
        "- Try allowing pre-releases with --pre if appropriate.",
        "- Consider using an older Python interpreter that matches the cutoff era.",
        "- If you know what you’re doing, install without dependencies: try: pipt install <pkg> --date <date> --no-deps (not recommended).",
        "- Add or adjust a constraints file (-c) to pin transitive dependencies to versions available before the cutoff.",
        "- Re-run with -v to see the exact pip command and full resolver output.",
    ]
    head = [
        "Dependency conflict detected by pip's resolver.",
        f"Environment: Python {pyv} / {plat}.",
    ]
    if target_pkg and constraint_str:
        head.append(f"Requested: {target_pkg}{constraint_str}")
    return "\n".join(head + ["", "Suggestions:"] + tips)


def _pip_version_check():
    out = subprocess.check_output([sys.executable, "-m", "pip", "--version"], text=True)
    # e.g., "pip 25.2 from ..."
    parts = out.split()
    if len(parts) >= 2:
        ver = parts[1]
        try:
            from packaging.version import Version as V

            if V(ver) < V("23.0"):
                raise OldPipError(ver)
        except Exception:
            pass


def _verbose_print(options: Options, msg: str):
    if options.verbose:
        print(f"[VERBOSE] {msg}")


def _write_constraints_file(path: Path, constraints: Dict[str, SpecifierSet]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for name, spec in sorted(constraints.items()):
            f.write(f"{name}{spec}\n" if str(spec) else f"{name}\n")


def _pip_base_args(
    report_file: Optional[Path] = None,
    constraints_file: Optional[Path] = None,
    options: Optional[Options] = None,
) -> List[str]:
    args = [sys.executable, "-m", "pip", "install"]
    if report_file is not None:
        args += ["--dry-run", "--report", str(report_file)]
    if constraints_file is not None:
        args += ["-c", str(constraints_file)]
    if options and options.user_constraint_files:
        for c in options.user_constraint_files:
            args += ["-c", c]
    # Only force binary wheels when requested (historical mode)
    if options is None or options.binary_only:
        args += [
            "--prefer-binary",
            "--only-binary",
            ":all:",
        ]
    if options and options.no_deps:
        args += ["--no-deps"]
    args += [
        "--disable-pip-version-check",
        "--no-input",
    ]
    return args


def _classify_pip_error(stderr: str) -> str:
    """Return a classification label for pip failure based on stderr content.

    Returns one of: 'conflict', 'env', 'source', 'unknown'
    """
    msg = (stderr or "").lower()
    if not msg:
        return "unknown"
    # Treat any Requires-Python indication as environment incompatibility
    if "requires-python" in msg or "python version" in msg:
        return "env"
    if "resolutionimpossible" in msg or "conflicting dependencies" in msg:
        return "conflict"
    if (
        "no matching distribution found" in msg
        or "could not find a version that satisfies the requirement" in msg
        or "is not a supported wheel on this platform" in msg
        or "ignored the following versions that require a different python version" in msg
    ):
        return "env"
    if (
        "failed building wheel for" in msg
        or "building wheel for" in msg and "did not run successfully" in msg
        or "error: subprocess-exited-with-error" in msg
        or "build failed" in msg
    ):
        return "source"
    return "unknown"


def _environment_summary(options: Options) -> Tuple[str, str]:
    import platform

    py_ver = options.python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
    plat = f"{sys.platform}-{platform.machine()}"
    return py_ver, plat


def _run_pip_dry_run(
    target_args: List[str], constraints_file: Optional[Path], report_file: Path, options: Options
) -> Tuple[int, str, str]:
    cmd = _pip_base_args(report_file, constraints_file, options) + target_args
    _verbose_print(options, f"Running pip: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if options.verbose:
        if proc.stdout:
            _verbose_print(options, "----- pip stdout (dry-run) -----")
            print(proc.stdout, end="")
        if proc.stderr:
            _verbose_print(options, "----- pip stderr (dry-run) -----")
            print(proc.stderr, end="")
    return proc.returncode, proc.stdout, proc.stderr


def _parse_plan(report_path: Path) -> Dict[str, Version]:
    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    plan: Dict[str, Version] = {}
    if isinstance(data, list):
        for entry in data:
            if not isinstance(entry, dict):
                continue
            meta = entry.get("metadata") or {}
            name = (meta.get("name") or entry.get("name") or "").lower()
            ver = meta.get("version") or entry.get("version")
            if name and ver:
                try:
                    plan[name] = Version(str(ver))
                except Exception:
                    pass
    else:
        for entry in data.get("install", []):
            name = (entry.get("name") or "").lower()
            ver = entry.get("version")
            if name and ver:
                try:
                    plan[name] = Version(str(ver))
                except Exception:
                    pass
    return plan


async def resolve_dependency_plan(
    targets: List[Requirement], cutoff_dt: Optional[datetime], options: Options
) -> ResolutionResult:
    _pip_version_check()

    # If no cutoff is supplied, do a single dry-run with pip and return the plan.
    if cutoff_dt is None:
        with tempfile.TemporaryDirectory() as td:
            rfile = Path(td) / "report.json"
            target_args = [str(r) for r in targets]
            code, out, err = _run_pip_dry_run(target_args, None, rfile, options)
            if code != 0:
                classification = _classify_pip_error(err or out)
                first_target = targets[0].name if targets else None
                if classification == "conflict":
                    summary = _extract_conflict_summary(err or out)
                    msg = _suggestions_for_conflict(first_target, None, options)
                    raise ResolutionConflictError(f"{summary}\n\n{msg}")
                if classification == "env":
                    pyv, plat = _environment_summary(options)
                    raise EnvironmentCompatibilityError(
                        package=first_target,
                        latest_allowed=None,
                        python_version=pyv,
                        platform_str=plat,
                        details=(err or out),
                        extra_hints=None,
                    )
                if classification == "source":
                    raise SourceBuildError(package=first_target, details=(err or out))
                raise PipSubprocessError(code, (err or out))
            plan = _parse_plan(rfile)
            if not plan:
                _verbose_print(options, "Empty plan from pip report: nothing to do (already satisfied)")
                return ResolutionResult(constraints={}, plan_versions={})
            return ResolutionResult(constraints={}, plan_versions=plan)

    constraints: Dict[str, SpecifierSet] = {}

    async def seed_for_target(req: Requirement) -> None:
        meta = await fetch_package_metadata(
            req.name,
            options.index_url,
            ttl_seconds=options.cache_ttl_seconds,
            cache_dir=options.cache_dir,
            verbose=options.verbose,
        )
        # Support date_mode
        if options.date_mode == "nearest":
            from .index import get_nearest_for_package  # local import to avoid cycle

            nearest = await get_nearest_for_package(meta, cutoff_dt, options)
            if nearest is None:
                raise ResolutionConflictError(
                    f"No versions of {req.name} near cutoff {cutoff_dt.isoformat()} for the given options",
                    package=req.name,
                )
            cap = SpecifierSet(f"=={nearest}")
            constraints[req.name.lower()] = cap
            _verbose_print(options, f"Seed(nearest) {req.name}: =={nearest}")
            return

        vmax = await get_vmax_for_package(meta, cutoff_dt, options)
        if vmax is None:
            raise ResolutionConflictError(
                f"No versions of {req.name} are available on or before cutoff {cutoff_dt.isoformat()} for the given options",
                package=req.name,
            )
        # Pre-check Python compatibility of releases up to vmax to avoid opaque conflicts
        py_str = _py_version_str(options)
        if not _releases_support_python(meta, vmax, py_str):
            pyv, plat = _environment_summary(options)
            # Try to suggest a minimum Python from wheels/specs
            py_suggest = _suggest_python_from_specs_or_wheels(meta, vmax)
            hints: List[str] = []
            if py_suggest:
                hints.append(f"Minimum suggested Python for {req.name}=={vmax}: {py_suggest}")
            extra = "\n".join(hints) if hints else None
            raise EnvironmentCompatibilityError(
                package=req.name,
                latest_allowed=f"<={vmax}",
                python_version=pyv,
                platform_str=plat,
                details=(
                    f"No releases of {req.name} up to {vmax} declare compatibility with Python {py_str}. "
                    "Use an older Python (e.g., 3.10/3.11 for early 2023 NumPy) or move the cutoff forward."
                ),
                extra_hints=extra,
            )
        cap = SpecifierSet(f"<={vmax}")
        combined = str(req.specifier & cap)
        constraints[req.name.lower()] = SpecifierSet(combined)
        _verbose_print(options, f"Seed {req.name}: {combined}")

    for req in targets:
        await seed_for_target(req)

    max_iter = options.max_iterations
    last_plan: Dict[str, Version] = {}
    for loop_idx in range(1, max_iter + 1):
        with tempfile.TemporaryDirectory() as td:
            cfile = Path(td) / "constraints.txt"
            rfile = Path(td) / "report.json"
            _write_constraints_file(cfile, constraints)
            _verbose_print(
                options,
                f"Loop {loop_idx}: constraints -> {[f'{k}{v}' for k, v in constraints.items()]}",
            )
            target_args = [str(r) for r in targets]
            code, out, err = _run_pip_dry_run(target_args, cfile, rfile, options)
            if code != 0:
                # Intelligent failure analysis
                classification = _classify_pip_error(err or out)
                first_target = targets[0].name if targets else None
                first_constraint = str(constraints.get(first_target or "", "")) if first_target else None
                if classification == "conflict":
                    summary = _extract_conflict_summary(err or out)
                    # Enrich with specific version and Python suggestion
                    vmax = _parse_vmax_from_constraint(first_constraint)
                    extra_lines: List[str] = []
                    if first_target and vmax is not None:
                        try:
                            meta = await fetch_package_metadata(
                                first_target,
                                options.index_url,
                                ttl_seconds=options.cache_ttl_seconds,
                                cache_dir=options.cache_dir,
                                verbose=options.verbose,
                            )
                            rps = _requires_python_for_version(meta, vmax)
                            rp_disp = "; ".join(rps) if rps else None
                            if rp_disp:
                                extra_lines.append(f"Requires-Python for {first_target}=={vmax}: {rp_disp}")
                            py_suggest = _suggest_python_from_specs_or_wheels(meta, vmax)
                            if py_suggest:
                                extra_lines.append(f"Suggested Python version: {py_suggest}")
                            extra_lines.append(f"Latest allowed by cutoff: {first_target}=={vmax}")
                        except Exception:
                            if vmax is not None:
                                extra_lines.append(f"Latest allowed by cutoff: {first_target}=={vmax}")
                    msg = _suggestions_for_conflict(first_target, first_constraint, options)
                    detail = ("\n".join(extra_lines) + "\n\n" if extra_lines else "")
                    raise ResolutionConflictError(f"{summary}\n\n{detail}{msg}")
                if classification == "env":
                    pyv, plat = _environment_summary(options)
                    raise EnvironmentCompatibilityError(
                        package=first_target,
                        latest_allowed=first_constraint,
                        python_version=pyv,
                        platform_str=plat,
                        details=(err or out),
                        extra_hints=None,
                    )
                if classification == "source":
                    raise SourceBuildError(package=first_target, details=(err or out))
                # Unknown
                raise PipSubprocessError(code, (err or out))
            last_plan = _parse_plan(rfile)
            if not last_plan:
                _verbose_print(options, "Empty plan from pip report: nothing to do (already satisfied)")
                return ResolutionResult(constraints=constraints, plan_versions={})

            violations: Dict[str, Version] = {}
            # Parallel fetch of metadata for plan packages
            from asyncio import gather

            async def vmax_for(name: str) -> Tuple[str, Optional[Version]]:
                meta = await fetch_package_metadata(
                    name,
                    options.index_url,
                    ttl_seconds=options.cache_ttl_seconds,
                    cache_dir=options.cache_dir,
                    verbose=options.verbose,
                )
                vmax = await get_vmax_for_package(meta, cutoff_dt, options)
                return name, vmax

            names = list(last_plan.keys())
            vmax_results = await gather(*(vmax_for(n) for n in names))
            vmax_map = {n: v for n, v in vmax_results}
            for name, chosen_ver in last_plan.items():
                vmax = vmax_map.get(name)
                if vmax is None or chosen_ver > vmax:
                    violations[name] = chosen_ver

            if not violations:
                _verbose_print(options, "Resolution stable!")
                return ResolutionResult(constraints=constraints, plan_versions=last_plan)

            for name in violations.keys():
                vmax = vmax_map.get(name)
                if vmax is None:
                    raise ResolutionConflictError(
                        f"All historical versions of {name} are incompatible with the given options by cutoff {cutoff_dt.date()}",
                        package=name,
                    )
                cap = SpecifierSet(f"<={vmax}")
                existing = constraints.get(name.lower(), SpecifierSet())
                constraints[name.lower()] = SpecifierSet(str(existing & cap))

    raise ResolutionTimeoutError(max_iter)


def run_final_pip_install(
    target_args: List[str],
    constraints_file: Optional[Path],
    options: Options,
    latest_constraints: Optional[Dict[str, SpecifierSet]] = None,
) -> int:
    cmd = _pip_base_args(None, constraints_file, options) + target_args
    _verbose_print(options, f"Running pip: {' '.join(cmd)}")
    # Stream output live but also capture for verbose dumps and errors
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout and proc.stderr
    stdout_buf: List[str] = []
    for line in proc.stdout:
        stdout_buf.append(line)
        print(line, end="")
    err_out = proc.stderr.read()
    code = proc.wait()
    if options.verbose:
        if stdout_buf:
            _verbose_print(options, "----- pip stdout (install) -----")
            print("".join(stdout_buf), end="")
        if err_out:
            _verbose_print(options, "----- pip stderr (install) -----")
            print(err_out, end="")
    if code != 0:
        classification = _classify_pip_error(err_out)
        # Try to infer a primary target
        pkg_name: Optional[str] = None
        try:
            first = target_args[0]
            if first and not first.startswith("-r"):
                pkg_name = Requirement(first).name
        except Exception:
            pkg_name = None
        latest_allowed: Optional[str] = None
        if latest_constraints and pkg_name:
            latest_allowed = str(latest_constraints.get(pkg_name.lower(), "")) or None
        if classification == "conflict":
            summary = _extract_conflict_summary(err_out)
            extra_lines: List[str] = []
            vmax = _parse_vmax_from_constraint(latest_allowed)
            if pkg_name and vmax is not None:
                # Non-async context: avoid fetching metadata here
                extra_lines.append(f"Latest allowed by cutoff: {pkg_name}=={vmax}")
            msg = _suggestions_for_conflict(pkg_name, latest_allowed, options)
            detail = ("\n".join(extra_lines) + "\n\n" if extra_lines else "")
            raise ResolutionConflictError(f"{summary}\n\n{detail}{msg}")
        if classification == "env":
            pyv, plat = _environment_summary(options)
            raise EnvironmentCompatibilityError(
                package=pkg_name,
                latest_allowed=latest_allowed,
                python_version=pyv,
                platform_str=plat,
                details=err_out,
                extra_hints=None,
            )
        if classification == "source":
            raise SourceBuildError(package=pkg_name, details=err_out)
        raise PipSubprocessError(code, err_out)
    return code


def write_lockfile(
    path: Path, plan: Dict[str, Version], cutoff: Optional[datetime], include_hashes: bool = False
) -> None:
    header = []
    if cutoff is None:
        header = [
            f"# Locked by pipt on {datetime.utcnow().date()} (no cutoff provided)\n",
            "# Do not edit by hand.\n",
        ]
    else:
        header = [
            f"# Locked by pipt on {datetime.utcnow().date()} for cutoff {cutoff.date()}\n",
            "# Do not edit by hand.\n",
        ]
    lines: List[str] = []

    if include_hashes:

        async def gather_hashes() -> Dict[str, List[str]]:
            async def hashes_for(name: str, ver: Version) -> Tuple[str, List[str]]:
                meta = await fetch_package_metadata(name, Options().index_url)
                releases = meta.get("releases", {}).get(str(ver), [])
                hashes: List[str] = []
                for f in releases:
                    dig = (f.get("digests") or {}).get("sha256")
                    if dig:
                        hashes.append(f"sha256:{dig}")
                return name, hashes

            tasks = [hashes_for(n, v) for n, v in plan.items()]
            results = await asyncio.gather(*tasks)
            return {n: h for n, h in results}

        hash_map = asyncio.run(gather_hashes())
    else:
        hash_map = {}

    for name, ver in sorted(plan.items()):
        base = f"{name}=={ver}"
        hashes = hash_map.get(name, [])
        if include_hashes and hashes:
            # Append all hashes per pip's --require-hashes format
            line = base + " ".join([f" --hash={h}" for h in hashes])
        else:
            line = base
        lines.append(line + "\n")

    path.write_text("".join(header + lines), encoding="utf-8")
