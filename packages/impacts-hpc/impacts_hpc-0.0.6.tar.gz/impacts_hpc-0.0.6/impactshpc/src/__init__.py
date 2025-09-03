# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from .battery import Battery
from .core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from .cooling import Cooling
from .cpu import CPU, PowerMeasure
from .gpu import GPU
from .job import Job
from .other_components import MotherBoard, Case, CaseType, PowerSupply
from .park import Park, EnergyIntensity
from .ram import RAM
from .server import Server
from .ssd import SSD

__all__ = [
    "Battery",
    "HasConsumptionAndEmbodiedImpacts",
    "Cooling",
    "CPU",
    "PowerMeasure",
    "GPU",
    "Job",
    "MotherBoard",
    "Case",
    "CaseType",
    "PowerSupply",
    "Park",
    "EnergyIntensity",
    "RAM",
    "Server",
    "SSD",
]
