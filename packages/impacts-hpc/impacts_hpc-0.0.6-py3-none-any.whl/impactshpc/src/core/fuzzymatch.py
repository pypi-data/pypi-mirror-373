# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, override
from rapidfuzz import process, fuzz

import pandas

from impactshpc.src.core.config import config
from impactshpc.src.core.config import relative_to_absolute_path


@dataclass
class Name(ABC):
    def __str__(self) -> str:
        return ""


@dataclass
class ExactName(Name):
    name: str

    @override
    def __str__(self) -> str:
        return self.name


@dataclass
class FuzzymatchResult(Name, ABC):
    request: str


@dataclass
class FuzzymatchSingleResult(FuzzymatchResult):
    result: str

    @override
    def __str__(self) -> str:
        return self.result


@dataclass
class FuzzymatchMultipleResult(FuzzymatchResult):
    results: List[str]
    threshold: float = 90

    @override
    def __str__(self) -> str:
        if len(self.results) <= 3:
            return f"[{', '.join(self.results)}]_average"
        else:
            return f"[{self.results[0]}, ..., {self.results[2]}]_average"


def match(to_found: str, entries: List[tuple[str, str]], threshold: float = 90) -> FuzzymatchResult | None:
    """
    Perform a fuzzy match on a list of tuple. First element of the tuple is the string to return if the second string matches with `to_found`.
    This method can return zero (None),one (:class:`FuzzymatchSingleResult`) or several matches (:class:`FuzzymatchMultipleResult`).

    Args:
        to_found (str): The user-provided string to match against the CPU descriptions.
        entries (List[tuple[str, str]]): A list of tuples where each tuple contains the original CPU name and its concatenated description.
        threshold (float, optional): The minimum similarity score (0–100) to consider a match. Defaults to 90.

    Returns:
        FuzzymatchResult | None:
            - :class:`FuzzymatchSingleResult` if a single good match is found.
            - :class:`FuzzymatchMultipleResult` if multiple results are above the threshold.
            - `None` if no suitable match is found.
    """
    # Extract only the concatenated strings for matching
    search_space = [concat.lower() for _, concat in entries]
    results = process.extract(to_found.lower(), search_space, scorer=fuzz.token_ratio)
    matches = [r for r in results if r[1] == 100]

    if not matches:
        matches = [r for r in results if r[1] >= threshold]

    if not matches:
        return None

    # Map back the matched strings to the original names
    matched_names = [entries[search_space.index(m[0])][0] for m in matches]

    if len(matched_names) == 1:
        return FuzzymatchSingleResult(request=to_found, result=matched_names[0])
    else:
        return FuzzymatchMultipleResult(request=to_found, results=matched_names)


CPU_entries: List[tuple[str, str]] | None = None


def find_close_cpu_model_name(name: str, threshold: float = 90) -> FuzzymatchResult | None:
    """
    Fuzzymatch search for close CPU model names from a dataset using fuzzy matching on name, code name, and generation.
    This method can return zero (None),one (:class:`FuzzymatchSingleResult`) or several matches (:class:`FuzzymatchMultipleResult`).
    Returns the exact name of the CPU, making it suitable to use with :class:`CPU` class.

    Args:
        name (str): The user input string to search for.
        threshold (float, optional): The minimum similarity score (0–100) to consider a match. Defaults to 90.

    Returns:
        :class:`FuzzymatchResult` | None:
            - :class:`FuzzymatchSingleResult` if a single good match is found.
            - :class:`FuzzymatchMultipleResult` if multiple results are above the threshold.
            - `None` if no suitable match is found.
    """

    global CPU_entries
    if CPU_entries is None:
        df = pandas.read_csv(relative_to_absolute_path(config["csv"]["cpu_specs"]))
        CPU_entries = [
            (
                row["name"],
                " ".join(str(v) for v in [row["name"], row["code_name"], row["generation"]] if pandas.notna(v)),
            )
            for _, row in df.iterrows()
        ]

    return match(name, CPU_entries, threshold)


