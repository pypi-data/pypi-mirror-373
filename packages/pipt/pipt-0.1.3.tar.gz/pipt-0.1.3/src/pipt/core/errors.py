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
