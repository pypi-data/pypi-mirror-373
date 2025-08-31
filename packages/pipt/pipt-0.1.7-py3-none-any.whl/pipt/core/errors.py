from __future__ import annotations


class PiptError(Exception):
    """Base exception for pipt."""


class PackageNotFoundError(PiptError):
    def __init__(self, package: str, index_url: str):
        super().__init__(f"Package not found on index: {package} ({index_url})")
        self.package = package
        self.index_url = index_url


class MetadataError(PiptError):
    pass


class CutoffViolationError(PiptError):
    def __init__(
        self,
        pkg: str,
        chosen: str,
        chosen_date: str | None,
        vmax: str | None,
        vmax_date: str | None,
    ):
        self.pkg = pkg
        self.chosen = chosen
        self.chosen_date = chosen_date
        self.vmax = vmax
        self.vmax_date = vmax_date
        super().__init__(self.__str__())

    def __str__(self) -> str:
        lines = [f"Conflict found for package {self.pkg}:"]
        if self.chosen:
            when = f" (released {self.chosen_date})" if self.chosen_date else ""
            lines.append(f"  - requested/selected {self.pkg}=={self.chosen}{when} is after cutoff.")
        if self.vmax:
            when = f" (released {self.vmax_date})" if self.vmax_date else ""
            lines.append(f"  - Latest allowed is {self.pkg}=={self.vmax}{when}.")
        return "\n".join(lines)


class ResolutionFailedError(PiptError):
    pass


class ResolutionConflictError(PiptError):
    def __init__(self, message: str, *, package: str | None = None):
        self.package = package
        super().__init__(message)


class ResolutionTimeoutError(PiptError):
    def __init__(self, iterations: int):
        super().__init__(f"Resolution did not converge after {iterations} iterations")


class PipSubprocessError(PiptError):
    def __init__(self, code: int, stderr: str):
        self.code = code
        self.stderr = stderr
        super().__init__(f"pip failed with exit code {code}: {stderr.strip()}")


class OldPipError(PiptError):
    def __init__(self, version: str):
        super().__init__(
            f"pipt requires pip >= 23.0 for --report. Detected pip {version}. Please run 'pip install --upgrade pip'."
        )
        self.version = version


class EnvironmentCompatibilityError(PiptError):
    """Raised when pip cannot find any compatible distributions for the environment."""

    def __init__(
        self,
        *,
        package: str | None,
        latest_allowed: str | None,
        python_version: str,
        platform_str: str,
        details: str,
        extra_hints: str | None = None,
    ):
        self.package = package
        self.latest_allowed = latest_allowed
        self.python_version = python_version
        self.platform_str = platform_str
        self.details = details
        # Compose a concise, helpful message
        pkg_line = f"for {package} (latest allowed {latest_allowed})" if package and latest_allowed else (f"for {package}" if package else "for requested packages")
        msg = (
            "Environment compatibility issue: pip could not find a compatible distribution "
            f"{pkg_line} on Python {python_version} / {platform_str}.\n"
            "This typically happens when pre-built wheels do not exist for such an old release on a modern setup.\n"
            "Suggestions:\n"
            "  1) Use an older Python (e.g., 3.9) that matches the cutoff era, or\n"
            "  2) Move the cutoff date forward to a release with modern wheels, or\n"
            "  3) Re-run with -v to see full pip output.\n"
        )
        if extra_hints:
            msg += f"\nHints:\n{extra_hints}\n"
        super().__init__(msg)


class SourceBuildError(PiptError):
    """Raised when pip attempts and fails to build from source for the target package."""

    def __init__(self, *, package: str | None, details: str):
        self.package = package
        self.details = details
        msg = (
            "Source build failed: pip attempted to build from source but encountered errors.\n"
            "Typical fixes: ensure required build tools are installed (e.g., compilers), or choose a cutoff date "
            "with available wheels, or use a Python/version combo with wheels available.\n"
        )
        super().__init__(msg)
