from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List


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
