from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional, List
import tempfile

import typer
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from ..core.index import PackageIndex
from ..core.timeutil import parse_cutoff
from ..core.options import Options
from ..core.resolver import resolve_dependency_plan, run_final_pip_install, write_lockfile
from ..core.errors import PiptError
from packaging.requirements import Requirement

app = typer.Typer(add_completion=False)
console = Console()
VERBOSE: bool = False


@app.callback()
def main_opts(verbose: bool = typer.Option(False, "-v", "--verbose", help="Show verbose logs")):
    global VERBOSE
    typer.get_app_dir("pipt")  # warm app dir
    VERBOSE = verbose


@app.command(name="list", help="List package versions up to a date")
def list_cmd(
    package: str = typer.Argument(..., help="Package name"),
    before: str = typer.Option(
        ..., "--before", help="Date (YYYY-MM-DD or ISO8601, naive treated as UTC end-of-day)"
    ),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y for Requires-Python filtering"
    ),
):
    try:
        cutoff = parse_cutoff(before)
    except Exception as e:
        console.print(Panel.fit(f"Invalid --before value: {before}\n{e}", title="Invalid option", border_style="red"))
        raise typer.Exit(code=2)
    idx = PackageIndex()
    with Status("Fetching metadata..."):
        versions = asyncio.run(
            idx.get_versions_before(
                package,
                cutoff,
                include_prereleases=pre,
                allow_yanked=allow_yanked,
                python_version=python_version,
            )
        )
    if not versions:
        console.print(f"[yellow]No versions of {package} before {cutoff.isoformat()} found.")
        raise typer.Exit(code=1)

    table = Table(title=f"{package} versions on or before {cutoff.date()}")
    table.add_column("Version", style="cyan")
    table.add_column("Released (UTC)", style="green")
    table.add_column("Requires-Python", style="magenta")
    table.add_column("Yanked", style="red")

    for vi in versions:
        table.add_row(
            vi.version,
            vi.first_upload_time.strftime("%Y-%m-%d %H:%M:%S%z"),
            vi.requires_python_display,
            "yes" if vi.yanked else "",
        )
    console.print(table)


def _build_options(
    pre: bool, allow_yanked: bool, python_version: Optional[str], constraint: List[str], *, binary_only: bool, date_mode: str = "before"
) -> Options:
    return Options(
        allow_pre=pre,
        allow_yanked=allow_yanked,
        python_version=python_version,
        verbose=bool(VERBOSE),
        user_constraint_files=constraint.copy(),
        binary_only=binary_only,
        date_mode=date_mode,
    )


