from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from diskcache import Cache
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet

from .options import Options
from .errors import PackageNotFoundError, MetadataError

PYPI_JSON_URL = "https://pypi.org/pypi/{name}/json"


@dataclass
class VersionInfo:
    version: str
    first_upload_time: datetime
    file_requires_python: List[Optional[str]] = field(default_factory=list)
    yanked: bool = False

    @property
    def is_prerelease(self) -> bool:
        try:
            return Version(self.version).is_prerelease
        except InvalidVersion:
            return False

    @property
    def requires_python_display(self) -> str:
        uniq = []
        for rp in self.file_requires_python:
            if rp not in uniq:
                uniq.append(rp)
        parts = [p for p in uniq if p]
        return ", ".join(parts)


async def fetch_package_metadata(
    package_name: str,
    index_url: str,
    *,
    ttl_seconds: int = 86400,
    cache_dir: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    cache = Cache(cache_dir or ".cache/pipt-index")
    cache_key = (index_url, package_name.lower())
    try:
        cached = cache.get(cache_key)
    except Exception:
        cached = None
    if cached is not None:
        if verbose:
            print(f"[VERBOSE] [Cache HIT] {package_name}")
        return cached

    if verbose:
        print(f"[VERBOSE] [Cache MISS] {package_name}")

    url = index_url.format(name=package_name)
    backoff = 1.0
    last_exc: Optional[Exception] = None
    for attempt in range(5):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url, headers={"Accept": "application/json"})
            if r.status_code == 404:
                raise PackageNotFoundError(package_name, index_url)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, dict) or "releases" not in data:
                raise MetadataError(f"Malformed JSON for {package_name}")
            try:
                cache.set(cache_key, data, expire=ttl_seconds)
            except Exception:
                # cache failure should not crash
                pass
            return data
        except PackageNotFoundError:
            raise
        except (httpx.HTTPStatusError, httpx.TransportError, json.JSONDecodeError) as e:
            last_exc = e
            if attempt == 4:
                break
            time.sleep(backoff)
            backoff *= 2
    if last_exc:
        raise MetadataError(f"Failed to fetch metadata for {package_name}: {last_exc}")
    raise MetadataError(f"Failed to fetch metadata for {package_name}")


async def _collect_versions_from_metadata(metadata: Dict[str, Any]) -> List[VersionInfo]:
    releases: Dict[str, List[Dict[str, Any]]] = metadata.get("releases", {})
    results: List[VersionInfo] = []
    for ver, files in releases.items():
        if not files:
            continue
        first_time: Optional[datetime] = None
        file_requires: List[Optional[str]] = []
        any_yanked = False
        for f in files:
            ts = f.get("upload_time_iso_8601") or f.get("upload_time")
            dt: Optional[datetime] = None
            if ts:
                try:
                    if isinstance(ts, str) and ts.endswith("Z"):
                        ts = ts[:-1] + "+00:00"
                    dt = datetime.fromisoformat(ts) if isinstance(ts, str) else None
                except Exception:
                    dt = None
            if dt is None:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if first_time is None or dt < first_time:
                first_time = dt
            file_requires.append(f.get("requires_python"))
            if f.get("yanked"):
                any_yanked = True
        if first_time is None:
            continue
        results.append(VersionInfo(ver, first_time, file_requires, any_yanked))

    def ver_key(v: VersionInfo):
        try:
            return Version(v.version)
        except InvalidVersion:
            return Version("0")

    results.sort(key=ver_key)
    return results


async def get_vmax_for_package(
    metadata: Dict[str, Any], cutoff_dt: datetime, options: Options
) -> Optional[Version]:
    versions = await _collect_versions_from_metadata(metadata)

    candidates: List[VersionInfo] = []
    for vi in versions:
        if vi.first_upload_time > cutoff_dt:
            continue
        if vi.yanked and not options.allow_yanked:
            continue
        candidates.append(vi)

    if not candidates:
        return None

    if options.python_version:
        filtered: List[VersionInfo] = []
        for vi in candidates:
            ok = False
            if not vi.file_requires_python:
                ok = True
            else:
                for rp in vi.file_requires_python:
                    if not rp:
                        ok = True
                        break
                    try:
                        spec = SpecifierSet(rp)
                        if spec.contains(options.python_version, prereleases=True):
                            ok = True
                            break
                    except Exception:
                        ok = True
                        break
            if ok:
                filtered.append(vi)
        candidates = filtered

    if not candidates:
        return None

    stables = [vi for vi in candidates if not vi.is_prerelease]
    pool = candidates if (options.allow_pre or not stables) else stables

    if not pool:
        return None

    def ver_key(v: VersionInfo):
        try:
            return Version(v.version)
        except InvalidVersion:
            return Version("0")

    best = max(pool, key=ver_key)
    return Version(best.version)


