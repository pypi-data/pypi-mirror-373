# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import pytest
from impactshpc import CPU, ExactName, find_close_cpu_model_name
from impactshpc.src.core.ReplicableValue import SourcedValue
from impactshpc.src.core.impacts import Impacts


# ----------- EMBODIED IMPACTS --------------


def test_exact_name_known_and_die_size_in_database():
    cpu = CPU(
        name=ExactName("Intel Xeon E3-1285 v6"),  # in database it's die size is known (160 mm)
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(12.29, rel=0.01)


def test_exact_name_known_but_die_size_not_in_database():
    cpu = CPU(
        name=ExactName("Intel Xeon Gold 5215L"),  # in database it's die size is unknown
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(
        19.41, rel=0.01  # whole database average CPU impact
    )


def test_fuzzy_name_single_match_with_die_size_in_database():
    cpu = CPU(
        name=find_close_cpu_model_name("Intel Xeon Gold 6148F"),
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(22.81, rel=0.01)


def test_fuzzy_name_single_match_but_die_size_not_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon Gold 5218B"))

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(
        19.41, rel=0.01  # whole database average CPU impact
    )


def test_fuzzy_name_multiple_matches_with_die_size_in_database():
    cpu = CPU(
        name=find_close_cpu_model_name("Intel Core i3 Coffee Lake"),
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(11.62, rel=0.01)


def test_fuzzy_name_multiple_matches_but_no_die_size_in_database():
    cpu = CPU(
        name=find_close_cpu_model_name(
            "Intel Core i3-N30X Gracemont Core i3 (Alder Lake-N)"  # two CPU matching : Intel Core i3-N300 and Intel Core i3-N305. Both don't have a die size
        )
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(15.69, rel=0.01)


def test_no_name_and_only_family_known():
    cpu = CPU(cpu_family="Coffee Lake")

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(16.03, rel=0.01)


def test_no_name_but_only_cores_known_and_exact_match():
    cpu = CPU(cores=6)

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(13.47, rel=0.01)


def test_no_name_but_only_cores_known_and_interpolation_required():
    cpu = CPU(cores=7)

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(16.02, rel=0.01)


def test_no_name_both_family_and_cores_known_and_exact_match():
    cpu = CPU(cores=6, cpu_family="Coffee Lake")

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(12.17, rel=0.01)


def test_no_name_both_family_and_cores_known_and_interpolation_required():
    cpu = CPU(cores=7, cpu_family="Coffee Lake")

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(14.66, rel=0.01)


def test_no_name_family_and_cores_unknown():
    cpu = CPU()

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(19.41, rel=0.01)


def test_release_date_known_and_nothing_else():
    cpu = CPU(name=ExactName("test CPU"))

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == pytest.approx(19.41, rel=0.01)


# ----------- INSTANT CONSUMPTION --------------


def test_exact_name_model_range_and_tdp_in_database():
    cpu = CPU(name=ExactName("Ryzen 5 (Zen 2 (Renoir))"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(260, rel=1)


def test_exact_name_model_range_but_not_tdp_in_database():
    cpu = CPU(name=ExactName("Intel Xeon Gold 6138F"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(116, rel=1)


def test_exact_name_tdp_but_not_model_range_in_database():
    cpu = CPU(name=ExactName("Intel Xeon E5-2696 V4"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(153, rel=1)


def test_fuzzy_name_single_match_model_range_and_tdp_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon Platinum 8168"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(209, rel=1)


def test_fuzzy_name_single_match_model_range_but_not_tdp_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon Gold 6138F"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(116, rel=1)


def test_fuzzy_name_single_match_tdp_but_not_model_range_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon E5-2696 V4"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(153, rel=1)


def test_fuzzy_name_multiple_match_model_ranges_and_tdp_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon Gold"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(116, rel=1)


def test_fuzzy_name_multiple_match_model_ranges_but_not_tdp_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon Silver 411X Skylake"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(73, rel=1)


def test_fuzzy_name_multiple_match_tdp_but_not_model_range_in_database():
    cpu = CPU(name=find_close_cpu_model_name("Intel Xeon E5-2696 VX"))

    assert cpu.estimate_electric_power().value.to("W").magnitude == pytest.approx(153, rel=1)


def test_direct_embodied_impacts():
    cpu = CPU(
        embodied_impacts=Impacts(
            {
                "gwp": SourcedValue("CPU embodied impact", "10 kgCO2eq"),
                "adpe": SourcedValue("CPU embodied impact", "10 kgSbeq"),
                "pe": SourcedValue("CPU embodied impact", "10 MJ"),
            }
        )
    )

    assert cpu.estimate_embodied_impacts()["gwp"].value.to("kgCO2eq").magnitude == 10
