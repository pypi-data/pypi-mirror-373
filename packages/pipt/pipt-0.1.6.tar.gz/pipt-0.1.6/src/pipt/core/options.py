from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List
import re


@dataclass
class Options:
    allow_pre: bool = False
    allow_yanked: bool = False
    python_version: Optional[str] = None
    index_url: str = "https://pypi.org/pypi/{name}/json"
    cache_ttl_seconds: int = 86400
    cache_dir: Optional[str] = None
    max_iterations: int = 15
    verbose: bool = False
    user_constraint_files: List[str] = field(default_factory=list)
    # When true, add --prefer-binary/--only-binary=:all: to pip calls (historical mode).
    # When false (no date supplied), behave like pip and do not force binary wheels.
    binary_only: bool = True
    # When true, pass --no-deps to pip install invocations.
    no_deps: bool = False
    # Strategy for interpreting the cutoff date. "before" enforces historical <= cutoff. "nearest" is experimental.
    date_mode: str = "before"

    def __post_init__(self) -> None:
        if self.python_version is not None:
            if not re.match(r"^\d+\.\d+$", self.python_version):
                raise ValueError(
                    f"Invalid python_version '{self.python_version}'. Expected format 'X.Y' (e.g., '3.9')."
                )
        if not isinstance(self.allow_pre, bool) or not isinstance(self.allow_yanked, bool):
            raise TypeError("allow_pre and allow_yanked must be bools")
        if not isinstance(self.verbose, bool):
            raise TypeError("verbose must be a bool")
        if not isinstance(self.binary_only, bool):
            raise TypeError("binary_only must be a bool")
        if not isinstance(self.no_deps, bool):
            raise TypeError("no_deps must be a bool")
        if not isinstance(self.max_iterations, int) or self.max_iterations <= 0:
            raise ValueError("max_iterations must be a positive integer")
        if not isinstance(self.cache_ttl_seconds, int) or self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be a non-negative integer")
        # Validate constraint files list
        if not isinstance(self.user_constraint_files, list):
            raise TypeError("user_constraint_files must be a list of strings")
        for c in self.user_constraint_files:
            if not isinstance(c, str):
                raise TypeError("user_constraint_files must contain only strings")
        # Validate date_mode
        if self.date_mode not in ("before", "nearest"):
            raise ValueError("date_mode must be either 'before' or 'nearest'")
