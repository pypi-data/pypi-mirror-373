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
    cutoff = parse_cutoff(before)
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
    pre: bool, allow_yanked: bool, python_version: Optional[str], constraint: List[str]
) -> Options:
    return Options(
        allow_pre=pre,
        allow_yanked=allow_yanked,
        python_version=python_version,
        verbose=bool(VERBOSE),
        user_constraint_files=constraint.copy(),
    )


@app.command(help="Dry-run resolution and print the final plan")
def resolve(
    targets: List[str] = typer.Argument(..., help="One or more requirements, e.g. 'pandas<2.0'"),
    date: str = typer.Option(..., "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
    constraint: List[str] = typer.Option([], "-c", help="User constraint file(s) to layer"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
):
    cutoff = parse_cutoff(date)
    opts = _build_options(pre, allow_yanked, python_version, constraint)
    reqs = [Requirement(t) for t in targets]
    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        raise typer.Exit(code=2)

    if json_out:
        payload = {
            "cutoff": cutoff.isoformat(),
            "constraints": {k: str(v) for k, v in result.constraints.items()},
            "plan": {k: str(v) for k, v in result.plan_versions.items()},
        }
        console.print_json(data=payload)
        return

    table = Table(title=f"Resolved plan as of {cutoff.date()}")
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Release Date", style="magenta")
    for name, ver in sorted(result.plan_versions.items()):
        table.add_row(name, str(ver), "")
    console.print(table)

    ctable = Table(title="Constraints")
    ctable.add_column("Package")
    ctable.add_column("Specifier")
    for name, spec in sorted(result.constraints.items()):
        ctable.add_row(name, str(spec) or "")
    console.print(ctable)


@app.command(help="Resolve and install respecting the cutoff date")
def install(
    targets: List[str] = typer.Argument(..., help="One or more requirements or -r file.txt"),
    date: str = typer.Option(..., "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
    pre: bool = typer.Option(False, "--pre", help="Include pre-releases when necessary"),
    allow_yanked: bool = typer.Option(False, "--allow-yanked", help="Include yanked versions"),
    python_version: Optional[str] = typer.Option(
        None, "--python-version", help="Simulate Python version X.Y"
    ),
    constraint: List[str] = typer.Option([], "-c", help="User constraint file(s) to layer"),
):
    cutoff = parse_cutoff(date)
    opts = _build_options(pre, allow_yanked, python_version, constraint)
    reqs = [Requirement(t) for t in targets]
    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        raise typer.Exit(code=2)

    with tempfile.TemporaryDirectory() as td:
        cfile = Path(td) / "constraints.txt"
        from pipt.core.resolver import _write_constraints_file  # reuse helper

        _write_constraints_file(cfile, result.constraints)
        console.print("Running pip install...")
        try:
            run_final_pip_install([str(r) for r in reqs], cfile, opts, latest_constraints=result.constraints)
        except PiptError as e:
            # Present a concise, actionable message
            console.print(Panel.fit(str(e), title="pip install failed", border_style="red"))
            console.print("Tip: run again with -v to see the full pip command and output.")
            raise typer.Exit(code=1)


@app.command(help="Resolve and write a pip-compatible lockfile")
def lock(
    targets: List[str] = typer.Argument(..., help="One or more requirements"),
    date: str = typer.Option(..., "--date", help="Cutoff date (YYYY-MM-DD or ISO8601)"),
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
    cutoff = parse_cutoff(date)
    opts = _build_options(pre, allow_yanked, python_version, constraint)
    reqs = [Requirement(t) for t in targets]
    try:
        with Status("Resolving with pip..."):
            result = asyncio.run(resolve_dependency_plan(reqs, cutoff, opts))
    except PiptError as e:
        console.print(Panel.fit(str(e), title="Resolution failed", border_style="red"))
        raise typer.Exit(code=2)

    write_lockfile(output, result.plan_versions, cutoff, include_hashes=include_hashes)
    console.print(f"[green]Lockfile written to {output}")


def main(argv: Optional[List[str]] = None) -> int:
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
