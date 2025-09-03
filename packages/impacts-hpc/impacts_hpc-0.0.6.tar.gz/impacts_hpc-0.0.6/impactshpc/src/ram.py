# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


import pandas

from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.config import relative_to_absolute_path, config
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.ontology import ELECTRIC_POWER, EMBODIED_IMPACTS, IDLE_POWER, PEAK_POWER, Ontology

ram_manufacture = pandas.read_csv(relative_to_absolute_path(config["csv"]["ram_manufacture"]))


class RAM(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a RAM stick.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/ram/

    Attributes:
        size (ReplicableValue | str | None, optional): The :ref:`RAM size`. Defaults to the value in the config file under ``default_values_ram > size``.
        density (ReplicableValue | None, optional): :ref:`RAM density` is the quantity of data (in gigabytes) that a cm² of RAM contains. This value is expressed in GB/cm². Defaults to an estimation made by :meth:`_estimate_density`.
        engraving_process_thickness (ReplicableValue | str | None, optional): The thickness of the engraving process for manufacturing this RAM stick. If :attr:`density` is provided, this attribute is ignored. Defaults to None.
        manufacturer (str | None, optional): The manufacturing company. If :attr:`density` is provided, this attribute is ignored. Defaults to None.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
        size: ReplicableValue | str | None = None,
        density: ReplicableValue | str | None = None,
        engraving_process_thickness: ReplicableValue | str | None = None,
        manufacturer: str | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.size = SourcedValue.from_argument("size", size) or SourcedValue.from_config(
            "ram_size", config["default_values_ram"]["size"]
        )

        self._engraving_process_thickness = SourcedValue.from_argument(
            "engraving_process_thickness", engraving_process_thickness
        )
        self._surface_impact_factor = Impacts.from_config(
            "surface_impact_factor",
            config["default_values_ram"]["surface_impact_factor"],
        )
        self._base_impact = Impacts.from_config("base_config", config["default_values_ram"]["base_impact"])
        self._electrical_consumption_per_gigabyte = SourcedValue.from_config(
            "ram_consumption_factor",
            config["default_values_ram"]["ram_consumption_factor"],
        )
        self.manufacturer = manufacturer

        self.density = SourcedValue.from_argument("density", density) or self._estimate_density()

    def estimate_electric_power(self) -> ReplicableValue:
        """Estimate the `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the RAM stick.

        The estimation is based on the :attr:`size` and a factor indicating the consumption per gigabyte of RAM. This factor is defined in the config file under ``default_values_ram > electrical_consumption_per_gigabyte``.

        Returns:
            ReplicableValue: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the RAM stick.
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("ram_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        electric_power = self._electrical_consumption_per_gigabyte * self.size
        electric_power.make_intermediate_result(
            f"{self.size.value.magnitude}_GB_ram_{self.manufacturer or ''}_electric_power",
            "The RAM power consumption. Estimated from its size and an impact factor that gives the power per gigabyte of size.",
            ontology=ELECTRIC_POWER,
        )

        return electric_power

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("ram_idle_power", ontology=IDLE_POWER)
            return self.idle_power
        return SourcedValue(
            name="ram_idle_power", value="0 W", source="RAM static consumption is ignored.", ontology=IDLE_POWER
        )

    def estimate_peak_power(self):
        """Estimate the peak (maximum) `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU when the workload is 100%.

        The CPU's peak instant consumption is estimated using the :meth:`estimate_electric_power` method with a workload of 100%.

        Returns:
            Impact: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.
        """

        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("ram_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        peak = self.estimate_electric_power()
        peak.make_intermediate_result("ram_peak_power", ontology=PEAK_POWER)
        return peak

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the RAM.

        The embodied impacts of the RAM are estimated using the formula: ``self._surface_impact_factor * surface + self._base_impact``, where:

        - ``_surface_impact_factor`` is the impact of 1 cm² of RAM stick. It is defined in the config file under ``default_values_ram > surface_impact_factor``.
        - ``surface`` is the surface of the RAM stick estimated from its :attr:`size` and its :attr:`density`.
        - ``_base_impact`` is a constant impact of every RAM stick, which includes packaging, transport, etc. It is defined in the config file under ``default_values_ram > base_impact``.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the RAM.
        """
        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "ram_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        surface = self.size / self.density
        embodied_impacts = self._surface_impact_factor * surface + self._base_impact
        embodied_impacts.make_intermediate_result(
            "ram_embodied_impacts",
            "Embodied impacts estimated from the RAM stick surface and a factor giving the impact per cm² of RAM stick, plus the impact of the base impact that is the impact of the packaging, transport, etc, constant for all RAM sticks.",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied_impacts

    def _estimate_density(self) -> ReplicableValue:
        """Estimate the :ref:`RAM density` of the RAM stick.

        This estimation uses the :attr:`manufacturer` and the :attr:`engraving_process_thickness`. We first average the density of the RAM sticks in the file defined in the config file under ``csv > ram_manufacture`` that have the same manufacturer and the same engraving process thickness.

        If there are no sticks like that, we average the density of sticks with the same manufacturer. If there are still no matching sticks, we average the density of the sticks with the same engraving process thickness. If no sticks match at all, we return the average density of all RAM sticks.

        Returns:
            ReplicableValue: The estimated :ref:`RAM density` of the RAM stick.
        """

        same_manufacturer = ram_manufacture[ram_manufacture["manufacturer"] == self.manufacturer]

        if self._engraving_process_thickness is not None:
            same_engraving_process = ram_manufacture[
                ram_manufacture["process"] == self._engraving_process_thickness.value.to("nm").magnitude
            ]
            same_manufacturer_and_engraving_process = ram_manufacture[
                (ram_manufacture["manufacturer"] == self.manufacturer)
                & (ram_manufacture["process"] == self._engraving_process_thickness.value.to("nm").magnitude)
            ]
        else:
            same_engraving_process = pandas.DataFrame()
            same_manufacturer_and_engraving_process = pandas.DataFrame()

        if not same_manufacturer_and_engraving_process.empty:
            average = ReplicableValue.average(
                same_manufacturer_and_engraving_process["density"].tolist(),
                name="density",
                unit="GB / cm²",
                source=f"Average density of RAM specs with the same manufacturer and engraving process. Number of values averaged: {len(same_manufacturer_and_engraving_process)}. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ram_manufacture.csv",
            )

            return average
        elif not same_manufacturer.empty:
            average = ReplicableValue.average(
                same_manufacturer["density"].tolist(),
                name="density",
                unit="GB / cm²",
                source=f"Average density of RAM specs with the same manufacturer. Number of values averaged: {len(same_manufacturer)}. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ram_manufacture.csv",
            )

            return average
        elif not same_engraving_process.empty:
            average = ReplicableValue.average(
                same_engraving_process["density"].tolist(),
                name="density",
                unit="GB / cm²",
                source=f"Average density of RAM specs with the same engraving process. Number of values averaged: {len(same_engraving_process)}. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ram_manufacture.csv",
            )

            return average
        else:
            return SourcedValue.from_config("ram_density", config["default_values_ram"]["ram_density"])
