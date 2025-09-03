# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime, timedelta
import warnings
from typing import List

import pandas
from numpy import log, polyfit
from pint import Quantity
from scipy.optimize import curve_fit
from impactshpc.src.core.config import relative_to_absolute_path, config
from impactshpc.src.core.hasConsumptionAndEmbodiedImpacts import HasConsumptionAndEmbodiedImpacts
from impactshpc.src.core.dateRange import DateRange
from impactshpc.src.core.fuzzymatch import (
    Name,
    ExactName,
    FuzzymatchMultipleResult,
    FuzzymatchSingleResult,
)
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import Q_, ReplicableValue, SourcedValue, ureg
from impactshpc.src.core.ontology import ELECTRIC_POWER, EMBODIED_IMPACTS, IDLE_POWER, PEAK_POWER, Ontology

CPU_profiles = pandas.read_csv(relative_to_absolute_path(config["csv"]["cpu_profile"]))
CPUs_specs = pandas.read_csv(relative_to_absolute_path(config["csv"]["cpu_specs"])).drop_duplicates()

ZERO_WORKLOAD = SourcedValue(
    name="zero-workload",
    value="0",
    source="Static instant consumption is the consumption when the workload is 0%.",
)

MAX_WORKLOAD = SourcedValue(
    name="max-workload",
    value="100",
    source="Max workload is 100%",
)


class PowerMeasure:
    def __init__(self, workload_percent: Quantity | str, power: Quantity | str):
        if isinstance(workload_percent, str):
            self.workload_percent = Q_(workload_percent)
        else:
            self.workload_percent = workload_percent

        if isinstance(power, str):
            self.power = Q_(power)
        else:
            self.power = power


