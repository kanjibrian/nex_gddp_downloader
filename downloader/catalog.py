"""
Catalogue container with composite-key lookup.
"""

from __future__ import annotations

from collections import defaultdict

from downloader.models import ClimateFile


class Catalog:
    """
    Holds a list of :class:`ClimateFile` objects and provides
    fast lookup by (model, scenario, variable, ensemble) tuple.
    """

    def __init__(self, files: list[ClimateFile]):

        self.files = files

        # Per-field indexes (for introspection / debugging)
        self.model_index: dict[str, list[ClimateFile]] = defaultdict(list)
        self.scenario_index: dict[str, list[ClimateFile]] = defaultdict(list)
        self.variable_index: dict[str, list[ClimateFile]] = defaultdict(list)
        self.ensemble_index: dict[str, list[ClimateFile]] = defaultdict(list)

        # Composite-key lookup
        self._lookup: dict[
            tuple[str, str, str, str], list[ClimateFile]
        ] = defaultdict(list)

        self._build_indexes()

    def __len__(self) -> int:
        return len(self.files)

    def _build_indexes(self) -> None:

        for file in self.files:

            self.model_index[file.model].append(file)
            self.scenario_index[file.scenario].append(file)
            self.variable_index[file.variable].append(file)
            self.ensemble_index[file.ensemble].append(file)

            key = (file.model, file.scenario, file.variable, file.ensemble)
            self._lookup[key].append(file)

    def get(
        self,
        model: str,
        scenario: str,
        variable: str,
        ensemble: str,
    ) -> list[ClimateFile]:
        """
        Return all files matching the given combination.
        """

        return self._lookup.get(
            (model, scenario, variable, ensemble), []
        )