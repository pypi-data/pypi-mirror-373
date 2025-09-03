# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from enum import Enum

from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.allocation import AllocationMethod, naive_allocation
from impactshpc.src.core.config import config
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import ELECTRIC_POWER, EMBODIED_IMPACTS, IDLE_POWER, PEAK_POWER, Ontology


class HDD(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a HDD disk.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/hdd/
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        pass

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the HDD.

        Simply returns a constant impact defined in the config file under ``default_value_hdd``.

        Returns:
            Impact | None: The HDD `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_ .
        """
        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "HDD_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts
        return Impacts.from_config("hdd_embodied_impacts", config["default_value_hdd"])

    def estimate_electric_power(self) -> ReplicableValue | None:
        """Instant consumption of HDD is ignored.

        Returns:
            ReplicableValue | None: Always returns None.
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("HDD_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        return SourcedValue(
            name="hdd_idle_power", value="0 W", source="HDD consumption is ignored.", ontology=ELECTRIC_POWER
        )

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("HDD_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        return SourcedValue(
            name="hdd_idle_power", value="0 W", source="HDD consumption is ignored.", ontology=IDLE_POWER
        )

    def estimate_peak_power(self) -> ReplicableValue | None:
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("HDD_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        return SourcedValue(name="hdd_peak_power", value="0 W", source="HDD consumption is ignored.")


class PowerSupply(HasConsumptionAndEmbodiedImpacts):
    """Represents a power supply and computes its impacts.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/power_supply/

    Attributes:
        weight (ReplicableValue | None, optional): The weight of the power supply. Defaults to the value in the config file under ``default_value_power_supply > weight``.
    """

    def __init__(
        self,
        weight: ReplicableValue | None = None,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.weight = weight or SourcedValue.from_config(
            "power_supply_weight", config["default_value_power_supply"]["weight"]
        )

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the CPU.

        This is done by multiplying the :attr:`weight` by an impact factor defined in the config file under ``default_value_power_supply > impact_factor``.

        Returns:
            Impact | None: The estimated embodied impacts of the CPU.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "power_supply_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        impact_factor = Impacts.from_config(
            "power_supply_impact_factor",
            config["default_value_power_supply"]["impact_factor"],
        )
        embodied = impact_factor * self.weight
        embodied.make_intermediate_result(
            "power_supply_embodied_impacts",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied

    def estimate_electric_power(self) -> ReplicableValue | None:
        """Instant consumption of HDD is ignored.

        Returns:
            ReplicableValue | None: Always returns None.
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("power_supply_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        return SourcedValue(
            name="power_supply_electric_power",
            value="0 W",
            source="PowerSupply consumption is ignored.",
            ontology=ELECTRIC_POWER,
        )

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("power_supply_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        return SourcedValue(name="power_supply_idle_power", value="0 W", source="PowerSupply consumption is ignored.")

    def estimate_peak_power(self) -> ReplicableValue | None:
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("power_supply_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        return SourcedValue(name="power_supply_peak_power", value="0 W", source="PowerSupply consumption is ignored.")


class MotherBoard(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a Motherboard.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/motherboard/

    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        pass

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the motherboard.

        Simply returns a constant impact defined in the config file under ``motherboard_embodied_impact``.

        Returns:
            Impact | None: The motherboard `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_ .
        """
        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "motherboard_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        return Impacts.from_config("motherboard_embodied_impact", config["motherboad_embodied_impact"])

    def estimate_electric_power(self) -> ReplicableValue | None:
        """Instant consumption of motherboard is ignored.

        Returns:
            ReplicableValue | None: always returns None
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("motherboard_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        return SourcedValue(
            name="motherboard_electric_power",
            value="0 W",
            source="Motherboard consumption is ignored.",
            ontology=ELECTRIC_POWER,
        )

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("motherboard_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        return SourcedValue(name="motherboard_idle_power", value="0 W", source="Motherboard consumption is ignored.")

    def estimate_peak_power(self) -> ReplicableValue | None:
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("motherboard_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        return SourcedValue(name="motherboard_peak_power", value="0 W", source="Motherboard consumption is ignored.")


class CaseType(Enum):
    RACK = "RACK"
    BLADE = "BLADE"


MAX_USAGE_RATE = SourcedValue(name="100%_usage_rate", value="100%")


class Case(HasEmbodiedImpacts):
    """
    Representes case containing servers, used to computes it's `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_ *

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/case/

    Attributes:
        embodied_impacts (Impacts | str | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the battery. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        server_count (ReplicableValue | str | int | float): The number of servers cases
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        type: CaseType = CaseType.RACK,
        allocation_method: AllocationMethod | None = None,
    ) -> None:
        super().__init__(embodied_impacts)
        self.type = type
        self.allocation_method = allocation_method or naive_allocation(
            SourcedValue.from_config("case_lifetime", config["default_value_case"]["lifetime"])
        )

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the cases.

        Returns a constant impact depending on the type of case used. These values are defined in the config file under ``default_value_case``.

        Returns:
            Impact | None: The case `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_ .
        """
        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "case_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        match self.type:
            case CaseType.RACK:
                return Impacts.from_config("rack_case_impact", config["default_value_case"]["rack"])
            case CaseType.BLADE:
                return Impacts.from_config("blade_case_impact", config["default_value_case"]["blade"])

    def embedded_impacts(self, job_duration: ReplicableValue):
        """Estimate the :ref:`embedded impacts` of the cases for the job.

        Internally uses :meth:`estimate_embodied_impacts` and passes it the :attr:`allocation_method` with the ``job_duration``.

        Args:
            job_duration (ReplicableValue): The duration of the job we want to allocate the embodied impacts to.

        Returns:
            Impact: The :ref:`embedded impacts` of the cases for the job.
        """
        return self.allocation_method(self.estimate_embodied_impacts(), job_duration, MAX_USAGE_RATE)
