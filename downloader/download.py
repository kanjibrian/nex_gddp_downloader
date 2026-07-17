"""
Download manager for NASA NEX-GDDP-CMIP6 files.

Supports parallel downloads, resume, MD5 verification,
progress bars, and automatic retry.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from downloader.checksum import verify_md5
from downloader.exceptions import DownloadError
from downloader.logger import get_logger
from downloader.models import ClimateFile
from downloader.progress import create_file_progress, create_overall_progress
from downloader.retry import retry_on_failure
from downloader.utils import format_size


class Downloader:
    """
    High-performance parallel downloader with resume, checksum
    verification, and progress tracking.
    """

    def __init__(self, config: Config):

        self.config = config
        self.log = get_logger()
        self.session = self._create_session()

        # Thread-safe counters
        self._lock = threading.Lock()
        self._downloaded = 0
        self._skipped = 0
        self._failed = 0

    # ------------------------------------------------------------------
    # HTTP Session
    # ------------------------------------------------------------------

    def _create_session(self) -> requests.Session:
        """
        Create a shared HTTP session with connection pooling
        and transport-level retries.
        """

        retry = Retry(
            total=self.config.retry.attempts,
            connect=self.config.retry.attempts,
            read=self.config.retry.attempts,
            backoff_factor=self.config.retry.delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=self.config.workers,
            pool_maxsize=self.config.workers,
        )

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        session.headers.update({
            "User-Agent": "NEX-GDDP-CMIP6-Downloader/1.0",
        })

        return session

    # ------------------------------------------------------------------
    # Download all
    # ------------------------------------------------------------------

    def download_all(self, files: list[ClimateFile]) -> None:
        """
        Download all files using a thread pool.
        """

        total = len(files)
        self.log.info("Preparing to download %s files.", f"{total:,}")

        overall = create_overall_progress(total)

        with ThreadPoolExecutor(max_workers=self.config.workers) as pool:

            futures = {
                pool.submit(self._safe_download, file): file
                for file in files
            }

            for future in as_completed(futures):
                future.result()  # surfaces exceptions if any
                overall.update(1)

        overall.close()

        self.log.info(
            "Finished: %s downloaded, %s skipped, %s failed.",
            f"{self._downloaded:,}",
            f"{self._skipped:,}",
            f"{self._failed:,}",
        )

    # ------------------------------------------------------------------
    # Safe wrapper (retry + error handling)
    # ------------------------------------------------------------------

    def _safe_download(self, file: ClimateFile) -> None:
        """
        Download a single file with retry and error handling.
        """

        try:
            retry_on_failure(
                func=lambda: self._download_file(file),
                attempts=self.config.retry.attempts,
                delay=self.config.retry.delay,
                logger=self.log,
                description=file.filename,
            )

        except DownloadError as exc:
            self.log.error("FAILED %s — %s", file.filename, exc)
            with self._lock:
                self._failed += 1

    # ------------------------------------------------------------------
    # Single file
    # ------------------------------------------------------------------

    def _download_file(self, file: ClimateFile) -> None:
        """
        Download one file with optional resume and checksum verification.
        """

        destination = file.local_path(self.config.download_directory)

        destination.parent.mkdir(parents=True, exist_ok=True)

        # --- Skip existing ----------------------------------------

        if self.config.skip_existing and destination.exists():

            # If verify_md5 is on, confirm the existing file is valid
            if self.config.verify_md5 and file.md5:
                try:
                    verify_md5(destination, file.md5)
                except Exception:
                    self.log.info(
                        "[RE-DOWNLOAD] %s (checksum mismatch)",
                        destination.name,
                    )
                    # Fall through to re-download
                else:
                    self.log.debug("[SKIP] %s (verified)", destination.name)
                    with self._lock:
                        self._skipped += 1
                    return
            else:
                self.log.debug("[SKIP] %s", destination.name)
                with self._lock:
                    self._skipped += 1
                return

        # --- Resume support ----------------------------------------

        initial_bytes = 0
        headers: dict[str, str] = {}

        if self.config.resume_downloads and destination.exists():
            initial_bytes = destination.stat().st_size
            headers["Range"] = f"bytes={initial_bytes}-"
            self.log.debug(
                "[RESUME] %s from %s",
                destination.name,
                format_size(initial_bytes),
            )

        # --- Stream download ---------------------------------------

        self.log.info("[DOWNLOAD] %s", destination.name)

        self._download_stream(
            url=file.url,
            destination=destination,
            initial_bytes=initial_bytes,
            extra_headers=headers,
        )

        # --- MD5 verification --------------------------------------

        if self.config.verify_md5 and file.md5:
            verify_md5(destination, file.md5)
            self.log.debug("[VERIFIED] %s", destination.name)

        with self._lock:
            self._downloaded += 1

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def _download_stream(
        self,
        url: str,
        destination: Path,
        initial_bytes: int = 0,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """
        Download a file using chunked streaming with a progress bar.
        """

        response = self.session.get(
            url,
            stream=True,
            timeout=self.config.timeout,
            headers=extra_headers or {},
        )

        response.raise_for_status()

        # Determine total size from Content-Length (if available)
        content_length = response.headers.get("Content-Length")
        total_size = (
            int(content_length) + initial_bytes
            if content_length
            else None
        )

        chunk_size = self.config.chunk_size_mb * 1024 * 1024

        # Choose write mode: append for resume, write for fresh download
        mode = "ab" if initial_bytes > 0 else "wb"

        progress = create_file_progress(
            filename=destination.name,
            total_size=total_size,
            initial=initial_bytes,
        )

        try:
            with open(destination, mode) as output:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        output.write(chunk)
                        progress.update(len(chunk))
        finally:
            progress.close()
