# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

import csv
from dataclasses import dataclass
from typing import List, Tuple

import pandas
from rapidfuzz import fuzz, process

from impactshpc.src.core.config import config, relative_to_absolute_path
from impactshpc.src.core.impacts import Impacts
from impactshpc.src.core.ReplicableValue import ReplicableValue, SourcedValue

electrical_mix_impacts_headers = list(
    csv.reader(open(relative_to_absolute_path(config["csv"]["electrical_mix_impacts_countries"]["file"])))
)[0]

electrical_mix_impacts: dict = {}
rows = list(csv.reader(open(relative_to_absolute_path(config["csv"]["electrical_mix_impacts_countries"]["file"]))))[2:]
for row in rows:
    impact_name = row[6]
    source = row[3]
    priority = int(row[4])
    country_values = row[7:]

    if impact_name not in electrical_mix_impacts:
        electrical_mix_impacts[impact_name] = {}

    for country_index, value in enumerate(country_values):
        country = electrical_mix_impacts_headers[country_index + 7]
        if value:
            if country not in electrical_mix_impacts[impact_name]:
                electrical_mix_impacts[impact_name][country] = {
                    "value": value,
                    "source": source,
                    "priority": priority,
                }
            else:
                current_entry = electrical_mix_impacts[impact_name][country]
                if priority < current_entry["priority"]:
                    electrical_mix_impacts[impact_name][country] = {
                        "value": value,
                        "source": source,
                        "priority": priority,
                    }


def energy_intensity_at_location(location: str) -> Impacts:
    """
    Get the energy intensity of the electrical mix in a specific location.
    If the location is not found, it returns the energy intensity for the EEE location.
    """
    return Impacts(
        {
            impact: (
                SourcedValue(
                    name=f"{impact}_energy_intensity",
                    value=f"{electrical_mix_impacts[impact][location]["value"]}{config["csv"]["electrical_mix_impacts_countries"]["units"][impact]}",
                    source=f"{impact} impact of a kWh of electricity in {location}. Source : {electrical_mix_impacts[impact][location]['source'] }",
                )
                if location in electrical_mix_impacts[impact]
                # If the location is not found, we fallback on the EEE location
                else SourcedValue(
                    name=f"{impact}_energy_intensity",
                    value=f"{electrical_mix_impacts[impact]["EEE"]["value"]}{config["csv"]["electrical_mix_impacts_countries"]["units"][impact]}",
                    source=f"We couldn't find {impact} impact of a kWh of electricity in {location}, thus we fallback on energy intensity in Europe. Source for {impact} impact in EEE : {electrical_mix_impacts[impact]['EEE']['source'] }",
                )
            )
            for impact in config["impact_indicators"].keys()
        }
    )
