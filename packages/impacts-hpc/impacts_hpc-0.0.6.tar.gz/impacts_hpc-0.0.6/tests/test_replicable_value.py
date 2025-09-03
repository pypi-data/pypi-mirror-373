# ImpactsHPC - Python library designed to estimate the environmental impacts of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import pytest

from impactshpc.src.core.ReplicableValue import SourcedValue
from impactshpc.src.core.config import Q_


def test_conversion_min_max_to_std():
    a = SourcedValue("a", "10 W", min="5 W", max="15W")
    assert a.standard_deviation == Q_("2.5 W")


def test_conversion_std_to_min_max():
    a = SourcedValue("a", "10 W", standard_deviation="2.5 W")
    assert a.min == Q_("5 W")
    assert a.max == Q_("15 W")
