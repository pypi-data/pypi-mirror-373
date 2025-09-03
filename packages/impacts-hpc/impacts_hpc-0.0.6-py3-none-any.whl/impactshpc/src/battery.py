# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import pandas

from impactshpc.src.core.allocation import AllocationMethod, naive_allocation
from impactshpc.src.core.config import config, relative_to_absolute_path
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import BATTERY_CAPACITY, BATTERY_WEIGHT, EMBEDDED_IMPACTS, EMBODIED_IMPACTS, Ontology

batteries_impacts = pandas.read_csv(relative_to_absolute_path(config["csv"]["batteries_impacts"]))

MAX_USAGE_RATE = SourcedValue(name="100%_usage_rate", value="1")


class Battery(HasEmbodiedImpacts):
    """Represents the emergency batteries and is used to compute their `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_ .

    Either :attr:`capacity` or both :attr:`server_consumption` and :attr:`battery_duration` must be defined.

    Attributes:
        embodied_impacts (Impacts | str | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the battery. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        capacity (ReplicableValue | None, optional): The `battery capacity <TODO : REPLACE WITH ONTOLOGY OF BATTERY CAPACITY>`_. If None, it will be estimated from :attr:`server_consumption` and :attr:`battery_duration`.
        server_consumption (ReplicableValue | None, optional): The consumption of the server. Defaults to None.
        battery_duration (ReplicableValue | str | None, optional): The battery's expected duration with a consumption of :attr:`server_consumption`. Defaults to the value in the config file under ``default_values_battery > duration``.
        battery_type (str | None, optional): The type of the battery, which can be VRLA, LFP, LTO, LMO, NCM, NCA, NaNiCl, or VRFB. Defaults to the value in the config file under ``default_values_battery > type``.
        allocation_method (AllocationMethod | None, optional): The :ref:`allocation method` used to attribute a part of the battery's embodied impacts to a specific job. Defaults to :func:`naive_allocation`, where the lifetime is the value in the config file under ``default_values_battery > lifetime``.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        capacity: ReplicableValue | None = None,
        server_consumption: ReplicableValue | None = None,
        battery_duration: ReplicableValue | str | None = None,
        battery_type: str | None = None,
        allocation_method: AllocationMethod | None = None,
    ) -> None:
        super().__init__(embodied_impacts)
        self.server_consumption = server_consumption
        self.battery_duration = SourcedValue.from_argument(
            "battery_duration", battery_duration
        ) or SourcedValue.from_config("battery_duration", config["default_values_battery"]["duration"])
        self.battery_type = battery_type or config["default_values_battery"]["type"]
        self.allocation_method = allocation_method or naive_allocation(
            SourcedValue.from_config("batteries_lifetime", config["default_values_battery"]["lifetime"])
        )
        assert capacity is not None or self.server_consumption is not None

        self.capacity: ReplicableValue = (
            capacity or self.server_consumption * self.battery_duration  # type: ignore Pylance doesn't not see that self.server_consumption can't be None here
        )
        self.capacity.make_intermediate_result(
            "batteries_capacity",
            ontology=BATTERY_CAPACITY,
        )

        self.batterie_density = self._battery_density()
        self.weight = self.capacity / self.batterie_density
        self.weight.make_intermediate_result(
            f"battery_weight_{battery_type}",
            "Weight of the battery, estimated from its capacity in Wh stored, and the weight per Wh of capacity, that is itself deduced from the battery type.",
            ontology=BATTERY_WEIGHT,
        )

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the battery.

        If :attr:`embodied_impacts` is not None, this method only returns it.

        Otherwise, the formula used is: ``impact_per_kilo * weight``, where:

        - ``impact_per_kilo`` is the impact of 1 kilogram of battery of the type :attr:`battery_type`. It is computed by :meth:`_impact_per_kg`.
        - ``weight`` is the weight of the battery. It is computed from its :attr:`capacity` and the battery density computed by :meth:`_battery_density`.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACTS>`_ of the Battery.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "battery_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        embodied_impact = self._impact_per_kg(self.battery_type) * self.weight
        embodied_impact.make_intermediate_result(
            "batteries_embodied_impact",
            "Embedded impacts of the battery, estimated from its weight and the impact per kg of the battery type.",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied_impact

    def estimate_embedded_impacts(self, job_duration: ReplicableValue):
        """Estimate the :ref:`embedded impacts` of the batteries for the job.

        Internally uses :meth:`estimate_embodied_impacts` and passes it the :attr:`allocation_method` with the ``job_duration``.

        Args:
            job_duration (ReplicableValue): The duration of the job we want to allocate the embodied impacts to.

        Returns:
            Impact: The :ref:`embedded impacts` of the batteries for the job.
        """
        embedded = self.allocation_method(self.estimate_embodied_impacts(), job_duration, MAX_USAGE_RATE)
        embedded.make_intermediate_result("battery_embedded_impacts", ontology=EMBEDDED_IMPACTS)
        return embedded

    def _impact_per_kg(self, battery_type: str) -> Impacts:
        """Estimate the impact of 1 kilogram of battery, based on the battery type.

        Args:
            battery_type (str): The battery type, which can be VRLA, LFP, LTO, LMO, NCM, NCA, NaNiCl, or VRFB.

        Raises:
            ValueError: If the battery type is not known.

        Returns:
            Impact: The impacts of 1 kilogram of battery.
        """

        battery_specs = batteries_impacts[batteries_impacts["type"] == battery_type]

        if battery_specs.empty:
            raise ValueError(f"No battery specs found for type: {battery_type}")

        impact_per_kg = ReplicableValue.average(
            battery_specs["CO2_per_kg"].astype(float).tolist(),
            name="impact_per_kg",
            unit="kgCO2eq / kg",
            source=f"Average impact per kg for {battery_type} batteries from our database. {len(battery_specs)} values averaged.",
        )

        return Impacts({"gwp": impact_per_kg})

    def _battery_density(self) -> ReplicableValue:
        """Calculate the :ref:`battery density`, i.e., the energy that can be contained in 1 kilogram of battery.

        Raises:
            ValueError: Raised if :attr:`battery_type` is not one of VRLA, LFP, LTO, LMO, NCM, NCA, NaNiCl, or VRFB.

        Returns:
            ReplicableValue: The energy contained in 1 kilogram of battery.
        """

        battery_specs = batteries_impacts[batteries_impacts["type"] == self.battery_type]
        if battery_specs.empty:
            raise ValueError(f"No battery specs found for type: {self.battery_type}")

        density = ReplicableValue.average(
            battery_specs["wh_per_kg"].astype(float).tolist(),
            name="battery_density",
            unit="W . h / kg",
            source=f"Average density for {self.battery_type} batteries from our database.",
        )
        return density
