# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


import itertools
from typing import List, Tuple

from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.allocation import AllocationMethod, naive_allocation
from impactshpc.src.core.config import config
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import (
    CorrelationMode,
    ReplicableValue,
    SourcedValue,
)
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import (
    ELECTRIC_POWER,
    EMBEDDED_IMPACTS,
    EMBODIED_IMPACTS,
    IDLE_POWER,
    PEAK_POWER,
    Ontology,
)
from impactshpc.src.other_components import Case

# only electronic components, not Server instances
type Component = HasConsumptionAndEmbodiedImpacts


class Server(HasConsumptionAndEmbodiedImpacts):
    """Represents a :ref:`server` and is used to compute its impacts.

    Attributes:
        embodied_impacts (Impacts | str | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the server. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        components (List[Tuple[Component, int]], optional): A list of the :class:`Component` instances that represent the electronic components of the server, along with the number of each component in the server. Defaults to [].
        allocation_method (AllocationMethod | None, optional): An :ref:`allocation method <allocation method>` for the server. Defaults to :func:`naive_allocation` for the default lifetime of a server, defined in the config file under default_values_server > lifetime.
        usage_rate (ReplicableValue | None, optional): The usage rate of the server, between 0 and 1. Defaults to the value defined in the config file under default_values_server > usage_rate.
    Example:
    --------

    .. code-block:: python

        Server(
            components=[
                (CPU(name=ExactName("Intel Xeon Gold 6132")), 2),
                (RAM(size=SourcedValue(name="ram_size", value="3 TB", source="User Input")), 1),
                (GPU(name=find_close_gpu_model_name("Nvidia Tesla V100")), 4), # In the spec, we don't know the exact variant of Nvidia V100 used, so we can use find_close_gpu_model_name result and it will average the matching GPUs
                (MotherBoard(), 1),
            ]
        )

    This represents a server with two Intel Xeon Gold 6132 CPUs, three terabytes of RAM, four Nvidia Tesla V100 GPUs, and a motherboard.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        components: List[Tuple[Component, int]] = [],
        case: Case = Case(),
        allocation_method: AllocationMethod | None = None,
        usage_rate: ReplicableValue | None = None,
    ) -> None:
        super().__init__(embodied_impacts)
        self.components = components
        self.case = case
        self.allocation_method = allocation_method or naive_allocation(
            SourcedValue.from_config("lifetime", config["default_values_server"]["lifetime"])
        )
        self.usage_rate = usage_rate or SourcedValue.from_config(
            "usage_rate", config["default_values_server"]["usage_rate"]
        )

        # We split components in group, CPUs with CPUs, RAM with RAM...
        # In a group, sums are done in the DEPENDANT correlation mode, while between groups the final sum is done in INDEPENDANT correlation mode.
        self.groups = [list(group) for key, group in itertools.groupby(components, lambda tuple: type(tuple[0]))]

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the server.

        The server's embodied impacts are the sum of its components' embodied impacts.

        For :ref:`Uncertainties <uncertainty>`, the sum of the components of the same type is done in dependent mode, i.e., CPUs' impacts are considered positively correlated (correlation = 1) with other CPUs' impacts, RAM sticks are correlated with other RAM sticks, etc.

        The final sum of each group of the correlated impacts is done in independent mode, i.e., they are considered uncorrelated (correlation = 0).

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the server.
        """
        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "server_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        groups_impacts = []
        with ReplicableValue.set_correlation_mode(CorrelationMode.DEPENDENT):
            for group in self.groups:
                components_impacts = [c[0].estimate_embodied_impacts() * c[1] for c in group]
                components_impacts = [c for c in components_impacts if c is not None]
                if len(components_impacts) == 0:
                    continue

                groups_impacts.append(Impacts.sum(components_impacts))

        with ReplicableValue.set_correlation_mode(CorrelationMode.INDEPENDENT):
            total_impact = (
                Impacts.sum(groups_impacts)
                + self.case.estimate_embodied_impacts()
                + Impacts.from_config("server_assembly_impacts", config["default_value_assembly"])
            )

        total_impact.make_intermediate_result(
            "server_embodied_impact",
            ontology=EMBODIED_IMPACTS,
        )

        return total_impact

    def estimate_electric_power(self) -> ReplicableValue:
        """Estimate the `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the server.

        The server's instant consumption is the sum of its components' power consumptions.

        For :ref:`Uncertainties <uncertainty>`, the sum of the components of the same type is done in dependent mode, i.e., CPUs' consumptions are considered positively correlated (correlation = 1) with other CPUs' consumptions, RAM sticks are correlated with other RAM sticks, etc.

        The final sum of each group of the correlated consumptions is done in independent mode, i.e., they are considered uncorrelated (correlation = 0).

        Returns:
            ReplicableValue: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the server.
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("server_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        groups_consumptions = []
        with ReplicableValue.set_correlation_mode(CorrelationMode.DEPENDENT):
            for group in self.groups:
                components_electric_powers = [(c[0].estimate_electric_power(), c[1]) for c in group]
                components_electric_powers = [c[0] * c[1] for c in components_electric_powers if c[0] is not None]

                if len(components_electric_powers) == 0:
                    continue

                groups_consumptions.append(ReplicableValue.sum(components_electric_powers))

        with ReplicableValue.set_correlation_mode(CorrelationMode.INDEPENDENT):
            total_consumption = ReplicableValue.sum(groups_consumptions)

        total_consumption.make_intermediate_result("server_consumption", ontology=ELECTRIC_POWER)
        return total_consumption

    def estimate_peak_power(self) -> ReplicableValue:
        """Estimate the `peak power <TODO : REPLACE WITH ONTOLOGY OF PEAK POWER>`_ of the server.

        The server's peak consumption is the sum of its components' peak power consumptions.

        For :ref:`Uncertainties <uncertainty>`, the sum of the components of the same type is done in dependent mode, i.e., CPUs' consumptions are considered positively correlated (correlation = 1) with other CPUs' consumptions, RAM sticks are correlated with other RAM sticks, etc.

        The final sum of each group of the correlated consumptions is done in independent mode, i.e., they are considered uncorrelated (correlation = 0).

        Returns:
            ReplicableValue: The `peak power <TODO : REPLACE WITH ONTOLOGY OF PEAK POWER>`_ of the server.
        """
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("server_peak_power", ontology=PEAK_POWER)
            return self.peak_power
        groups_peak_powers = []
        with ReplicableValue.set_correlation_mode(CorrelationMode.DEPENDENT):
            for group in self.groups:
                components_peak_powers = [(c[0].estimate_peak_power(), c[1]) for c in group]
                components_peak_powers = [c[0] * c[1] for c in components_peak_powers if c[0] is not None]

                if len(components_peak_powers) == 0:
                    continue

                groups_peak_powers.append(ReplicableValue.sum(components_peak_powers))

        with ReplicableValue.set_correlation_mode(CorrelationMode.INDEPENDENT):
            total_peak_power = ReplicableValue.sum(groups_peak_powers)

        total_peak_power.make_intermediate_result("server_peak_power", ontology=PEAK_POWER)
        return total_peak_power

    def estimate_idle_power(self) -> ReplicableValue:
        """Estimate the `idle power <TODO : REPLACE WITH ONTOLOGY OF IDLE POWER>`_ of the server.

        The server's static consumption is the sum of its components' power consumptions at idle.

        For :ref:`Uncertainties <uncertainty>`, the sum of the components of the same type is done in dependent mode, i.e., CPUs' consumptions are considered positively correlated (correlation = 1) with other CPUs' consumptions, RAM sticks are correlated with other RAM sticks, etc.

        The final sum of each group of the correlated consumptions is done in independent mode, i.e., they are considered uncorrelated (correlation = 0).

        Returns:
            ReplicableValue: The `idle power <TODO : REPLACE WITH ONTOLOGY OF IDLE POWER>`_ of the server.
        """
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("server_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        groups_idle_powers = []
        with ReplicableValue.set_correlation_mode(CorrelationMode.DEPENDENT):
            for group in self.groups:
                components_idle_powers = [(c[0].estimate_idle_power(), c[1]) for c in group]
                components_idle_powers = [c[0] * c[1] for c in components_idle_powers if c[0] is not None]

                if len(components_idle_powers) == 0:
                    continue

                groups_idle_powers.append(ReplicableValue.sum(components_idle_powers))

        with ReplicableValue.set_correlation_mode(CorrelationMode.INDEPENDENT):
            total_idle_power = ReplicableValue.sum(groups_idle_powers)

        total_idle_power.make_intermediate_result("server_idle_power", ontology=IDLE_POWER)
        return total_idle_power

    def estimate_embedded_impacts(self, job_duration: ReplicableValue) -> Impacts:
        """Estimate the :ref:`embedded impacts` of the server for the job.

        Internally uses :meth:`estimate_embodied_impacts` and passes it the :attr:`allocation_method` with the ``job_duration``.

        Args:
            job_duration (ReplicableValue): The duration of the job we want to allocate the embodied impacts to.

        Returns:
            Impact: The :ref:`embedded impacts` of the server for the job.
        """

        embedded = self.allocation_method(self.estimate_embodied_impacts(), job_duration, self.usage_rate)
        embedded.make_intermediate_result("server_embedded_impact", ontology=EMBEDDED_IMPACTS)
        return embedded