class CPU(HasConsumptionAndEmbodiedImpacts):
    """Subclass of :class:`Component` representing a CPU.

    This class uses the same estimation as BoavitzAPI, described in

    ::

        Thibault Simon, David Ekchajzer, Adrien Berthelot, Eric Fourboul, Samuel Rince, et al.. BoaviztAPI: a bottom-up model to assess the environmental impacts of cloud services. HotCarbon’24 - 3rd Workshop on Sustainable Computer Systems, Jul 2024, Santa Cruz, United States. hal-04621947v3"

    See the documentation of BoavitzAPI : https://doc.api.boavizta.org/Explanations/components/cpu/

    Examples:
        .. code-block:: python

            from impacthpc import CPU, ExactName

            impacts = CPU(name=ExactName("Intel Xeon Gold 6248")).estimate_embodied_impacts()

            impacts_climate_change = impacts["gwp"]

            print(impacts_climate_change.explain())

        If you don't know the exact name of you CPU, use :func:`~impacthpc.src.core.fuzzymatch.find_close_cpu_model_name`

        .. code-block:: python

            from impacthpc import CPU, ExactName, find_close_cpu_model_name

            impacts = CPU(name=find_close_cpu_model_name("Intel 6248")).estimate_embodied_impacts()

            impacts_climate_change = impacts["gwp"]

            print(impacts_climate_change.explain())

        Electric power of this cpu :

        .. code-block:: python

            from impacthpc import CPU, ExactName

            power = CPU(name=ExactName("Intel Xeon Gold 6248")).estimate_electric_power()

            print(power.explain())

    Attributes:
        name (Name, optional): The name of a CPU model present in the database. Can be an instance of :class:`ExactName` or the return value of :func:`find_close_cpu_model_name` for fuzzy matching name. Defaults to None.
        tdp (float | None, optional): The `Thermal Design Power <https://en.wikipedia.org/wiki/Thermal_design_power>`_ of the CPU, used to determine the CPU's instantaneous power consumption. Defaults to None.
        model_range (str | None, optional): The model range of the CPU, for example ``EPYC``, ``Athlon X4``, ``Core i5``, ``Xeon Gold``... The supported model ranges are listed in the CSV file at the path defined in the config file under csv > cpu_profile.csv. If :attr:`tdp` or :attr:`power_measures` are provided, model_range will be ignored. Defaults to None.
        power_measures (List[PowerMeasure], optional): Measurements of the CPU's power consumption depending on the workload. Defaults to [].
        die_size (ReplicableValue | None, optional): The surface area of the CPU die. Used to determine the embodied impacts of the CPU. Defaults to None.
        cpu_family (str | None, optional): The family of the CPU. Ignored if the name is provided and the die size is in the database for the CPU name. Defaults to None.
        cores (int | None, optional): The number of physical cores of the CPU. Defaults to None.
        release_date_range (DateRange | None, optional): The date range in which the CPU was released. Used in computations when the exact name of the CPU isn't known and estimations are done with average values. Defaults to the ten last years.

    """

    def __init__(
        self,
        embodied_impacts: Impacts | None = None,
        electric_power: ReplicableValue | str | None = None,
        peak_power: ReplicableValue | str | None = None,
        idle_power: ReplicableValue | str | None = None,
        name: Name | None = None,
        tdp: float | None = None,
        model_range: str | None = None,
        power_measures: List[PowerMeasure] = [],
        die_size: ReplicableValue | str | None = None,
        cpu_family: str | None = None,
        cores: int | None = None,
        release_date_range: DateRange | None = None,
    ):
        super().__init__(
            embodied_impacts,
            electric_power,
            peak_power,
            idle_power,
        )
        self.name = name
        self.tdp = tdp
        self.model_range = model_range
        self.power_measures = power_measures
        self.cpu_family = cpu_family
        self.cores = cores
        self.release_date_range = release_date_range or DateRange(
            start=datetime.now() - timedelta(days=365 * 10),
            end=datetime.now(),
        )
        self._die_size_factor = Impacts.from_config(
            "die_size_impact_factor", config["default_values_cpu"]["die_size_impact_factor"]
        )
        self._base_impact = Impacts.from_config("base_impact", config["default_values_cpu"]["base_impact"])

        self._cpus_matching_by_name = self._get_cpus_matching_by_name()
        self.die_size = SourcedValue.from_argument("die_size", die_size) or self._estimate_die_size()
        self._result_name = str(name) if name is not None else "CPU"
        self._a, self._b, self._c, self._d = self._cpu_profile()

    def estimate_electric_power(
        self,
        workload: ReplicableValue | None = None,
    ) -> ReplicableValue:
        """Estimate the `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.

        CPU electric power is estimated using the formula ``a * ln(b * (workload + c)) + d``, where:

        - :ref:`workload <CPU workload>` is a percentage indicating how much the CPU is being used.
        - a, b, c, and d are parameters estimated using power measurements and TDP.

        These four parameters a, b, c, and d are called the :ref:`CPU profile` and are estimated by the method :meth:`_cpu_profile`.

        Args:
            workload (ReplicableValue, optional): The :arg:`workload` of the CPU, between 0 and 100, as a ReplicableValue. The unit should be dimensionless. Defaults to the value defined in the config file under default_values_cpu > workload.

        Returns:
            ReplicableValue: The estimated instant consumption of the CPU.
        """

        if self.electric_power is not None:
            self.electric_power.make_intermediate_result(
                f"{self._result_name}_electric_power",
                ontology=ELECTRIC_POWER,
            )
            return self.electric_power

        workload = workload or SourcedValue.from_config("default_workload", config["default_values_cpu"]["workload"])
        electric_power = self._a * ReplicableValue.ln(self._b * (workload + self._c)) + self._d
        electric_power.make_intermediate_result(
            f"{self._result_name}_electric_power", override_unit=ureg.watt, ontology=ELECTRIC_POWER
        )
        return electric_power

    def estimate_embodied_impacts(self) -> Impacts:
        """Estimate the `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the CPU.

        CPU embodied impacts are estimated using: ``self._die_size_factor * self.die_size + self._base_impact``, where:

        - ``_die_size_factor`` is the impact of 1 mm² of die. It is defined in the config file under default_values_cpu > die_size_factor.
        - ``die_size`` is the surface of the die in mm², either provided by the user or estimated in :meth:`_estimate_die_size`.
        - ``base_impact`` is the impact of everything that isn't the die in a CPU, and is defined in the config file under default_values_cpu > base_impact.

        Returns:
            Impact: The `embodied impacts <TODO : REPLACE WITH ONTOLOGY OF EMBODIED IMPACT>`_  of the CPU.
        """

        if self.embodied_impacts is not None:
            self.embodied_impacts.make_intermediate_result(
                f"{self._result_name}_embodied_impacts",
                ontology=EMBODIED_IMPACTS,
            )
            return self.embodied_impacts

        embodied_impacts = self._die_size_factor * self.die_size + self._base_impact
        embodied_impacts.make_intermediate_result(
            f"{self._result_name}_embodied_impacts",
            "Embodied impacts of the CPU, estimated from its die surface size and the impact per mm² of die, plus a base impact that corresponds to constant impact of all CPUs, like the alimentation, packaging, transport, etc.",
            ontology=EMBODIED_IMPACTS,
        )

        return embodied_impacts

    def estimate_peak_power(self):
        """Estimate the peak (maximum) `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU when the workload is 100%.

        The CPU's peak instant consumption is estimated using the :meth:`estimate_electric_power` method with a workload of 100%.

        Returns:
            Impact: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.
        """

        if self.peak_power is not None:
            self.peak_power.make_intermediate_result(f"{self._result_name}_peak_power", ontology=PEAK_POWER)
            return self.peak_power

        peak = self.estimate_electric_power(MAX_WORKLOAD)
        peak.make_intermediate_result(f"{self._result_name}_peak_power", ontology=PEAK_POWER)
        return peak

    def estimate_idle_power(self):
        """Estimate the static `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU when the workload is 0%.

        The CPU's static instant consumption is estimated using the :meth:`estimate_electric_power` method with a workload of 0%.

        Returns:
            Impact: The `electric power <TODO : REPLACE WITH ONTOLOGY OF ELECTRIC POWER>`_  of the CPU.
        """
        if self.idle_power is not None:
            self.idle_power.make_intermediate_result(f"{self._result_name}_idle_power", ontology=IDLE_POWER)
            return self.idle_power

        idle = self.estimate_electric_power(ZERO_WORKLOAD)
        idle.make_intermediate_result(f"{self._result_name}_peak_power", ontology=IDLE_POWER)
        return idle

    def _get_cpus_matching_by_name(self) -> pandas.DataFrame:
        """Return a sub-dataframe of ``CPUs_specs`` containing only the row matching :attr:`name`.

        Return an empty dataframe with the same columns as ``CPUs_specs`` if :attr:`name` is None.

        Raises:
            ValueError: :attr:`name` should be an instance of the abstract class :class:`Name` or None. Therefore, it can be an :class:`ExactName`, a :class:`FuzzymatchSingleResult`, a :class:`FuzzymatchMultipleResult`, or None.

        Returns:
            pandas.DataFrame: A sub-dataframe of ``CPUs_specs`` containing only the row matching :attr:`name`.
        """
        match self.name:
            case ExactName(name=exact_name):
                return CPUs_specs[CPUs_specs["name"] == exact_name]
            case FuzzymatchSingleResult(request=req, result=res):
                return CPUs_specs[CPUs_specs["name"] == res]
            case FuzzymatchMultipleResult(request=req, results=res, threshold=th):
                return CPUs_specs[CPUs_specs["name"].isin(res)]
            case None:
                return pandas.DataFrame(
                    columns=[
                        "name",
                        "code_name",
                        "generation",
                        "foundry",
                        "release_date",
                        "frequency",
                        "tdp",
                        "cores",
                        "threads",
                        "transistors",
                        "process_size",
                        "die_size",
                        "io_die_size",
                        "io_process_size",
                        "total_die_size",
                        "total_die_size_source",
                        "manufacturer",
                        "model_range",
                        "source",
                    ]
                )
            case _:
                raise ValueError("Unreachable case reached :/")

    def _estimate_die_size(
        self,
    ) -> ReplicableValue:
        """Estimate the :ref:`die size` of a CPU.

        .. image:: _static/estimate_die_size_schema.svg
        :alt: Schema that explains the logic used in this method

        Returns:
            ReplicableValue: The estimated :ref:`die size`.
        """

        # if cpus_matching_by_name isn't empty we take the mean of its total_die_size column
        if not self._cpus_matching_by_name.empty and not self._cpus_matching_by_name["total_die_size"].isna().all():
            if len(self._cpus_matching_by_name["total_die_size"].notna()) == 1:
                die_size = self._cpus_matching_by_name["total_die_size"].squeeze()
                return SourcedValue(
                    name="die_size",
                    value=f"{die_size} mm²",
                    source=f"Die size of {self._cpus_matching_by_name["name"].squeeze()}" or "",
                )

            else:
                die_size = self._cpus_matching_by_name["total_die_size"].mean()
                return SourcedValue(
                    name="die_size",
                    value=f"{die_size} mm²",
                    source=f"Average die size of {", ".join(self._cpus_matching_by_name['name'].squeeze())}"  # type: ignore
                    or "",
                )

        # Otherwise, we identify the possible families of the cpu
        cpu_families: pandas.Series = (
            pandas.Series([self.cpu_family])
            if self.cpu_family is not None
            else self._cpus_matching_by_name["code_name"]
        )

        # Same thing for cores, we try to find the best value
        if (
            self.cores is None
            and not self._cpus_matching_by_name.empty
            and not self._cpus_matching_by_name["cores"].isna().all()
        ):
            self.cores = round(self._cpus_matching_by_name["cores"].mean())

        family_cpus = CPUs_specs[CPUs_specs["code_name"].isin(cpu_families)]
        if not family_cpus.empty and not family_cpus["total_die_size"].dropna().empty:
            if self.cores:
                same_core_cpus = family_cpus[family_cpus["cores"] == self.cores]
                if not same_core_cpus.empty and not same_core_cpus["total_die_size"].dropna().empty:
                    # Case 1 : We know the CPU family and the number of cores, and some CPUs are matching.
                    # We take the average die size of the CPUs in the same family with the same number of cores.
                    result = ReplicableValue.average(
                        same_core_cpus["total_die_size"].dropna().tolist(),
                        name="die_size",
                        unit="mm²",
                        source=f"Average die size of CPUs in the {self.cpu_family} family with {self.cores} cores. {len(family_cpus)} CPUs averaged. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv",
                    )
                    return result
                else:
                    # Case 2 : no CPU have the exact same number of cores, but we know the family.
                    # We take the linear regression of the die size based on the number of cores.
                    # Filter family_cpus to keep only CPUs where 'release_date' distance to the given release_date is less than 10 years
                    family_cpus_10_year_range = family_cpus[
                        family_cpus["release_date"].apply(
                            lambda d: (
                                self.release_date_range.isInRange(datetime.strptime(d, "%Y-%m-%d"))
                                if pandas.notna(d)
                                else True
                            )
                        )
                    ]
                    result = self._linear_regression_core_to_die_size(family_cpus_10_year_range)
                    result.source = f"No other CPU with the same number of cores has been found in our database, thus we used a linear regression to estimate the die size based on the number of cores of this CPU, and the die sizes/numbers of cores of other CPUs in the same family and with a realease date within a 10 years range from {self.release_date_range}. It is based on {len(family_cpus)} other CPUs. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv"
                    return result
            else:
                # Case 3 : We know the CPU family, but not the number of cores.
                # We take the average die size of the CPUs in the same family.
                result = ReplicableValue.average(
                    family_cpus["total_die_size"].dropna().tolist(),
                    name="die_size",
                    unit="mm²",
                    source=f"Average die size of CPUs in the {self.cpu_family} family. {len(family_cpus)} CPUs averaged. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv",
                )
                return result
        elif self.cores is not None:
            # Case 4 : We know the number of cores, but not the CPU family.
            # We average the die size of all CPUs with the same number of cores and within a 10 year range of the release_date
            same_core_cpus = CPUs_specs[CPUs_specs["cores"] == self.cores]
            same_core_cpus_10years_range = same_core_cpus[
                same_core_cpus["release_date"].apply(
                    lambda d: (
                        self.release_date_range.isInRange(datetime.strptime(d, "%Y-%m-%d")) if pandas.notna(d) else True
                    )
                )
            ]

            if (
                not same_core_cpus_10years_range.empty
                and not same_core_cpus_10years_range["total_die_size"].dropna().empty
            ):
                result = ReplicableValue.average(
                    same_core_cpus_10years_range["total_die_size"].dropna().tolist(),
                    name="die_size",
                    unit="mm²",
                    source=f"Average die size of CPUs with {self.cores} cores and within a 10 years range from {self.release_date_range}. {len(same_core_cpus_10years_range)} CPUs averaged. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv",
                )
                return result
            else:
                # If no CPUs with the same number of cores are found, we use linear regression
                result = self._linear_regression_core_to_die_size(CPUs_specs)
                result.source = f"No other CPU with the same number of cores has been found in our database, thus we used a linear regression to estimate the die size based on the number of cores of this CPU, and the die sizes/numbers of cores of all CPUs. It is based on {len(CPUs_specs)} other CPUs. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv"
                return result
        else:
            # Case 5 : We don't know neither the CPU family nor the number of cores.
            # We take the average die size of all CPUs in CPUs_specs within a 10 year range of release_date.
            cpu_10_years_range = CPUs_specs[
                CPUs_specs["release_date"].apply(
                    lambda d: (
                        self.release_date_range.isInRange(datetime.strptime(d, "%Y-%m-%d")) if pandas.notna(d) else True
                    )
                )
            ]
            result = ReplicableValue.average(
                cpu_10_years_range["total_die_size"].dropna().tolist(),
                name="die_size",
                unit="mm²",
                source=f"Average die size of all CPUs within a 10 years range from {self.release_date_range}. {len(cpu_10_years_range)} CPUs averaged. See our database : https://github.com/Boavizta/boaviztapi/blob/main/boaviztapi/data/crowdsourcing/cpu_specs.csv",
            )
            return result

    def _cpu_profile(
        self,
    ) -> tuple[ReplicableValue, ReplicableValue, ReplicableValue, ReplicableValue]:
        """Estimate the :ref:`profile <CPU profile>` of the CPU.

        CPU energy consumption is estimated using the formula ``a * ln(b * (workload + c)) + d``, where:
        - :ref:`workload <CPU workload>` is a percentage indicating how much the CPU is being used.
        - a, b, c, and d are parameters estimated using power measurements and TDP.

        The CPU profile is the set of these four parameters: a, b, c, and d. This method is used to estimate them.

        If the TDP and/or power measures are known, we use scipy.optimize to find a, b, c, and d values that fit best.
        Otherwise, we use default values for the :attr:`model_range`.

        Returns:
            tuple[ReplicableValue, ReplicableValue, ReplicableValue, ReplicableValue]: The CPU profile consisting of the four parameters a, b, c, and d.
        """

        def logarithmic_model(workload, a, b, c, d):
            return a * log(b * (workload + c)) + d

        cpu_profile: pandas.Series = pandas.Series()
        cpu_profile_source: str = ""

        # If we know model range, we can find the corresponding cpu profile
        if self.model_range:
            cpu_profile: pandas.Series = CPU_profiles[
                CPU_profiles["model_range"] == self.model_range
            ].squeeze()  # type: ignore
            cpu_profile_source = f"CPU profile for the model range provided ({self.model_range})"
        # If we don't know model range but have matching cpus_specs and all cpus_specs["model_range"] are the same, then we use this model range
        if (
            cpu_profile.empty
            and not self._cpus_matching_by_name["model_range"].isna().all()
            and self._cpus_matching_by_name["model_range"].nunique() == 1
        ):
            model_range_value: str = self._cpus_matching_by_name["model_range"].iloc[0]
            cpu_profile: pandas.Series = CPU_profiles[
                CPU_profiles["model_range"] == model_range_value
            ].squeeze()  # type: ignore
            cpu_profile_source = f"CPU profile for the model range provided in cpus_specs ({model_range_value})"
        # Otherwise we fallback on default profile
        if cpu_profile.empty:
            cpu_profile: pandas.Series = CPU_profiles[
                CPU_profiles["model_range"] == config["default_values_cpu"]["cpu_profile"]
            ].squeeze()
            cpu_profile_source = (
                f"CPU profile for the default model range ({config['default_values_cpu']['cpu_profile']})"
            )

        # If TDP isn't provided we remplace it with the mean of the non-NaN TDP of cpus_matching_by_name
        # If cpus_matching_by_name is None or empty or tdp values are unknown, then we TDP stays None
        if (
            self.tdp is None
            and self._cpus_matching_by_name is not None
            and not self._cpus_matching_by_name["tdp"].isna().all()
        ):
            self.tdp = self._cpus_matching_by_name["tdp"].mean()

        tdp_points = (
            [
                PowerMeasure("0 %", f"{self.tdp * 0.12} W"),
                PowerMeasure("10 %", f"{self.tdp * 0.32} W"),
                PowerMeasure("50 %", f"{self.tdp * 0.75} W"),
                PowerMeasure("100 %", f"{self.tdp * 1.02} W"),
            ]
            if self.tdp
            else []
        )

        a: ReplicableValue
        b: ReplicableValue
        c: ReplicableValue
        d: ReplicableValue

        if tdp_points or self.power_measures:
            all_points = tdp_points + self.power_measures
            x = [measure.workload_percent.to("%").magnitude for measure in all_points]
            y = [measure.power.to("W").magnitude for measure in all_points]

            with warnings.catch_warnings(action="ignore"):
                params, _ = curve_fit(
                    logarithmic_model,
                    x,
                    y,
                    p0=cpu_profile[["a", "b", "c", "d"]].tolist(),
                )

            source = ""
            if self.tdp and self.power_measures:
                source = "Logarithmic model fine-tuned using tdp and power measures."
            elif self.tdp:
                source = "Logarithmic model fine-tuned using tdp"
            elif self.power_measures:
                source = "Logarithmic model fine-tuned using power measures"

            a = SourcedValue(name="a", value=f"{params[0]}", source=source)
            b = SourcedValue(name="b", value=f"{params[1]}", source=source)
            c = SourcedValue(name="c", value=f"{params[2]}", source=source)
            d = SourcedValue(name="d", value=f"{params[3]}", source=source)
        else:
            a = SourcedValue(name="a", value=f"{cpu_profile['a']}", source=cpu_profile_source)
            b = SourcedValue(name="b", value=f"{cpu_profile['b']}", source=cpu_profile_source)
            c = SourcedValue(name="c", value=f"{cpu_profile['c']}", source=cpu_profile_source)
            d = SourcedValue(name="d", value=f"{cpu_profile['d']}", source=cpu_profile_source)

        return a, b, c, d

    def _linear_regression_core_to_die_size(self, cpus: pandas.DataFrame) -> SourcedValue:
        """Perform a linear regression on the die sizes and numbers of cores of different CPUs to estimate the die size of the current CPU.

        Args:
            cpus (pandas.DataFrame): A dataframe with at least two columns, "cores" and "total_die_size", which describes CPUs and is used to perform the linear regression.

        Raises:
            ValueError: all pairs of cores and total_die_size in ``cpus`` are (nan, nan).

        Returns:
            SourcedValue: The estimated die size of the CPU.
        """
        # keep only columns cores and total_die_size, if both are defined (not NaN)
        core_die_pairs = cpus[["cores", "total_die_size"]].dropna(subset=["cores", "total_die_size"])
        if core_die_pairs.shape[0] > 0:
            cores_list = core_die_pairs["cores"].tolist()
            die_sizes = core_die_pairs["total_die_size"].tolist()
            regression = polyfit(cores_list, die_sizes, 1)  # Linear regression
            interpolation = round(regression[0] * self.cores + regression[1])
            return SourcedValue(
                "die_size",
                f"{interpolation} mm²",
                f"{min(die_sizes)} mm²",
                f"{max(die_sizes)} mm²",
                source="Linear regression of die size based on the number of cores",
            )
        else:
            raise ValueError("No valid core-die size pairs for regression.")
