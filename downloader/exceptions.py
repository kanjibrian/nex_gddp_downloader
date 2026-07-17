"""
Custom exceptions for the NEX-GDDP-CMIP6 downloader.
"""


class DownloaderError(Exception):
    """Base exception for all downloader errors."""


class CatalogError(DownloaderError):
    """Raised when the NASA catalogue cannot be fetched or parsed."""


class ConfigError(DownloaderError):
    """Raised when the configuration file is invalid or missing."""


class DownloadError(DownloaderError):
    """Raised when a file download fails after all retries."""


class ChecksumError(DownloadError):
    """Raised when the MD5 checksum of a downloaded file does not match."""

    def __init__(self, filename: str, expected: str, actual: str):
        self.filename = filename
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"MD5 mismatch for {filename}: "
            f"expected {expected}, got {actual}"
        )
