<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/OsamaS99/pipt@main/assets/logo.png" alt="pipt Logo" width="640"/>
  <p align="center">
    The Python Package Time Machine
  </p>
  <p align="center">
    <strong>Install dependencies as they existed on any given date.</strong>
  </p>
  <p align="center">
    <a href="https://github.com/OsamaS99/pipt/actions"><img alt="CI" src="https://github.com/OsamaS99/pipt/actions/workflows/ci.yml/badge.svg"></a>
    <a href="https://pypi.org/project/pipt"><img alt="PyPI" src="https://img.shields.io/pypi/v/pipt"></a>
  </p>
</div>

---

`pipt` is a command-line tool that acts as a time machine for your Python environment. It lets you install packages and their dependencies exactly as they were on a specific date, making past environments reproducible without hunting down historical versions by hand.

It's not a new package manager. It wraps `pip`, using its resolver to do the heavy lifting while `pipt` finds the right time-appropriate releases for you.

## Quickstart

- See what you’d get as of a date:

```bash
pipt resolve "pandas<2.0" --date 2023-01-01
```

- Install with a cutoff date:

```bash
pipt install "pandas<2.0" --date 2023-01-01
```

- Create a lockfile you can install with pip later:

```bash
pipt lock django --date 2021-03-15 > requirements.lock
pip install -r requirements.lock
```

## Key Features

- Reproducible builds tied to a specific date
- Date-based resolution: choose the latest versions available on or before the cutoff
- Lockfile generation compatible with `pip`
- Works with your existing workflows (constraints, pre-releases, yanked handling)
- Polished CLI powered by `rich`

## Installation

```bash
pip install pipt
```

Or with pipx (recommended for global CLI tools):

```bash
pipx install pipt
```

## How It Works

`pipt` iteratively refines version constraints. It starts from your requested requirements, selects the latest releases that existed on the cutoff date, and runs `pip`'s resolver in a dry run. If transitive dependencies are too new, `pipt` tightens constraints and repeats until a historically accurate plan is found.

## Usage

### Install a package as of a date

```bash
# Install pandas as it was on New Year's Day 2023
pipt install "pandas<2.0" --date 2023-01-01
```

### Resolve (dry run) without installing

```bash
# See the dependency plan for flask on June 1st, 2022
pipt resolve flask --date 2022-06-01
```

Add JSON output if you want to script around the result:

```bash
pipt resolve flask --date 2022-06-01 --json
```

### Create a pip-compatible lockfile

```bash
# Lock Django and its dependencies to their state on March 15th, 2021
pipt lock django --date 2021-03-15 > requirements.lock

# Include hashes for extra integrity
pipt lock django --date 2021-03-15 --include-hashes > requirements.lock
```

### List available versions before a date

```bash
# List all versions of requests published before 2020
pipt list requests --before 2020-01-01
```

### Handy options

- `--pre`: allow pre-releases when needed
- `--allow-yanked`: include yanked releases
- `--python-version X.Y`: resolve as if running on Python X.Y (respects Requires-Python)
- `-c constraints.txt`: layer your own constraints

## Compatibility

- Python: 3.9–3.12
- Platforms: Linux, macOS, Windows

## Contributing

Contributions are welcome! See the [Contributing Guide](CONTRIBUTING.md).

## License

`pipt` is licensed under the [MIT License](LICENSE).
