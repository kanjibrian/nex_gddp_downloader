"""
MD5 checksum utilities for verifying downloaded files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from downloader.exceptions import ChecksumError


def compute_md5(filepath: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """
    Compute the MD5 hash of a file by reading it in chunks.

    Parameters
    ----------
    filepath : Path
        Path to the file.
    chunk_size : int
        Read buffer size in bytes (default 8 MB).

    Returns
    -------
    str
        The hex-encoded MD5 digest.
    """

    md5 = hashlib.md5()

    with open(filepath, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def verify_md5(filepath: Path, expected_md5: str) -> None:
    """
    Verify that a file's MD5 matches the expected value.

    Raises
    ------
    ChecksumError
        If the computed hash does not match ``expected_md5``.
    """

    if not expected_md5:
        return

    actual = compute_md5(filepath)

    if actual != expected_md5.lower().strip():
        raise ChecksumError(
            filename=filepath.name,
            expected=expected_md5,
            actual=actual,
        )
