__all__ = [
    "NuGetError",
    "NuGetTimeoutError",
    "ServiceTimeoutError",
    "PackageQueryTimeoutError",
]


class NuGetError(Exception):
    """Base exception class for NuGet exceptions."""


class NuGetTimeoutError(NuGetError):
    """Exception raised when NuGet query timed out."""


class ServiceTimeoutError(NuGetTimeoutError):
    """Exception raised when NuGet service query timed out."""


class PackageQueryTimeoutError(NuGetTimeoutError):
    """Exception raised when NuGet package query timed out."""
