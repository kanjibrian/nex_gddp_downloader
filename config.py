from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(slots=True)
class RetryConfig:
    attempts: int
    delay: int


@dataclass(slots=True)
class YearRange:
    start: int
    end: int


@dataclass(slots=True)
class Config:

    catalog_csv: str

    download_directory: Path
    log_directory: Path

    workers: int
    timeout: int
    chunk_size_mb: int

    verify_md5: bool
    resume_downloads: bool
    skip_existing: bool
    preserve_structure: bool

    retry: RetryConfig

    variables: list[str]
    models: list[str]
    scenarios: list[str]
    ensembles: list[str]

    years: YearRange


def load_config(path: str = "settings.yml") -> Config:

    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    return Config(

        catalog_csv=cfg["catalog_csv"],

        download_directory=Path(cfg["download_directory"]),
        log_directory=Path(cfg["log_directory"]),

        workers=cfg["workers"],
        timeout=cfg["timeout"],
        chunk_size_mb=cfg["chunk_size_mb"],

        verify_md5=cfg["verify_md5"],
        resume_downloads=cfg["resume_downloads"],
        skip_existing=cfg["skip_existing"],
        preserve_structure=cfg["preserve_structure"],

        retry=RetryConfig(

            attempts=cfg["retry_attempts"],
            delay=cfg["retry_delay"]

        ),

        variables=cfg["variables"],
        models=cfg["models"],
        scenarios=cfg["scenarios"],
        ensembles=cfg["ensembles"],

        years=YearRange(

            start=cfg["years"]["start"],
            end=cfg["years"]["end"]

        )
    )