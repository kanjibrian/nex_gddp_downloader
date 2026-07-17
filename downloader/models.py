"""
Data models used throughout the downloader.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ClimateFile:
    """
    Represents a single downloadable file from the NASA
    NEX-GDDP-CMIP6 catalogue.
    """

    model: str
    scenario: str
    ensemble: str
    variable: str
    year: int
    url: str
    md5: str
    relative_path: Path
    size: int | None = field(default=None)

    @property
    def filename(self) -> str:
        return self.relative_path.name


    def local_path(self, root: Path) -> Path:
        """
        Returns where the file should be stored locally.
        """
        return root / self.relative_path


    def __str__(self) -> str:

        return (
            f"{self.model} | "
            f"{self.scenario} | "
            f"{self.variable} | "
            f"{self.year}"
        )