async def get_nearest_for_package(
    metadata: Dict[str, Any], cutoff_dt: datetime, options: Options
) -> Optional[Version]:
    """Return the version whose first upload is nearest to cutoff (<= preferred over >)."""
    versions = await _collect_versions_from_metadata(metadata)
    before: List[VersionInfo] = []
    after: List[VersionInfo] = []
    for vi in versions:
        if vi.yanked and not options.allow_yanked:
            continue
        # Filter by Requires-Python if simulated
        if options.python_version:
            ok = False
            if not vi.file_requires_python:
                ok = True
            else:
                for rp in vi.file_requires_python:
                    if not rp:
                        ok = True
                        break
                    try:
                        spec = SpecifierSet(rp)
                        if spec.contains(options.python_version, prereleases=True):
                            ok = True
                            break
                    except Exception:
                        ok = True
                        break
            if not ok:
                continue
        if vi.first_upload_time <= cutoff_dt:
            if vi.is_prerelease and not options.allow_pre:
                continue
            before.append(vi)
        else:
            if vi.is_prerelease and not options.allow_pre:
                continue
            after.append(vi)
    if not before and not after:
        return None

    def distance(vi: VersionInfo) -> int:
        return abs(int((vi.first_upload_time - cutoff_dt).total_seconds()))

    # Prefer stable over pre when distances equal
    def score(vi: VersionInfo) -> tuple:
        return (distance(vi), vi.is_prerelease)

    best_before = min(before, key=score) if before else None
    best_after = min(after, key=score) if after else None

    chosen: Optional[VersionInfo]
    if best_before and best_after:
        if score(best_before) <= score(best_after):
            chosen = best_before
        else:
            chosen = best_after
    else:
        chosen = best_before or best_after

    if not chosen:
        return None
    try:
        return Version(chosen.version)
    except InvalidVersion:
        return None


# Existing PackageIndex kept for list command
class PackageIndex:
    def __init__(
        self,
        index_url: Optional[str] = None,
        cache_dir: Optional[str] = None,
        ttl_seconds: int = 86400,
    ):
        self.index_url = index_url or PYPI_JSON_URL
        self.cache = Cache(cache_dir or ".cache/pipt-index")
        self.ttl = ttl_seconds

    async def fetch_package_json(self, name: str) -> Dict[str, Any]:
        cache_key = (self.index_url, name.lower())
        try:
            cached = self.cache.get(cache_key)
        except Exception:
            cached = None
        if cached is not None:
            return cached
        url = self.index_url.format(name=name)
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers={"Accept": "application/json"})
            if r.status_code == 404:
                raise ValueError(f"Package not found: {name}")
            r.raise_for_status()
            data = r.json()
        try:
            self.cache.set(cache_key, data, expire=self.ttl)
        except Exception:
            pass
        return data

    async def get_versions(self, name: str) -> List[VersionInfo]:
        data = await self.fetch_package_json(name)
        return await _collect_versions_from_metadata(data)

    async def get_versions_before(
        self,
        name: str,
        cutoff: datetime,
        include_prereleases: bool = False,
        allow_yanked: bool = False,
        python_version: Optional[str] = None,
    ) -> List[VersionInfo]:
        versions = await self.get_versions(name)
        filtered: List[VersionInfo] = []
        for vi in versions:
            if vi.first_upload_time > cutoff:
                continue
            if vi.is_prerelease and not include_prereleases:
                continue
            if vi.yanked and not allow_yanked:
                continue
            if python_version:
                ok = False
                if not vi.file_requires_python:
                    ok = True
                else:
                    for rp in vi.file_requires_python:
                        if not rp:
                            ok = True
                            break
                        try:
                            spec = SpecifierSet(rp)
                            if spec.contains(python_version, prereleases=True):
                                ok = True
                                break
                        except Exception:
                            ok = True
                            break
                if not ok:
                    continue
            filtered.append(vi)
        return filtered

    async def vmax(
        self,
        name: str,
        cutoff: datetime,
        include_prereleases: bool = False,
        allow_yanked: bool = False,
        python_version: Optional[str] = None,
    ) -> Optional[Tuple[str, datetime]]:
        candidates = await self.get_versions_before(
            name,
            cutoff,
            include_prereleases=include_prereleases,
            allow_yanked=allow_yanked,
            python_version=python_version,
        )
        if not candidates:
            return None
        stables = [vi for vi in candidates if not vi.is_prerelease]
        pool = candidates if include_prereleases or not stables else stables

        def ver_key(v: VersionInfo):
            try:
                return Version(v.version)
            except InvalidVersion:
                return Version("0")

        best = max(pool, key=ver_key)
        return best.version, best.first_upload_time
