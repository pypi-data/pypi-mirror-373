# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

"""Core classes and functions of ImpactsHPC"""

from .allocation import (
    AllocationMethod,
    naive_allocation,
    decrease_over_time_allocation,
)
from .config import config, ureg
from .dateRange import DateRange
from .formatters import Formatter, TextFormatter, HTMLFormatter, JSONFormatter
from .fuzzymatch import (
    Name,
    ExactName,
    FuzzymatchMultipleResult,
    FuzzymatchResult,
    FuzzymatchSingleResult,
    find_close_cpu_model_name,
    find_close_gpu_model_name,
    find_close_ram_manufacturer_name,
    find_close_ssd_manufacturer_name,
)
from .impacts import Impacts
from .ReplicableValue import ReplicableValue, SourcedValue, Operation, CorrelationMode
from .utils import energy_intensity_at_location

__all__ = [
    "AllocationMethod",
    "naive_allocation",
    "decrease_over_time_allocation",
    "config",
    "ureg",
    "DateRange",
    "Formatter",
    "TextFormatter",
    "HTMLFormatter",
    "JSONFormatter",
    "Name",
    "ExactName",
    "FuzzymatchMultipleResult",
    "FuzzymatchResult",
    "FuzzymatchSingleResult",
    "find_close_cpu_model_name",
    "find_close_gpu_model_name",
    "find_close_ram_manufacturer_name",
    "find_close_ssd_manufacturer_name",
    "Impacts",
    "ReplicableValue",
    "SourcedValue",
    "Operation",
    "CorrelationMode",
    "energy_intensity_at_location",
]
