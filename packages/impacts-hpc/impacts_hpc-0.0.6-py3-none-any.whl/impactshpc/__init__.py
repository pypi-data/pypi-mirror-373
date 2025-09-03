# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

__version__ = "0.0.6"

from impactshpc.src.core.ReplicableValue import SourcedValue
from impactshpc.src.core.formatters import TextFormatter, HTMLFormatter, JSONFormatter, UncertaintyFormat
from impactshpc.src.core.config import ureg
from impactshpc.src.cpu import PowerMeasure, CPU
from impactshpc.src.gpu import GPU
from impactshpc.src.server import Server
from impactshpc.src.ram import RAM
from impactshpc.src.job import Job
from impactshpc.src.battery import batteries_impacts
from impactshpc.src.park import Park, Cluster
from impactshpc.src.other_components import HDD, PowerSupply, Case, MotherBoard
from impactshpc.src.core.fuzzymatch import (
    find_close_cpu_model_name,
    find_close_ram_manufacturer_name,
    find_close_ssd_manufacturer_name,
    find_close_gpu_model_name,
    ExactName,
)
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.allocation import naive_allocation, decrease_over_time_allocation
from impactshpc.src.park import EnergyIntensity

#  park_impact, server_impacts, SourcedValue, cpu_impacts, hdd_embodied_impacts, power_supply_embodied_impacts, gpu_impacts, ram_impact, ssd_impacts, decrease_over_time_allocation, case_embodied_impact, TextFormatter
__all__ = [
    "CPU",
    "Server",
    "RAM",
    "Park",
    "HDD",
    "PowerSupply",
    "Case",
    "find_close_cpu_model_name",
    "find_close_gpu_model_name",
    "find_close_ram_manufacturer_name",
    "find_close_ssd_manufacturer_name",
    "ExactName",
    "SourcedValue",
    "PowerMeasure",
    "TextFormatter",
    "HTMLFormatter",
    "JSONFormatter",
    "batteries_impacts",
    "ureg",
    "Cluster",
    "GPU",
    "Job",
    "MotherBoard",
    "Impacts",
    "naive_allocation",
    "decrease_over_time_allocation",
    "UncertaintyFormat",
    "EnergyIntensity",
]
