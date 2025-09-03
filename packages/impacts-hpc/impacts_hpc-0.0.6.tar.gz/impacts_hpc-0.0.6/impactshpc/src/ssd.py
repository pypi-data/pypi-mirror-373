# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


from numpy import insert
import pandas

from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.config import relative_to_absolute_path
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.ontology import ELECTRIC_POWER, EMBODIED_IMPACTS, IDLE_POWER, PEAK_POWER, Ontology
from impactshpc.src.core.utils import config

ssd_manufacture = pandas.read_csv(relative_to_absolute_path(config["csv"]["ssd_manufacture"]))


class SSD(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a RAM stick.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/ssd/

    Attributes:
        size (ReplicableValue | str | None, optional): The :ref:`SSD size`. Defaults to the value in the config file under ``default_values_ssd > size``.
        density (ReplicableValue | str | None, optional): The :ref:`SSD density`. Defaults to an estimation made by :meth:`_estimate_density`.
        manufacturer (str | None, optional): _description_. Defaults to None.
        layers (int | None, optional): _description_. Defaults to None.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
        size: ReplicableValue | str | None = None,
        density: ReplicableValue | str | None = None,
        manufacturer: str | None = None,
        layers: int | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.size = SourcedValue.from_argument("size", size) or SourcedValue.from_config(
            "ssd_size", config["default_values_ssd"]["size"]
        )
        self.manufacturer = manufacturer
        self._surface_impact_factor = Impacts.from_config(
            "surface_impact_factor",
            config["default_values_ssd"]["surface_impact_factor"],
        )
        self._base_impact = Impacts.from_config("base_impact", config["default_values_ssd"]["base_impact"])
        self.layers = layers

        self.density = SourcedValue.from_argument("density", density) or self._estimate_density()

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the SSD.

        The embodied impacts of the SSD are estimated using the formula: ``self._surface_impact_factor * surface + self._base_impact``, where:

        - ``_surface_impact_factor`` is the impact of 1 cm² of SSD. It is defined in the config file under ``default_values_ssd > surface_impact_factor``.
        - ``surface`` is the surface of the SSD estimated from its :attr:`size` and its :attr:`density`.
        - ``_base_impact`` is a constant impact of every SSD  stick, which includes packaging, transport, etc. It is defined in the config file under ``default_values_ssd > base_impact``.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the SSD.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "ssd_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        embodied_impacts = self._surface_impact_factor * (self.size / self.density) + self._base_impact
        embodied_impacts.make_intermediate_result(
            "ssd_embodied_impacts",
            "Embedded impacts of the SSD estimated from its surface in cm², an ratio that gives the impact of a cm² of ssd, plus a base impact constant for all SSD, corresponding to the impact of the transport, packaging etc.",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied_impacts

    def estimate_electric_power(self) -> ReplicableValue | None:
        """SSD electrical consumption is ignored

        Returns:
            ReplicableValue | None: always returns None
        """
        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("ssd_electric_power", ontology=ELECTRIC_POWER)
        return None

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("idle_power", ontology=IDLE_POWER)
            return self.idle_power
        return SourcedValue(
            name="ssd_idle_power", value="0 W", source="SSD static consumption is ignored.", ontology=IDLE_POWER
        )

    def estimate_peak_power(self):
        """Estimate the peak (maximum) `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU when the workload is 100%.

        The CPU's peak instant consumption is estimated using the :meth:`estimate_electric_power` method with a workload of 100%.

        Returns:
            Impact: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.
        """

        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("ssd_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        peak = self.estimate_electric_power()
        if peak is not None:
            peak.make_intermediate_result("ssd_peak_power", ontology=PEAK_POWER)

        return peak

    def _estimate_density(self) -> ReplicableValue:
        """Estimate the :ref:`SSD density` of the RAM stick.

        This estimation uses the :attr:`manufacturer` and the :attr:`layers`. We first average the density of the SSD in the file defined in the config file under ``csv > ssd_manufacture`` that have the same manufacturer and the same number of layers.

        If there are no SSD like that, we average the density of SSD with the same manufacturer. If there are still no matching SSD, we average the density of the SSD with the same number of layers. If no SSD match at all, we return the average density of all SSDs.

        Returns:
            ReplicableValue: The estimated :ref:`RAM density` of the RAM stick.
        """
        # Placeholder logic for density estimation
        same_manufacturer = ssd_manufacture[ssd_manufacture["manufacturer"] == self.manufacturer]
        same_layers = ssd_manufacture[ssd_manufacture["layers"] == self.layers]
        same_manufacturer_and_layers = same_manufacturer[same_manufacturer["layers"] == self.layers]

        if not same_manufacturer_and_layers["density"].empty:
            density = ReplicableValue.average(
                same_manufacturer_and_layers["density"].tolist(),
                name="density",
                unit=" GB / cm²",
                source=f"Average density of SSD specs in our database for the same manufacturer and same number of layers. {len(same_manufacturer_and_layers)} values averaged. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ssd_manufacture.csv",
            )

        elif not same_layers["density"].empty:
            density = ReplicableValue.average(
                same_layers["density"].tolist(),
                name="density",
                unit=" GB / cm²",
                source=f"Average density of SSD specs in our database for the same manufacturer. {len(same_manufacturer)} values averaged. See our database:https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ssd_manufacture.csv",
            )

        elif not same_manufacturer["density"].empty:
            density = ReplicableValue.average(
                same_manufacturer["density"].tolist(),
                name="density",
                unit=" GB / cm²",
                source=f"Average density of SSD specs in our database for the same number of layers. {len(same_layers)} values averaged. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ssd_manufacture.csv",
            )

        else:
            density = ReplicableValue.average(
                ssd_manufacture["density"].tolist(),
                name="density",
                unit=" GB / cm²",
                source=f"Average density of SSD specs in our database. {len(ssd_manufacture)} values averaged. See our database: https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/ssd_manufacture.csv",
            )

        return density
