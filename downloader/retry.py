"""
Application-level retry logic with exponential backoff.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

import requests

from downloader.exceptions import ChecksumError, DownloadError

T = TypeVar("T")


def retry_on_failure(
    func: Callable[..., T],
    attempts: int,
    delay: float,
    logger: logging.Logger,
    description: str = "",
) -> T:
    """
    Call *func* up to *attempts* times, retrying on transient errors.

    Parameters
    ----------
    func : callable
        Zero-argument callable to execute.
    attempts : int
        Maximum number of tries.
    delay : float
        Base delay in seconds (doubles each retry).
    logger : logging.Logger
        Logger for retry messages.
    description : str
        Human-readable label for log messages.

    Raises
    ------
    DownloadError
        If all attempts fail.
    """

    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return func()

        except (requests.RequestException, ChecksumError, OSError) as exc:
            last_error = exc

            if attempt == attempts:
                break

            wait = delay * (2 ** (attempt - 1))

            logger.warning(
                "Attempt %d/%d failed for %s: %s — "
                "retrying in %.0fs",
                attempt,
                attempts,
                description,
                exc,
                wait,
            )

            time.sleep(wait)

    raise DownloadError(
        f"Failed after {attempts} attempts: {description}"
    ) from last_error
