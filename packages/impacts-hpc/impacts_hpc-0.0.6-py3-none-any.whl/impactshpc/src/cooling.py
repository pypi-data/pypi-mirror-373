# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import pandas

from impactshpc.src.core.allocation import AllocationMethod, naive_allocation
from impactshpc.src.core.config import relative_to_absolute_path, ureg
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import EMBEDDED_IMPACTS, EMBODIED_IMPACTS, EXTRAPOLATION_FACTOR, Ontology
from impactshpc.src.core.utils import config

MAX_USAGE_RATE = SourcedValue(name="100%_usage_rate", value="1")

cooling_impacts = pandas.read_csv(relative_to_absolute_path(config["csv"]["cooling_impacts"]))
cooling_extrapolation_factors = pandas.read_csv(
    relative_to_absolute_path(config["csv"]["cooling_extrapolation_factors"])
)


class Cooling(HasEmbodiedImpacts):
    """Represents the cooling system and is used to compute its `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_`.

    Attributes:
        embodied_impacts (Impacts | str | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the cooling system. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        cooling_power (ReplicableValue | str): The :ref:`cooling power`, in watts.
        allocation_method (AllocationMethod): An :ref:`allocation method` used to attribute a part of the embodied impact of the cooling system to a specific job.
    """

    def __init__(
        self,
        cooling_power: ReplicableValue | str,
        embodied_impacts: Impacts | None = None,
        allocation_method: AllocationMethod | None = None,
    ):
        super().__init__(embodied_impacts)
        self.cooling_power = SourcedValue.from_argument("cooling_power", cooling_power)
        self.allocation_method = allocation_method or naive_allocation(
            SourcedValue.from_config("cooling_lifetime", config["default_values_park"]["cooling_lifetime"])
        )

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the cooling system.

        If :attr:`embodied_impacts` is not None, this method only returns it.

        The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the cooling system are reduced to the impact of the refrigeration unit.

        Interpolation factors are defined for the different phases. The extrapolation factor for a refrigeration unit of X watts is a number close to 1, which, when multiplied by the reference impacts (defined in the config file under csv > cooling_impacts), gives the impact of a refrigeration unit of X watts. For our estimation, we interpolate between the two closest extrapolation factors (defined in the config file under csv > cooling_extrapolation_factors).

        For example, if the :attr:`cooling_power` is 355 W, to compute the impact of the manufacturing phase, we will interpolate between the two closest extrapolation factors: for 346 W it's 1.12, and for 380 W it's 1.099. The interpolated factor is then multiplied by the reference impact (for the GWP impact, it's 60.4 kg CO2eq) to give the impact of the 355 W refrigeration unit.

        Returns:
            Impact: The embodied impact of the cooling system.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "cooling_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        capacities: list[int] = pandas.to_numeric(cooling_extrapolation_factors["Capacity kW"]).tolist()
        capacities.sort()

        inferior_power = SourcedValue(
            name="inferior_power",
            value=f"{max([c for c in capacities if c <= self.cooling_power.value.to('kW').magnitude], default=min(capacities))} kW",
            source=f"The bigger cooling power known in the database that is inferior to {self.cooling_power.value}",
        )
        superior_power = SourcedValue(
            name="superior_power",
            value=f"{min([c for c in capacities if c >= self.cooling_power.value.to('kW').magnitude], default=max(capacities))} kW",
            source=f"The smaller cooling power known in the database that is superior to {self.cooling_power.value}",
        )
        inferior_power_row = cooling_extrapolation_factors[
            cooling_extrapolation_factors["Capacity kW"] == inferior_power.value.to("kW").magnitude
        ]
        superior_power_row = cooling_extrapolation_factors[
            cooling_extrapolation_factors["Capacity kW"] == superior_power.value.to("kW").magnitude
        ]

        phases_impacts = []

        for phase in ["manufacturing", "distribution", "installation"]:
            inferior_extrapolation_factor = SourcedValue(
                name=f"{phase}_inferior_extrapolation_factor",
                value=f"{inferior_power_row[phase].squeeze()}",
                source=f"Extrapolation factor for the {phase} phase of {round(inferior_power.value)}. Source : {inferior_power_row['source'].squeeze()}",
            )

            superior_extrapolation_factor = SourcedValue(
                name=f"{phase}_superior_extrapolation_factor",
                value=f"{superior_power_row[phase].squeeze()}",
                source=f"Extrapolation factor for the {phase} phase of {round(superior_power.value)}. Source : {inferior_power_row['source'].squeeze()}",
            )

            if inferior_power.value == superior_power.value:
                extrapolation_factor = inferior_extrapolation_factor
                extrapolation_factor.make_intermediate_result(
                    f"{phase}_extrapolation_factor.",
                    f"Extrapolation factor for the {phase} phase of {round(self.cooling_power.value)}.",
                    override_unit=ureg.Unit("W⁻¹"),
                    ontology=EXTRAPOLATION_FACTOR,
                )
            else:
                extrapolation_factor = _linear_interp(
                    inferior_power,
                    inferior_extrapolation_factor,
                    superior_power,
                    superior_extrapolation_factor,
                    self.cooling_power,
                )

                extrapolation_factor.make_intermediate_result(
                    f"{phase}_extrapolation_factor.",
                    f"Extrapolation factor for the {phase} phase of {round(self.cooling_power.value)}. Linear interpolation of the extrapolation factor for {round(inferior_power.value)} cooling and {round(superior_power.value)}.",
                    override_unit=ureg.Unit("W⁻¹"),
                    ontology=EXTRAPOLATION_FACTOR,
                )
            reference_impact = Impacts(
                {
                    "gwp": SourcedValue(
                        name=f"{phase}_reference_impact",
                        value=f"{cooling_impacts[cooling_impacts['criteria'] == 'gwp'][phase].squeeze()} gCO2eq",
                        source=f"Reference Impact. This the impact of a 1kW of cooling for a extrapolation factor of 1. Source: {cooling_impacts[cooling_impacts['criteria'] == 'gwp']['source'].squeeze()}",
                    ),
                    "adpe": SourcedValue(
                        name=f"{phase}_reference_impact",
                        value=f"{cooling_impacts[cooling_impacts['criteria'] == 'adpe'][phase].squeeze()} gSbeq",
                        source=f"Reference Impact. This the impact of a 1kW of cooling for a extrapolation factor of 1. Source: {cooling_impacts[cooling_impacts['criteria'] == 'gwp']['source'].squeeze()}",
                    ),
                    "pe": SourcedValue(
                        name=f"{phase}_reference_impact",
                        value=f"{cooling_impacts[cooling_impacts['criteria'] == 'pe'][phase].squeeze()} MJ",
                        source=f"Reference Impact. This the impact of a 1kW of cooling for a extrapolation factor of 1. Source: {cooling_impacts[cooling_impacts['criteria'] == 'pe']['source']}",
                    ),
                }
            )
            phase_impact = reference_impact * self.cooling_power * extrapolation_factor
            phase_impact.make_intermediate_result(
                f"{phase}_cooling_impacts",
                f"Impacts of the {phase} phase of cooling group of {self.cooling_power.value}.",
            )
            phases_impacts.append(phase_impact)

        embodied_impact = Impacts.sum(phases_impacts)
        embodied_impact.make_intermediate_result(
            "cooling_embodied_impact",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied_impact

    def embedded_impacts(self, job_duration: ReplicableValue) -> Impacts:
        """Estimate the :ref:`embedded impacts` of the cooling system for the job.

        Internally uses :meth:`estimate_embodied_impacts` and passes it the :attr:`allocation_method` with the ``job_duration``.

        Args:
            job_duration (ReplicableValue): The duration of the job we want to allocate the embodied impacts to.

        Returns:
            Impact: The :ref:`embedded impacts` of the cooling system for the job.
        """
        embedded = self.allocation_method(self.estimate_embodied_impacts(), job_duration, MAX_USAGE_RATE)
        embedded.make_intermediate_result("cooling_embedded_impact", ontology=EMBEDDED_IMPACTS)
        return embedded


def _linear_interp(
    x0: ReplicableValue,
    y0: ReplicableValue,
    x1: ReplicableValue,
    y1: ReplicableValue,
    x: ReplicableValue,
) -> ReplicableValue:
    """Compute a linear interpolation between the points (x0, y0) and (x1, y1) with an interpolation factor x.

    Args:
        x0 (ReplicableValue): The x coordinate of the first point.
        y0 (ReplicableValue): The y coordinate of the first point.
        x1 (ReplicableValue): The x coordinate of the second point.
        y1 (ReplicableValue): The y coordinate of the second point.
        x (ReplicableValue): An interpolation factor between 0 and 1, indicating how close to (x0, y0) and how far from (x1, y1) the result will be.

    Returns:
        ReplicableValue: The interpolated value.
    """

    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)
