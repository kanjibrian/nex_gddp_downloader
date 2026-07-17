"""
Filtering utilities for ClimateFile objects.
"""
from __future__ import annotations
from collections.abc import Iterable
from config import Config
from downloader.catalog import Catalog
from downloader.models import ClimateFile

def filter_catalog(catalog: Catalog, config: Config) -> list[ClimateFile]:

    start_year = config.years.start
    end_year = config.years.end

    filtered: list[ClimateFile] = []

    for model in config.models:
        for scenario in config.scenarios:
            for variable in config.variables:
                for ensemble in config.ensembles:

                    filtered.extend(
                        f
                        for f in catalog.get(
                            model,
                            scenario,
                            variable,
                            ensemble,
                        )
                        if start_year <= f.year <= end_year
                    )

    return filtered


def unique_values(
    files: Iterable[ClimateFile],
    attribute: str,
) -> list[str]:
    """
    Return sorted unique values for an attribute.

    Example
    -------
    unique_values(files, "model")
    """
    return sorted(
        {
            getattr(file, attribute)
            for file in files
        }
    )