@app.command(help="Dry-run resolution and print the final plan")
def resolve(
    targets: List[str] = typer.Argument(..., help="One or more requirements, e.g. 'pandas<2.0'"),
    date: Optional[str] = typer.Option(None, "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    date_mode: str = typer.Option("before", "--date-mode", help="Strategy for cutoff: 'before' or 'nearest'"),
    allow_source: bool = typer.Option(False, "--allow-source", help="Allow building from source (disables binary-only in historical mode)"),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
    constraint: List[str] = typer.Option([], "-c", help="User constraint file(s) to layer"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
):
    cutoff = None
    if date:
        try:
            cutoff = parse_cutoff(date)
        except Exception as e:
            console.print(Panel.fit(f"Invalid --date value: {date}\n{e}", title="Invalid option", border_style="red"))
            raise typer.Exit(code=2)
    # In historical mode (date provided), default to binary-only unless user allows source
    binary_only = bool(date) and not allow_source
    opts = _build_options(pre, allow_yanked, python_version, constraint, binary_only=binary_only, date_mode=date_mode)
    reqs = [Requirement(t) for t in targets]
    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        console.print("Tip: -v is a global option. Use: pipt -v resolve ...")
        raise typer.Exit(code=2)

    if json_out:
        payload = {
            "cutoff": cutoff.isoformat() if cutoff else None,
            "constraints": {k: str(v) for k, v in result.constraints.items()},
            "plan": {k: str(v) for k, v in result.plan_versions.items()},
        }
        console.print_json(data=payload)
        return

    if not result.plan_versions:
        console.print("[green]Nothing to do. All requirements are already satisfied for the selected mode.")
        return

    title = f"Resolved plan as of {cutoff.date()}" if cutoff else "Resolved plan (no cutoff)"
    table = Table(title=title)
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Release Date", style="magenta")
    for name, ver in sorted(result.plan_versions.items()):
        table.add_row(name, str(ver), "")
    console.print(table)

    if result.constraints:
        ctable = Table(title="Constraints")
        ctable.add_column("Package")
        ctable.add_column("Specifier")
        for name, spec in sorted(result.constraints.items()):
            ctable.add_row(name, str(spec) or "")
        console.print(ctable)


@app.command(help="Resolve and install respecting the cutoff date")
def install(
    targets: List[str] = typer.Argument(..., help="One or more requirements or -r file.txt"),
    date: Optional[str] = typer.Option(None, "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    date_mode: str = typer.Option("before", "--date-mode", help="Strategy for cutoff: 'before' or 'nearest'"),
    allow_source: bool = typer.Option(False, "--allow-source", help="Allow building from source (disables binary-only in historical mode)"),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
    constraint: List[str] = typer.Option([], "-c", help="User constraint file(s) to layer"),
    no_deps: bool = typer.Option(False, "--no-deps", help="Install without dependencies (advanced)"),
):
    cutoff = None
    if date:
        try:
            cutoff = parse_cutoff(date)
        except Exception as e:
            console.print(Panel.fit(f"Invalid --date value: {date}\n{e}", title="Invalid option", border_style="red"))
            raise typer.Exit(code=2)
    # In historical mode (date provided), default to binary-only unless user allows source
    binary_only = bool(date) and not allow_source
    opts = Options(
        allow_pre=pre,
        allow_yanked=allow_yanked,
        python_version=python_version,
        verbose=bool(VERBOSE),
        user_constraint_files=constraint.copy(),
        binary_only=binary_only,
        no_deps=no_deps,
        date_mode=date_mode,
    )
    reqs = [Requirement(t) for t in targets]

    if cutoff is None:
        console.print("Running pip install (no cutoff)...")
        try:
            run_final_pip_install([str(r) for r in reqs], None, opts, latest_constraints=None)
        except PiptError as e:
            console.print(Panel.fit(str(e), title="pip install failed", border_style="red"))
            console.print("Tip: run again with -v (global) to see the full pip command and output.")
            raise typer.Exit(code=1)
        return

    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        console.print("Tip: -v is a global option. Use: pipt -v install ...")
        raise typer.Exit(code=2)

    with tempfile.TemporaryDirectory() as td:
        cfile = Path(td) / "constraints.txt"
        from pipt.core.resolver import _write_constraints_file  # reuse helper

        _write_constraints_file(cfile, result.constraints)
        console.print("Running pip install...")
        try:
            run_final_pip_install([str(r) for r in reqs], cfile, opts, latest_constraints=result.constraints)
        except PiptError as e:
            console.print(Panel.fit(str(e), title="pip install failed", border_style="red"))
            console.print("Tip: -v is a global option. Use: pipt -v install ...")
            raise typer.Exit(code=1)
        else:
            console.print("[green]Installation completed.")


@app.command(help="Resolve and write a pip-compatible lockfile")
def lock(
    targets: List[str] = typer.Argument(..., help="One or more requirements"),
    date: Optional[str] = typer.Option(None, "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    date_mode: str = typer.Option("before", "--date-mode", help="Strategy for cutoff: 'before' or 'nearest'"),
    allow_source: bool = typer.Option(False, "--allow-source", help="Allow building from source (disables binary-only in historical mode)"),
    output: Path = typer.Option(
        Path("lockfile.txt"), "-o", "--output", help="Output lockfile path"
    ),
    include_hashes: bool = typer.Option(
        False, "--include-hashes", help="Include hashes (experimental)"
    ),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
    constraint: List[str] = typer.Option([], "-c", help="User constraint file(s) to layer"),
):
    cutoff = None
    if date:
        try:
            cutoff = parse_cutoff(date)
        except Exception as e:
            console.print(Panel.fit(f"Invalid --date value: {date}\n{e}", title="Invalid option", border_style="red"))
            raise typer.Exit(code=2)
    # In historical mode (date provided), default to binary-only unless user allows source
    binary_only = bool(date) and not allow_source
    opts = _build_options(pre, allow_yanked, python_version, constraint, binary_only=binary_only, date_mode=date_mode)
    reqs = [Requirement(t) for t in targets]
    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        raise typer.Exit(code=2)

    write_lockfile(output, result.plan_versions, cutoff, include_hashes=include_hashes)
    console.print(f"[green]Lockfile written to {output}")


@app.command(help="Diagnose environment and cutoff without installing")
def diagnose(
    target: str = typer.Argument(..., help="A single requirement (e.g. 'torch==1.13.1' or 'numpy')"),
    date: Optional[str] = typer.Option(None, "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
):
    from ..core.index import fetch_package_metadata
    from ..core.resolver import _environment_summary, _requires_python_for_version, _wheel_python_tags_for_version
    from packaging.version import Version

    cutoff = None
    if date:
        try:
            cutoff = parse_cutoff(date)
        except Exception as e:
            console.print(Panel.fit(f"Invalid --date value: {date}\n{e}", title="Invalid option", border_style="red"))
            raise typer.Exit(code=2)
    req = Requirement(target)
    opts = Options(allow_pre=pre, allow_yanked=allow_yanked, python_version=python_version, verbose=bool(VERBOSE), binary_only=bool(date))
    pyv, plat = _environment_summary(opts)
    console.print(f"Environment: Python {pyv} / {plat}")
    meta = asyncio.run(fetch_package_metadata(req.name, Options().index_url))
    console.print(f"Package: {req.name}")
    if cutoff:
        from ..core.index import get_vmax_for_package
        vmax = asyncio.run(get_vmax_for_package(meta, cutoff, opts))
        console.print(f"Latest allowed by cutoff: {vmax if vmax else 'None'}")
        if vmax:
            specs = _requires_python_for_version(meta, Version(str(vmax)))
            if specs:
                console.print(f"Requires-Python for {req.name}=={vmax}: {', '.join(specs)}")
            pys = _wheel_python_tags_for_version(meta, Version(str(vmax)))
            if pys:
                console.print(f"Wheel Python minors for {req.name}=={vmax}: {', '.join(pys)}")
    else:
        console.print("No cutoff provided; behaves like pip.")


def main(argv: Optional[List[str]] = None) -> int:
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
