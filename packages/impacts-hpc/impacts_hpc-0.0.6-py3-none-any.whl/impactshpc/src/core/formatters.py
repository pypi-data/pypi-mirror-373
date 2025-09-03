# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from enum import Enum
import json
from typing import List
import platform
import warnings

from pint import Quantity

from impactshpc.src.core.ontology import Ontology

from .config import ureg

from mip._version import __version__ as mip_version
from mip._version import __version_tuple__ as mip_version_tuple


def mip_version_is_adapted_for_mac_os() -> bool:
    """
    Returns True if mip is strictly above 1.14, False either.
    Used because mip <= 1.14 don't work with mac silicon chips.
    """
    if mip_version == "1.16rc0":
        return True

    if int(mip_version_tuple[0]) <= 1 and int(mip_version_tuple[1]) <= 14:
        return False
    return True


MIP_VERSION_IS_ADAPTED_FOR_MAC_OS = mip_version_is_adapted_for_mac_os()
WARNING_MAC_OS = (
    "Some features of pint don't work on mac os "
    "(see https://gitlab.in2p3.fr/impacts-hpc/impacts-hpc/-/issues/1)"
    " due to old version of python-mip package. To get all features,"
    " you can install a pre-release version of mip : `pip install mip==1.16rc0`"
)


def format_reduced(qty: Quantity) -> str:
    """Retourne une version plus lisible de qty."""
    if qty.check("[CO2Mass]") and qty.to("gCO2eq").magnitude > 1e6:
        return f"{round(qty.to("TCO2eq"), 2):~P}"

    if qty.check("[SbMass]") and qty.to("gCO2eq").magnitude > 1e6:
        return f"{round(qty.to("TCO2eq"), 2):~P}"
    if platform.system() == "Darwin" and not MIP_VERSION_IS_ADAPTED_FOR_MAC_OS:
        warnings.warn(WARNING_MAC_OS)
        return f"{round(qty.to_reduced_units().to_compact(), 2):~P}"
    return f"{round(qty.to_reduced_units().to_compact().to_preferred([ureg.Wh]), 2):~P}"


def format_not_reduced(qty: Quantity) -> str:
    """Retourne une version plus lisible de qty."""
    if qty.check("[CO2Mass]") and qty.to("gCO2eq").magnitude > 1e6:
        return f"{round(qty.to("TCO2eq")):~P}"

    if qty.check("[SbMass]") and qty.to("gCO2eq").magnitude > 1e6:
        return f"{round(qty.to("TCO2eq")):~P}"

    if platform.system() == "Darwin" and not MIP_VERSION_IS_ADAPTED_FOR_MAC_OS:
        warnings.warn(WARNING_MAC_OS)
        return f"{round(qty.to_compact(), 2):~P}"
    return f"{round(qty.to_compact().to_preferred([ureg.Wh]), 2):~P}"


class UncertaintyFormat(Enum):
    """The way the uncertainties should be formatted. See :ref:`uncertainty`

    Attributes:
        MIN_MAX = Minimum and maximum values
        STANDARD_DEVIATION = the standard deviation of the
    """

    MIN_MAX = 0
    STANDARD_DEVIATION = 1


