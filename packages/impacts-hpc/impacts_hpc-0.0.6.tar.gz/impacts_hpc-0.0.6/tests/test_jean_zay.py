# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


from impactshpc import (
    Park,
    Cluster,
    SourcedValue,
    Server,
    CPU,
    RAM,
    find_close_cpu_model_name,
    find_close_gpu_model_name,
    MotherBoard,
    GPU,
    ExactName,
    Job,
)
import pytest


def test_jean_zay():
    jean_zay = Park(
        clusters={
            "cpu_p1": Cluster(
                servers_count=SourcedValue(name="cpu_p1_servers_count", value="720", source="User input"),
                server_model=Server(
                    components=[
                        (CPU(name=find_close_cpu_model_name("Intel 6248")), 2),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="192 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (MotherBoard(), 1),
                    ],
                ),
            ),
            "gpu_p2s": Cluster(
                servers_count=SourcedValue(name="gpu_p2s_servers_count", value="20", source="User input"),
                server_model=Server(
                    components=[
                        (CPU(name=find_close_cpu_model_name("Intel 6248")), 2),
                        (
                            GPU(name=find_close_gpu_model_name("Nvidia Tesla V100 SXM2 32Go")),
                            8,
                        ),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="384 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
            "gpu_p2l": Cluster(
                servers_count=SourcedValue(name="gpu_p2l_servers_count", value="11", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=find_close_cpu_model_name("Intel 6248")), 2),
                        (
                            GPU(name=find_close_gpu_model_name("Nvidia Tesla V100 SXM2 32Go")),
                            8,
                        ),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="768 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
            "gpu_p5": Cluster(
                servers_count=SourcedValue(name="gpu_p5_servers_count", value="52", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=ExactName("AMD EPYC 7543")), 2),
                        (GPU(name=ExactName("NVIDIA A100 SXM4 80 GB")), 8),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="512 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
            "gpu_p6": Cluster(
                servers_count=SourcedValue(name="gpu_p6_servers_count", value="364", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=ExactName("Intel Xeon Platinum 8468")), 2),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="512 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (GPU(name=ExactName("NVIDIA H100 SXM5")), 4),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
            "prepost": Cluster(
                servers_count=SourcedValue(name="prepost_servers_count", value="4", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=ExactName("Intel Xeon Gold 6132")), 2),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="3 TB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (
                            GPU(name=find_close_gpu_model_name("Nvidia Tesla V100")),
                            4,
                        ),  # in the spec, we don't know the exact variant of Nvidia V100 used, so we can use find_close_gpu_model_name result and it will average the matching GPUs
                        (MotherBoard(), 1),
                    ],
                ),
            ),
            "visu": Cluster(
                servers_count=SourcedValue(name="visu_servers_count", value="5", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=ExactName("Intel Xeon Gold 6248")), 2),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="192 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (GPU(name=ExactName("Nvidia Quadro P6000")), 4),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
            "compil": Cluster(
                servers_count=SourcedValue(name="compil_servers_count", value="3", source="User Input"),
                server_model=Server(
                    components=[
                        (CPU(name=ExactName("Intel Xeon Silver 4114")), 2),
                        (
                            RAM(
                                size=SourcedValue(
                                    name="ram_size",
                                    value="96 GB",
                                    source="User Input",
                                )
                            ),
                            1,
                        ),
                        (GPU(name=ExactName("Nvidia Quadro P6000")), 4),
                        (MotherBoard(), 1),
                    ]
                ),
            ),
        },
    )

    result = jean_zay.job_impact(
        Job(
            cluster_name="gpu_p2s",
            servers_count=SourcedValue(value="10", name="nodes count"),
            duration=SourcedValue(value="10 h", name="Duration"),
        )
    )["gwp"]

    print(result.explain())

    assert result.value.to("kgCO2eq").magnitude == pytest.approx(36.04, rel=0.01)
