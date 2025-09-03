# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.


from datetime import datetime, timedelta

import pandas

from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.config import config, relative_to_absolute_path
from impactshpc.src.core.dateRange import DateRange
from impactshpc.src.core.fuzzymatch import (
    ExactName,
    FuzzymatchMultipleResult,
    FuzzymatchSingleResult,
    Name,
)
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue
from impactshpc.src.core.ontology import ELECTRIC_POWER, EMBODIED_IMPACTS, IDLE_POWER, PEAK_POWER, Ontology
from impactshpc.src.ram import RAM

gpu_specs = pandas.read_csv(relative_to_absolute_path(config["csv"]["gpu_specs"]))


MAX_WORKLOAD = 100


class GPU(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a GPU.

    This class uses the same estimation as MLCA, described in

    ::

        Clément Morand, Anne-Laure Ligozat, Aurélie Névéol. MLCA: a tool for Machine Learning Life Cycle Assessment. 2024 10th International Conference on ICT for Sustainability (ICT4S), Jun 2024, Stockholm, Sweden. pp.227-238, 10.1109/ICT4S64576.2024.00031. hal-04643414"

    See the original implementation made by the authors : https://github.com/blubrom/MLCA/blob/d2d8a42a030ea6259959b7d13a2b8637c8501044/boaviztapi/model/components/component.py#L568C7-L568C19

    Attributes:
        name (Name | None, optional): The name of a GPU model present in the database. Can be an instance of :class:`ExactName` or the return value of :func:`find_close_cpu_model_name` for fuzzy matching the name. Defaults to None.
        tdp (ReplicableValue | None, optional): The `Thermal Design Power <https://en.wikipedia.org/wiki/Thermal_design_power>`_ of the GPU, used to determine the GPU's :ref:`instantaneous power consumption <instant consumption>`. Defaults to None.
        die_size (ReplicableValue | None, optional): The die surface size of the GPU. Defaults to None.
        ram_size (ReplicableValue | None, optional): size of the GPU's embedded RAM. Defaults to None.
        family (str | None, optional): Family of the GPU. Defaults to None.
        release_range (DateRange, optional): A range in which the GPU was released. Defaults to the last ten years.
    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
        name: Name | None = None,
        tdp: ReplicableValue | None = None,
        die_size: ReplicableValue | None = None,
        ram_size: ReplicableValue | None = None,
        ram_density: ReplicableValue | str | None = None,
        family: str | None = None,
        release_range: DateRange | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.name = name
        self.release_range: DateRange = release_range or DateRange(
            start=datetime.now() - timedelta(days=365 * 10), end=datetime.now()
        )

        self.family = family
        self.tdp = tdp
        self._gpus_matching_by_name = self._get_gpus_matching_by_name()
        self._gpus_within_date_range = self._get_gpu_within_date_range()
        self.ram_size = ram_size or self._ram_size()
        self._result_name = str(name) if name is not None else "GPU"
        self.ram_density = SourcedValue.from_argument(f"{self._result_name}_ram_density", ram_density)
        self.die_size = die_size or self._estimate_die_size()

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the GPU.

        GPU embodied impacts are estimated using: ``self._die_size_factor * self.die_size + self._base_impact``, where:
        - ``_die_size_factor`` is the impact of 1 mm² of die. It is defined in the config file under default_values_gpu > die_size_factor.
        - ``die_size`` is the surface of the die in mm², either provided by the user or estimated in :meth:`_estimate_die_size`.
        - ``base_impact`` is the impact of everything that isn't the die in a GPU, and is defined in the config file under default_values_gpu > base_impact.

        To this, we add the RAM impact, estimated using the :class:`RAM` class.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the GPU.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                f"{self._result_name}_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        die_impact_factor = Impacts.from_config(
            "die_impact_factor",
            configEntry=config["default_value_gpu"]["die_impact_factor"],
        )
        base_impact = Impacts.from_config("base_impact", configEntry=config["default_value_gpu"]["base_impact"])

        ram_size = self._ram_size()
        ram = RAM(size=ram_size, density=self.ram_density) if ram_size is not None else RAM()

        gpu_embodied_impact = die_impact_factor * self.die_size + base_impact
        gpu_embodied_impact.make_intermediate_result(
            f"{self._result_name}_without_RAM_embodied_impact",
            f"{self._result_name} embodied impact, computed as the die impact, a base impact ",
            ontology=EMBODIED_IMPACTS,
        )

        total_embodied_impact = gpu_embodied_impact + ram.estimate_embodied_impacts()
        total_embodied_impact.make_intermediate_result(
            f"{self._result_name}_embodied_impact",
            f"{self._result_name} embodied impact, computed as the die impact and a base impact, and its RAM impact",
            ontology=EMBODIED_IMPACTS,
        )

        return total_embodied_impact

    def estimate_electric_power(self, workload: ReplicableValue | int | float | None = None) -> ReplicableValue:
        """Estimate the `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.

        If known, we return the TDP. If it is not known, we average the TDP of the GPUs within the release range. If no GPUs are in the release range, we average all TDPs of GPUs in the database.

        Args:
            workload (ReplicableValue, optional): The :ref:`workload` of the CPU, between 0 and 100, as a ReplicableValue. The unit should be dimensionless. Defaults to the value defined in the config file under default_values_gpu > workload.

        Returns:
            ReplicableValue: The estimated instant consumption of the CPU.
        """

        if self.electric_power is not None:
            self.electric_power.make_intermediate_result(f"{self._result_name}_electric_power", ontology=ELECTRIC_POWER)
            return self.electric_power

        workload = (
            workload
            or SourcedValue.from_argument("workload", workload)
            or SourcedValue.from_config("workload", config["default_value_gpu"]["workload"])
        )

        if self.tdp is not None:
            tdp = self.tdp
        elif not self._gpus_matching_by_name["tdp"].isna().all():
            nb_matching_gpu = len(self._gpus_matching_by_name["tdp"].dropna())
            tdp = SourcedValue(
                name=f"{self._result_name}_tdp",
                value=f"{self._gpus_matching_by_name['tdp'].mean()} W",
                min=f"{self._gpus_matching_by_name['tdp'].min()} W",
                max=f"{self._gpus_matching_by_name['tdp'].max()} W",
                standard_deviation=f"{self._gpus_matching_by_name['tdp'].std(ddof=0)} W",
                source=(
                    f"Thermal Design Power of {self._gpus_matching_by_name[self._gpus_matching_by_name['tdp'].notna()]['name'].squeeze()} from {self._gpus_matching_by_name[self._gpus_matching_by_name['tdp'].notna()]['source'].squeeze()}"
                    if nb_matching_gpu == 1
                    else f"Average TDP of {', '.join(self._gpus_matching_by_name[self._gpus_matching_by_name['tdp'].notna()]['name'].tolist())}"
                ),
            )
        elif not self._gpus_within_date_range["tdp"].isna().all():
            tdp = SourcedValue(
                name=f"{self._result_name}_tdp",
                value=f"{self._gpus_within_date_range['tdp'].mean()} W",
                min=f"{self._gpus_within_date_range['tdp'].min()} W",
                max=f"{self._gpus_within_date_range['tdp'].max()} W",
                standard_deviation=f"{self._gpus_within_date_range['tdp'].std(ddof=0)} W",
                source=f"Average TDP of all GPU within the date range {self.release_range}, {len(self._gpus_within_date_range['tdp'].dropna())} averaged",  # type: ignore
            )
        else:
            tdp = SourcedValue(
                name=f"{self._result_name}_tdp",
                value=f"{gpu_specs['tdp'].mean()} W",
                min=f"{gpu_specs['tdp'].min()} W",
                max=f"{gpu_specs['tdp'].max()} W",
                standard_deviation=f"{gpu_specs['tdp'].std(ddof=0)} W",
                source=f"Average TDP of all GPUs in the database, {len(gpu_specs['tdp'].dropna())} averaged",  # type: ignore
            )

        consumption = (workload / 100) * tdp
        consumption.make_intermediate_result(f"{self._result_name}_electric_power", ontology=ELECTRIC_POWER)
        return consumption

    def estimate_idle_power(self) -> ReplicableValue | None:
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result(f"{self._result_name}_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        idle = self.estimate_electric_power(
            SourcedValue.from_config("idle_workload", config["default_value_gpu"]["idle_workload"])
        )
        idle = idle.make_intermediate_result(f"{self._result_name}_idle_power", ontology=IDLE_POWER)
        return idle

    def estimate_peak_power(self) -> ReplicableValue | None:
        if self.peak_power is not None:
            self.peak_power.make_intermediate_result(f"{self._result_name}_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        peak = self.estimate_electric_power(MAX_WORKLOAD)
        peak.make_intermediate_result(f"{self._result_name}_peak_power", ontology=PEAK_POWER)
        return peak

    def _estimate_die_size(
        self,
    ) -> ReplicableValue:
        """Estimate the die size of the GPU.

        If the user provided :attr:`name`, we try to find in the database if the die size is known for this model.
        If the user provided :attr:`family`, we average the die sizes of GPUs in the same family.
        Otherwise, we return the average die size of all GPUs in the database.

        Returns:
            ReplicableValue: The estimated die size of the GPU.
        """

        if not self._gpus_matching_by_name["gpu_die_size"].isna().all():
            return SourcedValue(
                name=f"{self._result_name}_die_size",
                value=f"{self._gpus_matching_by_name['gpu_die_size'].mean()} mm²",
                min=f"{self._gpus_matching_by_name['gpu_die_size'].min()} mm²",
                max=f"{self._gpus_matching_by_name['gpu_die_size'].max()} mm²",
                standard_deviation=f"{self._gpus_matching_by_name['gpu_die_size'].std(ddof=0)} mm²",
                source=(
                    f"Die size of {self._gpus_matching_by_name['name'].squeeze()}. Source : https://www.techpowerup.com/gpu-specs/"
                    if len(self._gpus_matching_by_name["gpu_die_size"]) == 1
                    else "Average die size of GPUs matching by name. Source : https://www.techpowerup.com/gpu-specs/"
                ),
            )

        same_family_gpus_within_date_range = self._gpus_within_date_range[
            self._gpus_within_date_range["family"] == self.family
        ]
        if not same_family_gpus_within_date_range["gpu_die_size"].isna().all():
            return SourcedValue(
                name=f"{self._result_name}_die_size",
                value=f"{same_family_gpus_within_date_range['gpu_die_size'].mean()} mm²",
                min=f"{same_family_gpus_within_date_range['gpu_die_size'].min()} mm²",
                max=f"{same_family_gpus_within_date_range['gpu_die_size'].max()} mm²",
                standard_deviation=f"{same_family_gpus_within_date_range['gpu_die_size'].std(ddof=0)} mm²",
                source=f"Average die size of all GPUs in database with the same family and within the date range. {len(same_family_gpus_within_date_range)} values averaged.",
            )

        same_family_gpus = gpu_specs[gpu_specs["family"] == self.family]
        if not same_family_gpus["gpu_die_size"].isna().all():
            return SourcedValue(
                name=f"{self._result_name}_die_size",
                value=f"{same_family_gpus['gpu_die_size'].mean()} mm²",
                min=f"{same_family_gpus['gpu_die_size'].min()} mm²",
                max=f"{same_family_gpus['gpu_die_size'].max()} mm²",
                standard_deviation=f"{same_family_gpus['gpu_die_size'].std(ddof=0)} mm²",
                source=f"Average die size of all GPUs in database with the same family. {len(same_family_gpus)} values averaged.",
            )

        return SourcedValue(
            name=f"{self._result_name}_die_size",
            value=f"{gpu_specs['gpu_die_size'].mean()} mm²",
            min=f"{gpu_specs['gpu_die_size'].min()} mm²",
            max=f"{gpu_specs['gpu_die_size'].max()} mm²",
            standard_deviation=f"{gpu_specs['gpu_die_size'].std(ddof=0)} mm²",
            source=f"Average die size of all GPU in database. {len(gpu_specs['gpu_die_size'].dropna())} values averaged.",
        )

    def _get_gpus_matching_by_name(self) -> pandas.DataFrame:
        """Return a sub-dataframe of ``gpu_specs`` containing only the row matching :attr:`name`.

        Return an empty dataframe with the same columns as ``gpu_specs`` if :attr:`name` is None.

        Raises:
            ValueError: :attr:`name` should be an instance of the abstract class :class:`Name` or None. Therefore, it can be an :class:`ExactName`, a :class:`FuzzymatchSingleResult`, a :class:`FuzzymatchMultipleResult`, or None.

        Returns:
            pandas.DataFrame: A sub-dataframe of ``gpu_specs`` containing only the row matching :attr:`name`.
        """

        match self.name:
            case ExactName(name=exact_name):
                return gpu_specs[gpu_specs["name"] == exact_name]
            case FuzzymatchSingleResult(request=req, result=res):
                return gpu_specs[gpu_specs["name"] == res]
            case FuzzymatchMultipleResult(request=req, results=res, threshold=th):
                return gpu_specs[gpu_specs["name"].isin(res)]
            case None:
                return pandas.DataFrame(
                    columns=[
                        "name",
                        "gpu_name",
                        "gpu_variant",
                        "gpu_architecture",
                        "family",
                        "release_date",
                        "tdp",
                        "gpu_process_size",
                        "gpu_die_size",
                        "density",
                        "memory_size",
                        "length",
                        "width",
                        "height",
                        "source",
                    ]
                )
            case _:
                raise ValueError("Unreachable case reached :/")

    def _get_gpu_within_date_range(self) -> pandas.DataFrame:
        """Return a sub-dataframe of ``gpu_specs`` containing only the rows within :attr:`release_range`.

        Returns:
            pandas.DataFrame: A sub-dataframe of ``gpu_specs`` containing only the rows within :attr:`release_range`.
        """

        return gpu_specs[
            gpu_specs["release_date"].apply(
                lambda d: (self.release_range.isInRange(datetime.strptime(d, "%Y-%m-%d")) if pandas.notna(d) else True)
            )
        ]

    def _ram_size(self) -> ReplicableValue | None:
        """Returns the ram size based on the :attr:`name` and the database. If the RAM size isn't in database or :attr:`name` is not knowm, returns None.

        Returns:
            ReplicableValue | None: the ram size based on the :attr:`name` and the database. If the RAM size isn't in database or :attr:`name` is not knowm, returns None.
        """
        if not self._gpus_matching_by_name["memory_size"].isna().all():
            return SourcedValue(
                value=f"{self._gpus_matching_by_name['memory_size'].mean()} GB",
                name="memory_size",
                source=(
                    "Average memory size of given GPUs."
                    if len(self._gpus_matching_by_name["memory_size"].dropna()) > 1
                    else f"{self._gpus_matching_by_name['name'].iloc[0]} memory size"
                ),
            )
        else:
            return None