GPU_entries: List[tuple[str, str]] | None = None


def find_close_gpu_model_name(name: str, threshold: float = 80) -> FuzzymatchResult | None:
    """
    Fuzzymatch search for close GPU model names from a dataset using fuzzy matching on name and variant.
    This method can return zero (None),one (:class:`FuzzymatchSingleResult`) or several matches (:class:`FuzzymatchMultipleResult`).
    Returns the exact name of the GPU, making it suitable to use with :class:`GPU` class.

    Args:
        name (str): The user input string to search for.
        threshold (float, optional): The minimum similarity score (0–100) to consider a match. Defaults to 80.

    Returns:
        :class:`FuzzymatchResult` | None:
            - :class:`FuzzymatchSingleResult` if a single good match is found.
            - :class:`FuzzymatchMultipleResult` if multiple results are above the threshold.
            - `None` if no suitable match is found.
    """

    global GPU_entries
    if GPU_entries is None:
        df = pandas.read_csv(relative_to_absolute_path(config["csv"]["gpu_specs"]))
        GPU_entries = [
            (
                row["name"],
                " ".join(
                    str(v)
                    for v in [
                        row["name"],
                        row["gpu_name"],
                        row["gpu_variant"],
                    ]
                    if pandas.notna(v)
                ),
            )
            for _, row in df.iterrows()
        ]

    return match(name, GPU_entries, threshold)


RAM_entries: List[tuple[str, str]] | None = None


def find_close_ram_manufacturer_name(name: str, threshold: float = 80) -> FuzzymatchResult | None:
    """
    Fuzzymatch search for close RAM manufacturer names from a dataset using fuzzy matching on name, variant and memory size.
    This method can return zero (None),one (:class:`FuzzymatchSingleResult`) or several matches (:class:`FuzzymatchMultipleResult`).
    Returns the exact name of the RAM, making it suitable to use with :class:`RAM` class.

    Args:
        name (str): The user input string to search for.
        threshold (float, optional): The minimum similarity score (0–100) to consider a match. Defaults to 80.

    Returns:
        :class:`FuzzymatchResult` | None:
            - :class:`FuzzymatchSingleResult` if a single good match is found.
            - :class:`FuzzymatchMultipleResult` if multiple results are above the threshold.
            - `None` if no suitable match is found.
    """

    global RAM_entries
    if RAM_entries is None:
        df = pandas.read_csv(relative_to_absolute_path(config["csv"]["ram_manufacture"]))
        RAM_entries = [
            (
                row["manufacturer"],
                row["manufacturer"],
            )
            for _, row in df.iterrows()
            if pandas.notna(row["manufacturer"])
        ]

    return match(name, RAM_entries, threshold)


SSD_entries: List[tuple[str, str]] | None = None


def find_close_ssd_manufacturer_name(name: str, threshold: float = 80) -> FuzzymatchResult | None:
    """
    Fuzzymatch search for close SSD manufacturer names from a dataset using fuzzy matching on name, variant and memory size.
    This method can return zero (None),one (:class:`FuzzymatchSingleResult`) or several matches (:class:`FuzzymatchMultipleResult`).
    Returns the exact name of the SSD, making it suitable to use with :class:`SSD` class.

    Args:
        name (str): The user input string to search for.
        threshold (float, optional): The minimum similarity score (0–100) to consider a match. Defaults to 80.

    Returns:
        :class:`FuzzymatchResult` | None:
            - :class:`FuzzymatchSingleResult` if a single good match is found.
            - :class:`FuzzymatchMultipleResult` if multiple results are above the threshold.
            - `None` if no suitable match is found.
    """

    global SSD_entries
    if SSD_entries is None:
        df = pandas.read_csv(relative_to_absolute_path(config["csv"]["ssd_manufacture"]))
        SSD_entries = [
            (
                row["manufacturer"],
                row["manufacturer"],
            )
            for _, row in df.iterrows()
            if pandas.notna(row["manufacturer"])
        ]

    return match(name, SSD_entries, threshold)
