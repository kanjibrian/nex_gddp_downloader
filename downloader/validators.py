"""
Validation utilities.
"""
from __future__ import annotations
from downloader.filters import unique_values
from downloader.models import ClimateFile

def validate_selection(files: list[ClimateFile]) -> None:
    """
    Ensure the filters selected at least one file.
    """
    if files:
        return

    raise ValueError("No files matched the selected filters.")


def print_summary(files: list[ClimateFile]) -> None:
    """
    Print a summary of the filtered catalogue.
    """
    print("\nSelection Summary")
    print("-" * 60)

    print(f"Files: {len(files):,}")
    print(f"Models: {len(unique_values(files, 'model'))}")
    print(f"Variables: {len(unique_values(files, 'variable'))}")
    print(f"Scenarios: {len(unique_values(files, 'scenario'))}")
    print(f"Ensembles: {len(unique_values(files, 'ensemble'))}")

    years = sorted({file.year for file in files})

    if years:
        print(f"Years: {years[0]} - {years[-1]}")