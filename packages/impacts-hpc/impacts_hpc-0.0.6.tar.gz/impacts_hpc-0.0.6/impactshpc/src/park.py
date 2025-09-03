# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


from numbers import Number
from typing import List

from dataclasses import dataclass

from impactshpc.src.battery import Battery
from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.cooling import Cooling
from impactshpc.src.core.config import config
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.hasEmbodiedImpact import HasEmbodiedImpacts
from impactshpc.src.core.ontology import (
    ELECTRIC_POWER,
    EMBEDDED_IMPACTS,
    EMBODIED_IMPACTS,
    IDLE_POWER,
    PEAK_POWER,
    USAGE_IMPACTS,
    Ontology,
)
from impactshpc.src.core.utils import (
    energy_intensity_at_location,
)
from impactshpc.src.job import Job
from impactshpc.src.other_components import Case
from impactshpc.src.server import Server


@dataclass
class EnergyIntensity:
    """Environnental impact of 1 kWh of electricty. If you don't know the exact value, you can use the :meth:`at_location` to find the energy intensity in a country or a region.

    Attributes:
        value (Impact): the impact of 1 kWh of electricity.
    """

    value: Impacts

    @staticmethod
    def at_location(location: str):
        """Find the energy intensity at the specify location. ``location`` should be a three letter country code as defined in ISO 3166-1 https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3.

        Args:
            location (str): three letter country code

        Returns:
            _type_: an Impact instance containing the energy intensity at ``location``.
        """
        return EnergyIntensity(value=energy_intensity_at_location(location))


class Cluster:
    def __init__(
        self,
        server_model: Server,
        servers_count: ReplicableValue | str | int | float,
        PUE: ReplicableValue | None = None,
    ):
        self.server_model: Server = server_model
        self.servers_count: ReplicableValue = SourcedValue.from_argument("servers_count", servers_count)
        self.PUE: ReplicableValue = PUE or SourcedValue.from_config("PUE", config["default_values_park"]["PUE"])


