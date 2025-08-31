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
)
from .index import fetch_package_metadata, get_vmax_for_package
from .options import Options


@dataclass
class ResolutionResult:
    constraints: Dict[str, SpecifierSet]
    plan_versions: Dict[str, Version]


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
    args += [
        "--prefer-binary",
        "--only-binary",
        ":all:",
        "--disable-pip-version-check",
        "--no-input",
    ]
    return args


def _run_pip_dry_run(
    target_args: List[str], constraints_file: Path, report_file: Path, options: Options
) -> Tuple[int, str, str]:
    cmd = _pip_base_args(report_file, constraints_file, options) + target_args
    _verbose_print(options, f"Running pip: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
    targets: List[Requirement], cutoff_dt: datetime, options: Options
) -> ResolutionResult:
    _pip_version_check()

    constraints: Dict[str, SpecifierSet] = {}

    async def seed_for_target(req: Requirement) -> None:
        meta = await fetch_package_metadata(
            req.name,
            options.index_url,
            ttl_seconds=options.cache_ttl_seconds,
            cache_dir=options.cache_dir,
            verbose=options.verbose,
        )
        vmax = await get_vmax_for_package(meta, cutoff_dt, options)
        if vmax is None:
            raise ResolutionConflictError(
                f"No versions of {req.name} are available on or before cutoff {cutoff_dt.isoformat()} for the given options",
                package=req.name,
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
                # If looks like dependency conflict, raise ResolutionConflictError, else PipSubprocessError
                msg = (err or out).strip()
                if "ResolutionImpossible" in msg or "conflicting dependencies" in msg:
                    raise ResolutionConflictError(msg)
                raise PipSubprocessError(code, msg)
            last_plan = _parse_plan(rfile)
            if not last_plan:
                raise MetadataError(
                    "Empty plan from pip report; unexpected report schema or pip version"
                )

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


def run_final_pip_install(target_args: List[str], constraints_file: Path, options: Options) -> int:
    cmd = _pip_base_args(None, constraints_file, options) + target_args
    # Stream output live
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.stdout and proc.stderr
    for line in proc.stdout:
        print(line, end="")
    err_out = proc.stderr.read()
    code = proc.wait()
    if code != 0:
        raise PipSubprocessError(code, err_out)
    return code


def write_lockfile(
    path: Path, plan: Dict[str, Version], cutoff: datetime, include_hashes: bool = False
) -> None:
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
