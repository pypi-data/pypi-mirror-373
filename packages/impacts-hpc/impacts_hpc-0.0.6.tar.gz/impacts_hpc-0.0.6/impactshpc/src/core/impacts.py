# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from functools import reduce
from typing import Any, List

from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.ontology import Ontology


class Impacts:
    def __init__(self, impact_per_criteria: dict[str, ReplicableValue]):
        assert len(impact_per_criteria.keys()) > 0, "impact_per_criteria should not be empty"
        self.name = None
        self._impact_per_criteria = impact_per_criteria

    @staticmethod
    def from_config(name: str, configEntry: dict[str, dict[str, Any]]) -> "Impacts":
        """
        Creates an Impact object from a configuration entry.
        The configEntry should be a dictionary where keys are criteria names
        and values are dictionaries with 'value' and 'source' keys.
        """
        impact_per_criteria: dict[str, ReplicableValue] = {
            criteria: SourcedValue.from_config(name=f"{name}_{criteria}", configEntry=sourcedValue)
            for criteria, sourcedValue in configEntry.items()
        }
        return Impacts(impact_per_criteria)

    def make_intermediate_result(self, name: str, explainations: str | None = None, ontology: Ontology | None = None):
        """Call :meth:`impacthpc.src.core.ReplicableValue.make_intermediate_result` on the :class:`impacthpc.src.core.ReplicableValue` of this Impcats."""
        self.name = name

        for criteria in self._impact_per_criteria.keys():
            self._impact_per_criteria[criteria].make_intermediate_result(f"{name}_{criteria}", explainations, ontology)

    def __add__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        if isinstance(other, Impacts):
            # if a criteria is present in both impacts, we sum the values
            # if it is only present in one, we keep the value from that impact
            combined_impact: dict[str, ReplicableValue] = {}
            for criteria in set(self._impact_per_criteria) | set(other._impact_per_criteria):
                if criteria in self._impact_per_criteria and criteria in other._impact_per_criteria:
                    combined_value = self._impact_per_criteria[criteria] + other._impact_per_criteria[criteria]
                elif criteria in self._impact_per_criteria:
                    combined_value = self._impact_per_criteria[criteria]
                    valid_criteria = list(other._impact_per_criteria.keys())[0]
                    combined_value.warnings.append(
                        f"This value excludes the impacts {other.name or other[valid_criteria].name or other[valid_criteria]._as_formula()}"
                    )
                else:
                    combined_value = other._impact_per_criteria[criteria]
                    valid_criteria = next(iter(self._impact_per_criteria.keys()))
                    combined_value.warnings.append(
                        f"This value excludes the impacts {self.name or self[valid_criteria].name or self[valid_criteria]._as_formula()}"
                    )
                combined_impact[criteria] = combined_value

            return Impacts(combined_impact)
        else:
            # If other is a ReplicableValue, we add its value to each criteria in the impact
            combined_impact: dict[str, ReplicableValue] = {
                criteria: value + other for criteria, value in self._impact_per_criteria.items()
            }
            return Impacts(combined_impact)

    def __radd__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        return self.__add__(other)

    def __sub__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        if isinstance(other, Impacts):
            # if a criteria is present in both impacts, we subtract the values
            # if it is only present in one, we keep the value from that impact
            combined_impact: dict[str, ReplicableValue] = {}
            for criteria in set(self._impact_per_criteria) | set(other._impact_per_criteria):
                if criteria in self._impact_per_criteria and criteria in other._impact_per_criteria:
                    combined_impact[criteria] = (
                        self._impact_per_criteria[criteria] - other._impact_per_criteria[criteria]
                    )
                else:
                    raise ValueError(
                        "Can't substract an impact by another because some values for the criteria {criteria} are missing"
                    )

            return Impacts(combined_impact)
        else:
            # If other is a ReplicableValue, we subtract its value from each criteria in the impact
            combined_impact = {criteria: value - other for criteria, value in self._impact_per_criteria.items()}
            return Impacts(combined_impact)

    def __mul__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        if isinstance(other, Impacts):
            # if a criteria is present in both impacts, we multiply the values
            # if it is only present in one, we keep the value from that impact
            combined_impact: dict[str, ReplicableValue] = {}
            for criteria in set(self._impact_per_criteria) | set(other._impact_per_criteria):
                if criteria in self._impact_per_criteria and criteria in other._impact_per_criteria:
                    combined_value = self._impact_per_criteria[criteria] * other._impact_per_criteria[criteria]
                else:
                    raise ValueError(
                        "Can't multiply an impact by another because some values for the criteria {criteria} are missing"
                    )
                combined_impact[criteria] = combined_value

            return Impacts(combined_impact)
        else:
            # If other is a ReplicableValue, we multiply its value with each criteria in the impact
            combined_impact: dict[str, ReplicableValue] = {
                criteria: value * other for criteria, value in self._impact_per_criteria.items()
            }
            return Impacts(combined_impact)

    def __rmul__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        return self.__mul__(other)

    def __truediv__(self, other: "Impacts | ReplicableValue | int") -> "Impacts":
        if isinstance(other, Impacts):
            # if a criteria is present in both impacts, we divide the values
            # if it is only present in one, we keep the value from that impact
            combined_impact: dict[str, ReplicableValue] = {}
            for criteria in set(self._impact_per_criteria) | set(other._impact_per_criteria):
                if criteria in self._impact_per_criteria and criteria in other._impact_per_criteria:
                    combined_impact[criteria] = (
                        self._impact_per_criteria[criteria] / other._impact_per_criteria[criteria]
                    )
                else:
                    raise ValueError(
                        "Can't divide an impact by another because some values for the criteria {criteria} are missing"
                    )
            return Impacts(combined_impact)
        else:
            # If other is a ReplicableValue, we divide each criteria in the impact by its value
            combined_impact: dict[str, ReplicableValue] = {
                criteria: value / other for criteria, value in self._impact_per_criteria.items()
            }
            return Impacts(combined_impact)

    @staticmethod
    def sum(values: List["Impacts"]) -> "Impacts":
        @dataclass
        class OccurenceEntry:
            impact: "Impacts"
            occurences: int

        occurences: dict[int, OccurenceEntry] = {}
        for value in values:
            if value.name in occurences:
                occurences[hash(value)].occurences += 1
            else:
                occurences[hash(value)] = OccurenceEntry(value, 1)

        terms = []
        for entry in occurences.values():
            match entry.occurences:
                case 0:
                    continue
                case 1:
                    terms.append(entry.impact)
                case _:
                    terms.append(entry.impact * entry.occurences)

        return reduce(lambda x, y: x + y, terms)

    def __getitem__(self, criteria: str) -> ReplicableValue:
        return self._impact_per_criteria[criteria]

    def keys(self) -> list[str]:
        return list(self._impact_per_criteria.keys())

    def values(self) -> list[ReplicableValue]:
        return list(self._impact_per_criteria.values())

    def __getattr__(self, name: str):
        try:
            return getattr(self._impact_per_criteria, name)
        except AttributeError:
            return NotImplemented