class Park(HasConsumptionAndEmbodiedImpacts):
    """
    Represents a park of servers, a datacenter, or an HPC center.

    Attributes:
        embodied_impacts (Impacts | str | None, optional): The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the park. If the value is known, :meth:`estimate_embodied_impacts` returns it, otherwise an estimation is done based on other attributes. Defaults to None.
        clusters (dict[str, Cluster]): A dictionary whose keys are names and values are clusters. Clusters are sets of nodes with the same specifications.
        energy_intensity (EnergyIntensity, optional): Energy intensity of the electrical mix of the region where the park is running. This represents the impacts of producing 1 kWh of electricity. Defaults to the average energy intensity of Europe.
        PUE (ReplicableValue, optional): The `Power Usage Effectiveness <https://en.wikipedia.org/wiki/Power_usage_effectiveness>`_ of the park. This value is overridden by the PUE of the cluster if provided. Defaults to the value in the config file under default_values_park > PUE.
        cooling (Cooling | None, optional): An instance of :class:`Cooling` representing the cooling system. Only used for embodied impacts; consumption is estimated using the PUE. Defaults to an estimation of the cooling power installed based on the servers' consumption.
        batteries (list[Battery] | None, optional): A list of :class:`Battery` instances representing the emergency batteries. Defaults to an estimation based on the server consumption and the time to start the emergency power supply (this duration is defined in the config file under default_values_battery > duration).
    """

    def __init__(
        self,
        clusters: dict[str, Cluster],
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
        energy_intensity: EnergyIntensity | None = None,
        PUE: ReplicableValue | None = None,
        cooling: Cooling | None = None,
        batteries: list[Battery] | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.energy_intensity = energy_intensity or EnergyIntensity.at_location("EEE")
        self.clusters = clusters
        self.PUE = PUE or SourcedValue.from_config("PUE", config["default_values_park"]["PUE"])

        # Ensure all clusters names are unique
        names = self.clusters.keys()
        if len(names) != len(set(names)):
            raise ValueError("All clusters 'name' values must be unique.")

        self.energy_intensity = energy_intensity or EnergyIntensity.at_location("EEE")

        self.cooling = cooling
        self.batteries = batteries
        if self.batteries is not None:
            assert (
                len(self.batteries) > 0
            ), "self.batteries can't be empty. You must provide either a non-empty list of Battery instances or None."

    def servers_power(self) -> ReplicableValue:
        """Estimate the consumption of all servers in the park, without accounting for the PUE.

        Returns:
            ReplicableValue: The sum of the consumptions of the servers in the park.
        """

        powers = []
        for name, cluster in self.clusters.items():
            power = cluster.server_model.estimate_electric_power() * cluster.servers_count
            power.make_intermediate_result(f"{name}_electric_power", ontology=ELECTRIC_POWER)
            powers.append(power)

        total_power = ReplicableValue.sum(powers)

        total_power.make_intermediate_result(
            "whole_park_servers_powers", "Power of the servers of the park", ontology=ELECTRIC_POWER
        )
        return total_power

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the park.

        If :attr:`embodied_impacts` is not None, this method only returns it.

        Otherwise, sums the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the servers in :attr:`clusters`, the :attr:`batteries`, and the :attr:`cooling`.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the park.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                "park_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        servers_consumption = self.servers_power()
        if self.batteries is not None:
            batteries_embodied_impact = Impacts.sum([b.estimate_embodied_impacts() for b in self.batteries])
        else:
            batteries_embodied_impact = Battery(server_consumption=servers_consumption).estimate_embodied_impacts()

        batteries_embodied_impact.make_intermediate_result(
            "batteries_embodied_impact",
            ontology=EMBODIED_IMPACTS,
        )

        servers_embodied_impacts_list = []
        for name, p in self.clusters.items():
            embodied = p.server_model.estimate_embodied_impacts() * p.servers_count
            embodied.make_intermediate_result(
                f"{name}_embodied_impact",
                ontology=EMBODIED_IMPACTS,
            )
            servers_embodied_impacts_list.append(embodied)

        servers_embodied_impacts = Impacts.sum(servers_embodied_impacts_list)
        servers_embodied_impacts.make_intermediate_result(
            "servers_embodied_impact",
            ontology=EMBODIED_IMPACTS,
        )

        cooling = self.cooling or Cooling(cooling_power=servers_consumption)

        total_embodied_impacts = (
            servers_embodied_impacts + batteries_embodied_impact + cooling.estimate_embodied_impacts()
        )
        total_embodied_impacts.make_intermediate_result(
            "park_embodied_impacts",
            ontology=EMBODIED_IMPACTS,
        )

        return total_embodied_impacts

    def estimate_peak_power(self) -> ReplicableValue:
        """Estimate the peak consumption (maximum consumption, when maximal workload) of the park.

        Sums the servers' peak consumptions, multiplied by their PUE.

        Returns:
            ReplicableValue: The peak consumption of the park.
        """
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result("park_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        all_peak_powers = []
        for name, cluster in self.clusters.items():
            cluster_peak_power = (
                cluster.server_model.estimate_peak_power() * cluster.servers_count * (cluster.PUE or self.PUE)
            )
            cluster_peak_power.make_intermediate_result(f"{name}_peak_power_including_PUE", ontology=PEAK_POWER)

            all_peak_powers.append(cluster_peak_power)

        total_peak_power = ReplicableValue.sum(all_peak_powers)
        total_peak_power.make_intermediate_result("park_peak_power", ontology=PEAK_POWER)
        return total_peak_power

    def estimate_idle_power(self) -> ReplicableValue:
        """Estimate the static consumption (when 0% workload) of the park.

        Sums the static consumption of the servers, multiplied by their PUE.

        Returns:
            ReplicableValue: The static consumption of the park.
        """
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result("park_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        all_idle_powers = []
        for name, cluster in self.clusters.items():
            cluster_idle_power = (
                cluster.server_model.estimate_idle_power() * cluster.servers_count * (cluster.PUE or self.PUE)
            )
            cluster_idle_power.make_intermediate_result(f"{name}_idle_power_including_PUE", ontology=IDLE_POWER)

            all_idle_powers.append(cluster_idle_power)

        total_idle_power = ReplicableValue.sum(all_idle_powers)
        total_idle_power.make_intermediate_result("park_idle_power", ontology=IDLE_POWER)
        return total_idle_power

    def estimate_electric_power(self) -> ReplicableValue:
        """Estimate the `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the park.

        Sums the servers' consumption, multiplied by their PUE (the PUE of the cluster if defined, otherwise the park's PUE).

        Returns:
            ReplicableValue: The estimated instant consumption of the park.
        """

        if self.electric_power is not None:
            self.electric_power.make_intermediate_result("park_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        all_consumptions = []
        for name, p in self.clusters.items():
            cluster_power = p.server_model.estimate_electric_power() * p.servers_count * (p.PUE or self.PUE)
            cluster_power.make_intermediate_result(f"{name}_electric_power_including_PUE", ontology=ELECTRIC_POWER)

            all_consumptions.append(cluster_power)

        total_consumption = ReplicableValue.sum(all_consumptions)
        total_consumption.make_intermediate_result("park_electric_power", ontology=ELECTRIC_POWER)
        return total_consumption

    def job_impact(self, job: Job) -> Impacts:
        """Estimate the environmental impact of a job running on this park. This takes into account the impact of the electricity consumption of the job, as well as the embodied impact of the park attributed to this job.

        This includes:

        - The :ref:`embedded impacts` of the servers attributed to the job.
        - The impacts of electricity consumption of the job, based on :attr:`energy_intensity`.
        - The :ref:`embedded impacts` of the batteries, using the :class:`Battery`'s allocation method in addition to an allocation based on the proportion of the total consumption of the park that this job's servers use.
        - The :ref:`embedded impacts` of the cooling, using the :class:`Cooling`'s allocation method in addition to an allocation based on the proportion of the total consumption of the park that this job's servers use.

        Args:
            job (Job): A job running on a cluster of the park. Its cluster must exist in the park.

        Returns:
            Impact: The total impact of the job.
        """
        assert job.cluster_name in self.clusters
        cluster = self.clusters[job.cluster_name]

        job_servers_electric_power = cluster.server_model.estimate_electric_power() * job.nodes_count
        job_servers_electric_power.make_intermediate_result(
            "job_servers_electric_power", "The electric power of the servers used by this job", ontology=ELECTRIC_POWER
        )

        job_electric_power = job_servers_electric_power * (cluster.PUE or self.PUE)
        job_electric_power.make_intermediate_result(
            "job_electric_power",
            "The electric power of the part of park used by this job, estimated as the servers' consumption multiplied by the PUE.",
            ontology=ELECTRIC_POWER,
        )

        servers_consumptions = self.servers_power()
        job_consumption_over_total_servers_consumption = job_servers_electric_power / servers_consumptions

        if self.batteries is not None:
            # If the user defines self.batteries, we attribute part of the park's total battery size that we consider to be 'built for this job'.
            # This proportion is calculated using the battery allocation method and the ratio of the energy consumption of this job to the total energy consumption of the park.
            batteries_embedded_impact = Impacts.sum([b.estimate_embedded_impacts(job.duration) for b in self.batteries])
            batteries_embedded_impact.make_intermediate_result(
                "whole_park_batteries_embedded_impact",
                f"The embodied impacts of the batteries attributed to this job duration ({job.duration}). This value supposes that the whole park is used for this job.",
                ontology=EMBEDDED_IMPACTS,
            )
            batteries_embedded_impact *= job_consumption_over_total_servers_consumption
            batteries_embedded_impact.make_intermediate_result(
                "job_batteries_embedded_impact",
                "Part of the impact of the batteries of the whole park attributed to this job.",
                ontology=EMBEDDED_IMPACTS,
            )
        else:
            # Otherwise, we calculate the impact of the batteries needed to support the consumption of this job during the start-up of the emergency generators.
            batteries_embedded_impact = Battery(server_consumption=job_electric_power).estimate_embedded_impacts(
                job.duration
            )
            batteries_embedded_impact.make_intermediate_result(
                "job_batteries_embedded_impact",
                "Part of the impact of the batteries of the whole park attributed to this job.",
            )

        cooling = self.cooling or Cooling(cooling_power=servers_consumptions)
        cooling_embedded_impact = cooling.embedded_impacts(job.duration)
        cooling_embedded_impact.make_intermediate_result(
            "whole_park_cooling_embedded_impact",
            f"The embodied impacts of the cooling attributed to this job duration ({job.duration}). This value supposes that the whole park is used for this job.",
            ontology=EMBEDDED_IMPACTS,
        )
        cooling_embedded_impact *= job_consumption_over_total_servers_consumption
        cooling_embedded_impact.make_intermediate_result(
            "job_cooling_embedded_impact",
            "Part of the impact of the cooling of the whole park attributed to this job.",
            ontology=EMBEDDED_IMPACTS,
        )

        servers_embeded_impacts = cluster.server_model.estimate_embedded_impacts(job.duration) * job.nodes_count
        servers_embeded_impacts.make_intermediate_result(
            "servers_embeded_impacts", "Servers used by this job embedded impacts"
        )
        job_embedded_impact = servers_embeded_impacts + batteries_embedded_impact + cooling_embedded_impact
        job_embedded_impact.make_intermediate_result(
            "job_embedded_impact",
            ontology=EMBEDDED_IMPACTS,
        )

        job_direct_usage_impact = job_electric_power * job.duration * self.energy_intensity.value
        job_direct_usage_impact.make_intermediate_result(
            "usage_impact", "Usage phase impact, the impact of its energy consumption", ontology=USAGE_IMPACTS
        )

        static_time_attributed_to_job = job.duration * (1 / cluster.server_model.usage_rate) - job.duration
        static_time_attributed_to_job.make_intermediate_result(
            "static_time_attributed_to_job",
        )
        job_embedded_idle_power = (
            static_time_attributed_to_job * cluster.server_model.estimate_idle_power() * (cluster.PUE or self.PUE)
        )
        job_static_impact = job_embedded_idle_power * self.energy_intensity.value
        job_static_impact.make_intermediate_result(
            "job_static_impact",
            f"As the usage rate of this job cluster is {cluster.server_model.usage_rate.value.magnitude * 100}%, it remains unused for part of the time. Consumption while inactive is called static consumption and cannot be attributed to any particular job. Instead, it is distributed among all jobs depending on their duration.",
        )

        total_impact = job_direct_usage_impact + job_embedded_impact + job_static_impact
        total_impact.make_intermediate_result("total_impact")

        return total_impact
