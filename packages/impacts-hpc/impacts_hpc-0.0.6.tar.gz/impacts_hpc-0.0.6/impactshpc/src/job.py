# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


from numbers import Number
from impactshpc.src.core.config import config
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue


class Job:
    """A class representing a job executed on a :class:`Park`.

    Attributes:
        cluster_name (str): The name of the cluster this job is executed on. Should match one cluster defined in :attr:`Park.clusters`.
        nodes_count (ReplicableValue | str | int | float): The number of nodes used in the cluster by this job.
        duration (ReplicableValue | str): The duration of the job.
        cpu_workload (ReplicableValue | int | float | None, optional): The :ref:`CPU workload` of the CPUs (a number between 0 and 100). Defaults to None.
    """

    def __init__(
        self,
        cluster_name: str,
        servers_count: ReplicableValue | str | int | float,
        duration: ReplicableValue | str,
        cpu_workload: ReplicableValue | str | int | float | None = None,
    ) -> None:
        self.cluster_name = cluster_name
        self.nodes_count = SourcedValue.from_argument("nodes_count", servers_count)
        self.duration = SourcedValue.from_argument("duration", duration)
        self.cpu_workload = (
            SourcedValue.from_argument("cpu_workload", cpu_workload)
            or SourcedValue.from_config("default_workload", config["default_values_cpu"]["workload"]),
        )
