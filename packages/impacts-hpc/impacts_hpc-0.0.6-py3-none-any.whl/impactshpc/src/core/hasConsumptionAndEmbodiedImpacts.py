# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from dataclasses import dataclass

from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import PEAK_POWER


@dataclass
class HasConsumptionAndEmbodiedImpacts(HasEmbodiedImpacts, ABC):
    """Abstract class defining the methods for estimating `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_, `peak power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_ and `idle power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_

    Attributes:
        embodied_impacts (Impacts | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the component. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        electric_power (ReplicableValue | str | None, optional): The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the component. If the value is known, :meth:`estimate_electric_power` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        peak_power (ReplicableValue | str | None, optional): The `peak power <TODO : REPLACE WITH ONTOLOGY OF PEAK POWER>`_ of the component. If the value is known, :meth:`estimate_peak_power` returns it, otherwise an estimation is done based on other attributes . Defaults to None.
        idle_power (ReplicableValue | str | None, optional): The `idle power <TODO : REPLACE WITH ONTOLOGY OF IDLE POWER>`_ of the component. If the value is known, :meth:`estimate_idle_power` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
    ):
        super().__init__(embodied_impacts)
        self.electric_power = SourcedValue.from_argument("electric_power", electric_power)
        self.peak_power = SourcedValue.from_argument("peak_power", peak_power)
        self.idle_power = SourcedValue.from_argument("idle_power", idle_power)

    @abstractmethod
    def estimate_electric_power(self) -> ReplicableValue | None:
        pass

    def estimate_peak_power(self) -> ReplicableValue | None:
        """Returns the maximum consumption of the component"""
        return self.peak_power or self.electric_power or self.estimate_electric_power()

    def estimate_idle_power(self) -> ReplicableValue | None:
        """Returns the minimum consumption of the component, the consumption it has when no job are running"""

        return self.idle_power or SourcedValue(
            name="ZERO",
            source="static consumption is ignored. Feel free to change this behavior in impacthpc/src/gpu.py",
            value="0 watt",
        )
