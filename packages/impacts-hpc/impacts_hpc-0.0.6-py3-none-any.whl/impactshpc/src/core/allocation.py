# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from typing import Callable

from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue

ONE_YEAR_HOURS = SourcedValue(
    name="one_year",
    value="8760 h",
    source="Number of hours in one year",
)

# Embodied impacts, duration of the job, usage rate -> embedded impact
type AllocationMethod = Callable[[Impacts, ReplicableValue, ReplicableValue], Impacts]


def naive_allocation(lifetime: ReplicableValue | str) -> AllocationMethod:
    """
    Naive allocation method consist of dividing the embodied impact of a component by its lifetime.
    """

    def allocation(embodied_impacts: Impacts, duration: ReplicableValue, usage_rate: ReplicableValue) -> Impacts:
        total_usage_duration = SourcedValue.from_argument("lifetime", lifetime) * usage_rate
        total_usage_duration.make_intermediate_result(
            "total_usage_duration", "The total amount of time that the server has been in active use."
        )
        embedded = embodied_impacts * (duration / total_usage_duration)
        return embedded

    return allocation


def decrease_over_time_allocation(age: ReplicableValue | str) -> AllocationMethod:
    """
    First year of commissioning is 50% of the embodied impact, second year is 25%, third year is 12.5%, etc.
    """

    age = SourcedValue.from_argument("age", age)

    def allocation(embodied_impacts: Impacts, duration: ReplicableValue, usage_rate: ReplicableValue) -> Impacts:
        duration_ratio = duration / ONE_YEAR_HOURS
        year_of_use_ratio = SourcedValue(
            name="year_of_use_ratio",
            value=f"{0.5 ** age.value.to('year').magnitude}",  # type: ignore
            explaination="Ratio of the total embodied impact allocated to the year of use. First year is 50% of the total embodied impact, second year is 25%, third year is 12.5%, etc.",
        )

        year_impact = embodied_impacts * year_of_use_ratio
        year_impact.make_intermediate_result(
            "year_impacts",
            f"The impacts attributed to the {inflect(age.value.magnitude)} year of usage of the component. First year is 50% of the total embodied impact, second year is 25%, third year is 12.5%, etc.",
        )

        embedded = year_impact * duration_ratio

        return embedded

    return allocation


def inflect(number: int) -> str:
    """Numbers ending by XXX1 becomes XXX1st, XXX2 becomes XXX2nd, XXX3 becomes XXX3rd, and after it becomes XXXth

    Args:
        number (int): a number

    Returns:
        str: Numbers ending by XXX1 becomes XXX1st, XXX2 becomes XXX2nd, XXX3 becomes XXX3rd, and after it becomes XXXth
    """
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

    return f"{number}{suffix}"