class Formatter[T, U](ABC):
    """Abstract class Formatter defines a simple API for formatting the :class:`ReplicableValue` in the :meth:`ReplicableValue.explain` method.

    Formatter uses `Python generics <https://typing.python.org/en/latest/spec/generics.html>`_ for type hinting.

    T is a type, defined by each sub-class of Formatter for the whole subclass.
    For example, in :class:`JSONFormatter`, T is defined as ``dict``.
    :meth:`format_sourced_value` and :meth:`format_operation` must return something of type T. So for :class:`JSONFormatter` their return type is ``dict``.

    U is the :meth:`format_result` return type, it will the type of the output result. For :class:`JSONFormatter`, it's ``str``. Under the hood, :meth:`JSONFormatter.format_sourced_value` and :meth:`JSONFormatter.format_operation` returns
    dicts and :meth:`JSONFormatter.format_result` uses :func:`json.dumps` to convert thoses dicts to JSON.

    Attributes:
        uncertainty_format (UncertaintyFormat, optional): the uncertainty format. See :ref:`uncertainty`. Defaults to UncertaintyFormat.STANDARD_DEVIATION.
    """

    def __init__(self, uncertainty_format: UncertaintyFormat = UncertaintyFormat.STANDARD_DEVIATION) -> None:
        self.uncertainty_format = uncertainty_format

    @abstractmethod
    def format_sourced_value(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> T:
        """Format a :class:`SourcedValue` instance. This method must be implemented.

        Attributes:
            name (str | None): Name of the SourcedValue, if any.
            value (Quantity): The central value, with units.
            min (Quantity): Minimum plausible value.
            max (Quantity): Maximum plausible value.
            standard_deviation (Quantity): Standard deviation (uncertainty) of the value.
            source (str): The source (quote, link, etc.) of the value.
            warnings (List[str]): List of warnings or notes about the value.
            explanation (str | None): Optional explanation or description.
            ontology (str | None): Optional ontology tag for semantic annotation.
            recursion_level (int): Recursion level is the depth of this value in the tree represented by the :class:`ReplicableValue` on which we called :meth:`ReplicableValue.explain`.
            already_seen (bool): Whether the value has already been formatted in a previously traversed branch of the tree represented by the :class:`ReplicableValue` on which we called :meth:`ReplicableValue.explain`. The :meth:`Operation._explain_rec` method uses Depth-First Search and respects the order of the :attr:`Operation.operands` list.
            important (bool): True if the value is an important intermediate result. If true, it will be extracted and passed to :meth:`format_result` in the list of extracted important values.

        Returns:
            T: The formatted :class:`SourcedValue`.
        """

        pass

    @abstractmethod
    def format_operation(
        self,
        formula: str,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        operator: str,
        operands: list[T],
        isInfix: bool,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> T:
        """Format an :class:`Operation` instance. This method must be implemented.

        Args:
            formula (str): A string representing the formula that the :class:`Operation` represents, returned by :meth:`Operation._as_formula`.
            name (str | None): Name of the SourcedValue, if any. It is unique.
            value (Quantity): The central value, with units.
            min (Quantity): Minimum plausible value.
            max (Quantity): Maximum plausible value.
            standard_deviation (Quantity): Standard deviation (uncertainty) of the value.
            operator (str): The operator of this operation.
            operands (list[T]): List of the operands used in this operation, already formatted.
            isInfix (bool): True if the operation is infix (i.e., it's a binary operation and the operator is placed between the operands, like ``A + B``). False if the operation is prefix (i.e., the operation can have any number of parameters and is written as a function, like ``ln(a)``).
            warnings (List[str]): List of warnings or notes about the value.
            explanation (str | None): Optional explanation or description.
            ontology (str | None): Optional ontology tag for semantic annotation.
            recursion_level (int): Recursion level is the depth of this value in the tree represented by the :class:`ReplicableValue` on which we called :meth:`ReplicableValue.explain`.
            already_seen (bool): Whether the value has already been formatted in a previously traversed branch of the tree represented by the :class:`ReplicableValue` on which we called :meth:`ReplicableValue.explain`. The :meth:`Operation._explain_rec` method uses Depth-First Search and respects the order of the :attr:`Operation.operands` list.
            important (bool): True if the value is an important intermediate result. If true, it will be extracted and passed to :meth:`format_result` in the list of extracted important values.

        Returns:
            T: The formatted :class:`Operation`.
        """

        pass

    @abstractmethod
    def format_extracted_important_values(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
    ) -> T:
        """Format extracted values which are the :class:`ReplicableValue` instances with the :attr:`Replicable.important` boolean set to true. These values are extracted and can be used to format the final result in :meth:`format_result`.

        Args:
            name (str | None): Name of the SourcedValue, if any. It is unique.
            value (Quantity): The central value, with units.
            min (Quantity): Minimum plausible value.
            max (Quantity): Maximum plausible value.
            standard_deviation (Quantity): Standard deviation (uncertainty) of the value.
            source (str): The source (quote, link, etc.) of the value.
            warnings (List[str]): List of warnings or notes about the value.
            explanation (str | None): Optional explanation or description.
            ontology (str | None): Optional ontology tag for semantic annotation.

        Returns:
            T: Formatted extracted important source value.
        """
        pass

    @abstractmethod
    def format_result(self, result: T, extracted_important_values: list[T]) -> U:
        """Format the final result. Does nothing by default, but can be overridden to process or modify the final result before :meth:`ReplicableValue.explain` returns it.

        For example, :class:`TextFormatter` overrides :meth:`format_result` in order to add the extracted important values at the beginning of the explanation.
        :class:`JSONFormatter` override :meth:`format_result` to use :func:`json.dumps` on the final dict returned by :meth:`format_operation` and :meth:`format_sourced_value`

        Args:
            result (T): The formatted result of :meth:`ReplicableValue._explain_rec`.
            extracted_important_values (list[T]): The extracted important values. These can be used to add a quick recap of the important results at the beginning of the explanation.

        Returns:
            T: By default, returns the ``result`` parameter as is. Can be overridden to modify the final result before :meth:`ReplicableValue.explain` returns it.
        """
        pass


BOLD = "\033[1m"
RESET_BOLD = "\033[0m"
RED = "\033[31m"
RESET_RED = "\033[0m"


class TextFormatter(Formatter[str, str]):
    def __init__(self, uncertainty_format: UncertaintyFormat = UncertaintyFormat.STANDARD_DEVIATION) -> None:
        super().__init__(uncertainty_format)

    def format_sourced_value(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> str:
        std = f"±{format_not_reduced(standard_deviation)}" if standard_deviation > 0 else ""
        min_max = f" (min = {format_not_reduced(min)}, max = {format_not_reduced(max)})"

        match self.uncertainty_format:
            case UncertaintyFormat.STANDARD_DEVIATION:
                uncertainty = std
            case UncertaintyFormat.MIN_MAX:
                uncertainty = min_max

        if already_seen:
            return f"{' ' * recursion_level}{BOLD}{name}{RESET_BOLD} is {BOLD}{format_not_reduced(value)}{RESET_BOLD}{uncertainty}. See above."

        text = f"{' ' * recursion_level}{BOLD}{name}{RESET_BOLD} is {BOLD}{format_not_reduced(value)}{RESET_BOLD}{uncertainty}"

        if explaination is not None:
            text += f"\n{' ' * recursion_level}{explaination}"

        if len(warnings) > 0:
            for warning in warnings:
                text += f"\n{' ' * recursion_level}WARNING : {warning}"

        if ontology is not None:
            text += f"\n{' ' * recursion_level}{ontology.term}: {ontology.link}"

        text += f"\n{' ' * recursion_level}Source: {source}"
        return text

    def format_operation(
        self,
        formula: str,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        operator: str,
        operands: list[str],
        isInfix: bool,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> str:
        std = f"±{format_reduced(standard_deviation)}" if standard_deviation > 0 else ""
        min_max = f" (min = {format_reduced(min)}, max = {format_reduced(max)})"

        match self.uncertainty_format:
            case UncertaintyFormat.STANDARD_DEVIATION:
                uncertainty = std
            case UncertaintyFormat.MIN_MAX:
                uncertainty = min_max

        if already_seen:
            return f"{' ' * recursion_level}{BOLD}{name}{RESET_BOLD} is {BOLD}{format_reduced(value)}{RESET_BOLD}{uncertainty}. See above."

        text = (
            f"{' ' * recursion_level}{BOLD}{name}{RESET_BOLD} is {BOLD}{format_reduced(value)}{RESET_BOLD}{uncertainty}"
        )

        if explaination is not None:
            text += f"\n{' ' * recursion_level}{explaination}"

        if len(warnings) > 0:
            for warning in warnings:
                text += f"\n{' ' * recursion_level}{BOLD + RED}WARNING : {warning}{RESET_BOLD + RESET_RED}"

        if ontology is not None:
            text += f"\n{' ' * recursion_level}{ontology.term}: {ontology.link}"

        text += f"\n{' ' * recursion_level}Formula: {formula}"
        text += f"\n{' ' * recursion_level}where :"
        text += f"\n{'\n'.join(operands)}"
        return text

    def format_extracted_important_values(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
    ) -> str:
        return f"{name} is {BOLD}{format_reduced(value)}{RESET_BOLD}"

    def format_result(self, result: str, extracted_important_values: list[str]):
        return "\n".join(extracted_important_values) + "\n \n" + result


class JSONFormatter(Formatter[dict, str]):
    def format_sourced_value(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> dict:
        return {
            "name": name,
            "value": format_not_reduced(value),
            "min": format_not_reduced(min),
            "max": format_not_reduced(max),
            "standard_deviation": format_not_reduced(standard_deviation),
            "explainations": explaination,
            "warnings": warnings,
            "ontology": {"term": ontology.term, "link": ontology.link} if ontology is not None else None,
            "source": source,
        }

    def format_operation(
        self,
        formula: str,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        operator: str,
        operands: list[dict],
        isInfix: bool,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> dict:
        return {
            "name": name,
            "value": format_reduced(value),
            "min": format_reduced(min),
            "max": format_reduced(max),
            "standard_deviation": format_reduced(standard_deviation),
            "explainations": explaination,
            "warnings": warnings,
            "formula": formula,
            "ontology": {"term": ontology.term, "link": ontology.link} if ontology is not None else None,
            "isInfix": isInfix,
            "operator": operator,
            "operands": operands,
        }

    def format_extracted_important_values(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
    ) -> dict:
        return {}

    def format_result(self, result: dict, extracted_important_values: List[dict]) -> str:
        return json.dumps(result)


class HTMLFormatter(Formatter[str, str]):
    def __init__(self, uncertainty_format: UncertaintyFormat = UncertaintyFormat.STANDARD_DEVIATION) -> None:
        super().__init__(uncertainty_format)

    def format_sourced_value(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> str:
        warningsHTML = "".join([f"<p><b style='color: red'>{warning}</b></p>" for warning in warnings])
        explaination = f"<p>{explaination}</p>" if explaination else ""
        std = f"±{format_not_reduced(standard_deviation)}" if standard_deviation > 0 else ""
        min_max = f" (min = {format_not_reduced(min)}, max = {format_not_reduced(max)})"
        ontology_html = f"<a href={ontology.link}>{ontology.term}</a>" if ontology is not None else ""

        match self.uncertainty_format:
            case UncertaintyFormat.STANDARD_DEVIATION:
                uncertainty = std
            case UncertaintyFormat.MIN_MAX:
                uncertainty = min_max

        return f"<details><summary>{name} is <b>{format_reduced(value)}</b>{uncertainty}</summary>{warningsHTML}{explaination}{ontology_html}<p>Source : {source}</p></details>"

    def format_operation(
        self,
        formula: str,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        operator: str,
        operands: list[str],
        isInfix: bool,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
        recursion_level: int,
        already_seen: bool,
        important: bool,
    ) -> str:
        warningsHTML = "".join([f"<p><b style='color: red'>{warning}</b></p>" for warning in warnings])
        explaination = f"<p>{explaination}</p>" if explaination else ""
        operands = [f"<li>{operand}</li>" for operand in operands]
        std = f"±{format_reduced(standard_deviation)}" if standard_deviation > 0 else ""
        min_max = f" (min = {format_reduced(min)}, max = {format_reduced(max)})"
        ontology_html = f"<a href={ontology.link}>{ontology.term}</a>" if ontology is not None else ""

        match self.uncertainty_format:
            case UncertaintyFormat.STANDARD_DEVIATION:
                uncertainty = std
            case UncertaintyFormat.MIN_MAX:
                uncertainty = min_max

        return f"<details><summary>{name} is <b>{format_reduced(value)}</b>{uncertainty}</summary><p>Formula : {formula}</p>{warningsHTML}{explaination}{ontology_html}<p>where : </p><ul>{''.join(operands)}</ul></details>"

    def format_extracted_important_values(
        self,
        name: str | None,
        value: Quantity,
        min: Quantity,
        max: Quantity,
        standard_deviation: Quantity,
        source: str,
        explaination: str | None,
        warnings: List[str],
        ontology: Ontology | None,
    ) -> str:
        return ""

    def format_result(self, result: str, extracted_important_values: List[str]) -> str:
        return result
