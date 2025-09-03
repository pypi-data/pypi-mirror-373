# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Any
from pint import UnitRegistry
from yaml import safe_load
import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")

_CONFIG_FILE = (
    os.environ["IMPACTHPC_CONFIG_FILE"]
    if "IMPACTHPC_CONFIG_FILE" in os.environ
    else os.path.join(ROOT_DIR, "impactshpc/config.yml")
)

config: dict[str, Any] = safe_load(open(_CONFIG_FILE, "r"))
"""The dict correponding to the YAML config file at _CONFIG_FILE (config.yml)"""


def relative_to_absolute_path(relative: str) -> str:
    return os.path.join(ROOT_DIR, relative)


ureg = UnitRegistry(os.path.join(os.path.dirname(__file__), "units/units.txt"))
"""The Pint UnitRegistry used in ImpactsHPC. Adds the units gCO2eq (and its variant kgCO2eq, mgCO2eq, TCO2eq...), gSebeq (with the same variants) and bytes (B, kB, MB, GB, TB).
"""


Q_ = ureg.Quantity
