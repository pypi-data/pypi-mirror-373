# ImpactsHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactsHPC.
# ImpactsHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactsHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactsHPC. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from functools import reduce
from itertools import chain
from numbers import Number
from typing import Any, List, TypeVar, overload

import numpy
from numpy import log
from pint import Quantity, Unit
from impactshpc.src.core.formatters import Formatter, TextFormatter, format_not_reduced
from impactshpc.src.core.config import Q_, ureg
from dataclasses import dataclass

from impactshpc.src.core.ontology import Ontology


class CorrelationMode(Enum):
    """
    Enumeration representing the correlation mode of a value. See :ref:`uncertainty`.

    Attributes:
        DEPENDENT: Indicates that the value is positively correlated with other variables in the context (correlation = 1).
        INDEPENDENT: Indicates that the value is independent and not affected by other variables in the context (correlation = 0).
    """

    DEPENDENT = "DEPENDENT"
    INDEPENDENT = "INDEPENDENT"


#: In a computation, define which operation is done first. For example, in 3 + 4 * 5, we first do 4 * 5 = 20 and then add 3 to get 23. The `*` has priority over the `+`.
operator_priorities = {
    "+": 1,
    "-": 2,
    "*": 3,
    "/": 4,
}


class ReplicableValue(ABC):
    """
    ReplicableValue is a core class of ImpactsHPC for representing numerical values with associated uncertainties and provenance.
    This class enables the construction of operation trees, where each leaf represents a value (with its minimum, maximum, and standard deviation) and each node represents an operation that produces a result.
    Arithmetic operations between ReplicableValue instances automatically propagate uncertainties according to standard rules (see https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae).
    See :ref:`replicable value explanation`.

    .. image:: _static/tree_operation.png
        :alt: Schema of an operation represented as a tree, where leaves are variables and each node is an operator.

    Attributes:
        correlation_mode (CorrelationMode): (static) Class-level setting for how uncertainties are combined during operations.
        name (str | None): Name of the value, if any.
        value (Quantity): The central value, with units.
        min (Quantity): Minimum plausible value.
        max (Quantity): Maximum plausible value.
        standard_deviation (Quantity): Standard deviation (uncertainty) of the value.
        warnings (List[str]): List of warnings or notes about the value.
        explanation (str | None): Optional explanation or description.
        ontology (str | None): Optional ontology tag for semantic annotation.
        important (bool): True if the value is important. When true, this value is extracted during the explaination process in :meth:`explain`

    Note:
        This class is abstract and should not be instantiated directly. Subclasses must implement :func:`_as_formula` and :func:`explain`. The two subclasses are :class:`SourcedValue` and :class:`Operation`.
    """

    correlation_mode: CorrelationMode = CorrelationMode.INDEPENDENT

    def __init__(
        self,
        name: str | None,
        value: Quantity | str,
        min: Quantity | str | None,
        max: Quantity | str | None,
        standard_deviation: Quantity | str | None = None,
        warnings: List[str] = [],
        explaination: str | None = None,
        ontology: Ontology | None = None,
        important: bool = False,
    ):
        self.name = name
        self.warnings = warnings
        self.explaination = explaination
        self.ontology = ontology
        self.important = important

        if isinstance(value, Q_):
            self.value = value
        elif isinstance(value, str):
            self.value = Q_(value)
        else:
            raise TypeError("value must be a Quantity or a string representing a quantity.")

        if standard_deviation is None:
            self.standard_deviation = None
        elif isinstance(standard_deviation, Q_):
            self.standard_deviation = standard_deviation
        elif isinstance(standard_deviation, str):
            self.standard_deviation = Q_(standard_deviation)
        else:
            raise TypeError("standard_deviation must be a Quantity or a string representing a quantity.")

        if min is None:
            if self.standard_deviation is not None:
                self.min = self.value - 2 * self.standard_deviation
            else:
                self.min = self.value
        elif isinstance(min, Q_):
            self.min = min
        elif isinstance(min, str):
            self.min = Q_(min)
        else:
            raise TypeError("Min must be None, a Quantity or a string representing a quantity.")

        if max is None:
            if self.standard_deviation is not None:
                self.max = self.value + 2 * self.standard_deviation
            else:
                self.max = self.value
        elif isinstance(max, Q_):
            self.max = max
        elif isinstance(max, str):
            self.max = Q_(max)
        else:
            raise TypeError("Max must be None, a Quantity or a string representing a quantity.")

        if self.standard_deviation is None:
            if self.min is not None and self.max is not None:
                self.standard_deviation = (self.max - self.min) / Q_("4")
            else:
                self.standard_deviation = Q_("0") * self.value.units

    @staticmethod
    @contextmanager
    def set_correlation_mode(mode: CorrelationMode):
        """
        Context manager to temporarily set the correlation mode used for arithmetic operations involving ReplicableValue instances.
        ReplicableValue instances represent random variables, where the `value` attribute is the expectation and the `standard_deviation` attribute quantifies uncertainty. When performing arithmetic operations on these values, the standard deviation of the result depends on the correlation between operands. In practice, determining the exact correlation between arbitrary values is often infeasible.

        To address this, ImpactsHPC restricts correlation handling to two modes:
        - Independent (correlation = 0): Standard deviations are combined assuming no correlation.
        - Dependent (correlation = 1): Standard deviations are combined assuming full positive correlation.

        This context manager allows you to specify which correlation mode should be used within a given block of code. For example, when subtracting a value from itself (e.g., `C - C`), the operands are fully correlated, and the standard deviation of the result should be zero. In contrast, when adding unrelated values (e.g., `A + B`), the operands are considered independent.

        Example usage:
        .. code-block:: python

            with ReplicableValue.set_correlation_mode(CorrelationMode.DEPENDENT):
                # Computations here assume full correlation (correlation = 1)
                result = C - C
            # Outside the context, computations assume independence (correlation = 0)
            result2 = A + B

        This approach simplifies the handling of correlations in complex systems, such as server impact computations, by allowing explicit control over correlation assumptions at the group or component level.

        Args:
            mode (CorrelationMode): The correlation mode to use within the context.
        """

        old_mode = ReplicableValue.correlation_mode
        ReplicableValue.correlation_mode = mode
        yield
        ReplicableValue.correlation_mode = old_mode

    @staticmethod
    def _add(a: ReplicableValue | int | float, b: ReplicableValue | int | float) -> ReplicableValue:
        """
        Implements the addition operator for ReplicableValue objects.
        Supports addition with another ReplicableValue, int, or float. If ``other`` is an int or float,
        the value is added to the current value, considering a standard deviation of 0 and the same unit as self.

        Args:
            a (ReplicableValue | int | float): The first operand
            b (ReplicableValue | int | float): The second operand


        Returns:
            ReplicableValue: The result of the addition as a new Operation object.

        Raises:
            NotImplementedError: If the operand type is not supported.
        """

        match a:
            case ReplicableValue():
                a_value = a.value
                a_min = a.min
                a_max = a.max
                a_std = a.standard_deviation
                a_warnings = a.warnings
            case _ if isinstance(a, (float, int)):
                a_value = a
                a_min = a
                a_max = a
                a_std = 0
                a_warnings = []
            case _:
                return NotImplemented

        match b:
            case ReplicableValue():
                b_value = b.value
                b_min = b.min
                b_max = b.max
                b_std = b.standard_deviation
                b_warnings = b.warnings
            case _ if isinstance(b, (float, int)):
                b_value = b
                b_min = b
                b_max = b
                b_std = 0
                b_warnings = []
            case _:
                return NotImplemented

        if ReplicableValue.correlation_mode == CorrelationMode.INDEPENDENT:
            standard_deviation: Quantity = numpy.sqrt(a_std**2 + b_std**2)  # type: ignore
        else:
            standard_deviation: Quantity = numpy.sqrt(
                a_std**2  # type: ignore
                + b_std**2  # type: ignore
                + 2 * a_std * b_std  # type: ignore
            )

        return Operation(
            name=None,
            value=a_value + b_value,  # type: ignore
            min=a_min + b_min,  # type: ignore
            max=a_max + b_max,  # type: ignore
            standard_deviation=standard_deviation,  # type: ignore
            operator="+",
            operands=[a, b],
            warnings=a_warnings + b_warnings,
        )

    def __add__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._add(self, other)

    def __radd__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._add(other, self)

    @staticmethod
    def _sub(a: ReplicableValue | int | float, b: ReplicableValue | int | float) -> ReplicableValue:
        """
        Implements the substraction operator for ReplicableValue objects.
        Supports substraction with another ReplicableValue, int, or float. If ``other`` is an int or float,
        the value is added to the current value, considering a standard deviation of 0 and the same unit as self.

        Args:
            a (ReplicableValue | int | float): The first operand
            b (ReplicableValue | int | float): The second operand


        Returns:
            ReplicableValue: The result of the substraction as a new Operation object.

        Raises:
            NotImplementedError: If the operand type is not supported.
        """

        match a:
            case ReplicableValue():
                a_value = a.value
                a_min = a.min
                a_max = a.max
                a_std = a.standard_deviation
                a_warnings = a.warnings
            case _ if isinstance(a, (float, int)):
                a_value = a
                a_min = a
                a_max = a
                a_std = 0
                a_warnings = []
            case _:
                return NotImplemented

        match b:
            case ReplicableValue():
                b_value = b.value
                b_min = b.min
                b_max = b.max
                b_std = b.standard_deviation
                b_warnings = b.warnings
            case _ if isinstance(b, (float, int)):
                b_value = b
                b_min = b
                b_max = b
                b_std = 0
                b_warnings = []
            case _:
                return NotImplemented

        # See https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae
        if ReplicableValue.correlation_mode == CorrelationMode.INDEPENDENT:
            standard_deviation: Quantity = numpy.sqrt(a_std**2 + b_std**2)  # type: ignore
        else:
            standard_deviation: Quantity = numpy.sqrt(
                a_std**2  # type: ignore
                + b_std**2  # type: ignore
                + 2 * a_std * b_std  # type: ignore
            )

        return Operation(
            name=None,
            value=a_value - b_value,  # type: ignore
            min=a_min - b_min,  # type: ignore
            max=a_max - b_max,  # type: ignore
            standard_deviation=standard_deviation,  # type: ignore
            operator="-",
            operands=[a, b],
            warnings=a_warnings + b_warnings,
        )

    def __sub__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._sub(self, other)

    def __rsub__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._sub(other, self)

    @staticmethod
    def _mul(a: ReplicableValue | int | float, b: ReplicableValue | int | float) -> ReplicableValue:
        """
        Implements the multiplication operator for ReplicableValue objects.
        Supports multiplication with another ReplicableValue, int, or float. If ``other`` is an int or float,
        the value is added to the current value, considering a standard deviation of 0 and the same unit as self.

        Args:
            a (ReplicableValue | int | float): The first operand
            b (ReplicableValue | int | float): The second operand


        Returns:
            ReplicableValue: The result of the multiplication as a new Operation object.

        Raises:
            NotImplementedError: If the operand type is not supported.
        """

        match a:
            case ReplicableValue():
                a_value = a.value
                a_units = a.value.units
                a_min = a.min
                a_max = a.max
                a_std = a.standard_deviation
                a_warnings = a.warnings
            case _ if isinstance(a, (float, int)):
                a_value = a
                a_units = ureg.Unit("")
                a_min = a
                a_max = a
                a_std = 0
                a_warnings = []
            case _:
                return NotImplemented

        match b:
            case ReplicableValue():
                b_value = b.value
                b_units = b.value.units
                b_min = b.min
                b_max = b.max
                b_std = b.standard_deviation
                b_warnings = b.warnings
            case _ if isinstance(b, (float, int)):
                b_value = b
                b_units = ureg.Unit("")
                b_min = b
                b_max = b
                b_std = 0
                b_warnings = []
            case _:
                return NotImplemented

        mini = min(
            a_min * b_min,  # type: ignore
            a_min * b_max,  # type: ignore
            a_max * b_min,  # type: ignore
            a_max * b_max,  # type: ignore
        )

        maxi = max(
            a_min * b_min,  # type: ignore
            a_min * b_max,  # type: ignore
            a_max * b_min,  # type: ignore
            a_max * b_max,  # type: ignore
        )

        # See https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae
        if a_value == 0 or b_value == 0:
            standard_deviation = 0 * a_units * b_units
        else:
            if ReplicableValue.correlation_mode == CorrelationMode.INDEPENDENT:
                standard_deviation: Quantity = numpy.abs(a_value * b_value) * numpy.sqrt(
                    (a_std / a_value) ** 2 + (b_std / b_value) ** 2  # type: ignore
                )
            else:
                standard_deviation: Quantity = numpy.abs(a_value * b_value) * numpy.sqrt(
                    (a_std / a_value) ** 2  # type: ignore
                    + (b_std / b_value) ** 2  # type: ignore
                    + 2 * (a_std * b_std) / (a_value * b_value)  # type: ignore
                )

        return Operation(
            name=None,
            value=a_value * b_value,  # type: ignore
            min=mini,  # type: ignore
            max=maxi,  # type: ignore
            operator="*",
            standard_deviation=standard_deviation,  # type: ignore
            operands=[a, b],
            warnings=a_warnings + b_warnings,
        )

    def __mul__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._mul(self, other)

    def __rmul__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._mul(other, self)

    @staticmethod
    def _div(a: ReplicableValue | int | float, b: ReplicableValue | int | float) -> ReplicableValue:
        """
        Implements the division operator for ReplicableValue objects.
        Supports division with another ReplicableValue, int, or float. If ``other`` is an int or float,
        the value is added to the current value, considering a standard deviation of 0 and the same unit as self.

        Args:
            a (ReplicableValue | int | float): The first operand
            b (ReplicableValue | int | float): The second operand


        Returns:
            ReplicableValue: The result of the division as a new Operation object.

        Raises:
            NotImplementedError: If the operand type is not supported.
        """

        match a:
            case ReplicableValue():
                a_value = a.value
                a_units = a.value.units
                a_min = a.min
                a_max = a.max
                a_std = a.standard_deviation
                a_warnings = a.warnings
            case _ if isinstance(a, (float, int)):
                a_value = a
                a_units = ureg.Unit("")
                a_min = a
                a_max = a
                a_std = 0
                a_warnings = []
            case _:
                return NotImplemented

        match b:
            case ReplicableValue():
                b_value = b.value
                b_units = b.value.units
                b_min = b.min
                b_max = b.max
                b_std = b.standard_deviation
                b_warnings = b.warnings
            case _ if isinstance(b, (float, int)):
                b_value = b
                b_units = ureg.Unit("")
                b_min = b
                b_max = b
                b_std = 0
                b_warnings = []
            case _:
                return NotImplemented

        mini = min(
            a_min / b_min,  #  type: ignore
            a_min / b_max,  #  type: ignore
            a_max / b_min,  #  type: ignore
            a_max / b_max,  #  type: ignore
        )
        maxi = max(
            a_min / b_min,  #  type: ignore
            a_min / b_max,  #  type: ignore
            a_max / b_min,  #  type: ignore
            a_max / b_max,  #  type: ignore
        )

        if a_value == 0 or b_value == 0:
            standard_deviation = 0 * (a_units / b_units)
        else:
            # See https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae
            if ReplicableValue.correlation_mode == CorrelationMode.INDEPENDENT:
                standard_deviation: Quantity = numpy.abs(a_value / b_value) * numpy.sqrt(
                    (a_std / a_value) ** 2 + (b_std / b_value) ** 2  # type: ignore
                )
            else:
                standard_deviation: Quantity = numpy.abs(a_value / b_value) * numpy.sqrt(
                    (a_std / a_value) ** 2  # type: ignore
                    + (b_std / b_value) ** 2  # type: ignore
                    - 2 * (a_std * b_std) / (a_value * b_value)  # type: ignore
                )

        return Operation(
            name=None,
            value=a_value / b_value,  # type: ignore
            min=mini,  # type: ignore
            max=maxi,  # type: ignore
            standard_deviation=standard_deviation,  # type: ignore
            operator="/",
            operands=[a, b],
            warnings=a_warnings + b_warnings,
        )

    def __truediv__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._div(self, other)

    def __rtruediv__(self, other: ReplicableValue | int | float) -> "ReplicableValue":
        return ReplicableValue._div(other, self)

    @staticmethod
    def ln(value: ReplicableValue) -> ReplicableValue:
        """
        Computes the natural logarithm of a value.

        Args:
            value (ReplicableValue): The value for which to compute the natural logarithm.

        Returns:
            ReplicableValue: The result of the natural logarithm as a new Operation object.

        Raises:
            NotImplementedError: If the operand type is not supported.
        """

        # See https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Example_formulae
        standard_deviation = abs(value.standard_deviation / value.value.magnitude)

        return Operation(
            name=None,
            value=log(value.value.magnitude) * ureg.dimensionless,
            min=log(value.min.magnitude) * ureg.dimensionless,
            max=log(value.max.magnitude) * ureg.dimensionless,  # type: ignore
            standard_deviation=standard_deviation,
            operands=[value],
            operator="ln",
            isInfix=False,  # will be printed as "ln(operand)"
        )

    @staticmethod
    def average(values: List[float | int], unit: str, name: str, source: str) -> SourcedValue:
        """
        Computes the average of the list as a SourcedValue.

        - ``value`` is the average of ``values``.
        - ``min`` and ``max`` are the minimum and maximum of ``values``.
        - ``standard_deviation`` is the standard deviation of ``values``.

        Args:
            values (List[float | int]): A list of numeric values to average.
            unit (str): The unit of the values as a string (e.g., "kg", "m"). See :obj:`impacthpc.src.core.config.ureg`
            name (str): The name to associate with the resulting SourcedValue.
            source (str): The source or provenance of the values.

        Returns:
            SourcedValue: An object containing the average, minimum, maximum, and standard deviation of the input values,
            all formatted with the specified unit, along with the provided name and source.

        Raises:
            ValueError: If the input list of values is empty.
        """

        if not values:
            raise ValueError("The list of values must not be empty.")

        average_value = sum(values) / len(values)

        standard_deviation = numpy.sqrt(
            sum((value - average_value) ** 2 for value in values) / len(values),
        )

        return SourcedValue(
            name=name,
            value=f"{average_value} {unit}",
            source=source,
            min=f"{min(values)} {unit}",
            max=f"{max(values)} {unit}",
            standard_deviation=f"{standard_deviation} {unit}",
        )

    @staticmethod
    def sum(values: List[ReplicableValue]) -> ReplicableValue:
        """
        Computes the sum of a list of ReplicableValue using :func:`__add__`, handling duplicates.
        Duplicates are removed:
        ``same_value + other_value + same_value + same_value`` becomes ``other_value + 3 * same_value``.

        Args:
            values (List[ReplicableValue]): The list to sum.

        Returns:
            ReplicableValue: The sum of the ReplicableValue instances in ``values``.
        """

        @dataclass
        class OccurenceEntry:
            replicable_value: ReplicableValue
            occurences: int

        occurences: dict[int, OccurenceEntry] = {}
        for value in values:
            if hash(value) in occurences:
                occurences[hash(value)].occurences += 1
            else:
                occurences[hash(value)] = OccurenceEntry(value, 1)

        terms = []
        for entry in occurences.values():
            match entry.occurences:
                case 0:
                    continue
                case 1:
                    terms.append(entry.replicable_value)
                case _:
                    terms.append(entry.replicable_value * entry.occurences)

        return reduce(lambda x, y: x + y, terms)

    def make_intermediate_result(
        self,
        name: str,
        explaination: str | None = None,
        ontology: Ontology | None = None,
        override_unit: Unit | None = None,
    ):
        """
        Makes this value an intermediate result. This is used in the explain() method.
        For example, if you have the computation ``A + B + C`` that isn't easy to understand, you can decompose it
        with intermediate results by doing:

        .. code-block:: python

            AandB = A + B
            AandB.make_intermediate_result("AandB")
            result = AandB + C
            result.make_intermediate_result("result")

        This will print something like:

        .. code-block::

            result is [some_value]
            Formula = AandB + C
            where
                - AandB is [other value]
                  Formula = A + B
                  where
                    - A is [value]
                    - B is [value]
                - C is [value]

        You can also add an explanation and an ontology to the results, and override its unit.

        Args:
            name (str): The name of the intermediate result that will be displayed by :func:`explain`.
            explanation (str | None, optional): If not None, sets the :attr:`explanation` attribute. Defaults to None.
            ontology (str | None, optional): If not None, sets the :attr:`ontology` attribute. Defaults to None.
            override_unit (Unit | None, optional): If not None, overrides the unit of the result by calling :func:`set_unit`. Defaults to None.
        """

        self.name = name
        self.explaination = explaination
        self.ontology = ontology
        if override_unit is not None:
            self.set_unit(override_unit)

    def set_unit(self, unit: Unit):
        """
        Sets the unit of the value. ImpactsHPC uses the library Pint (https://pint.readthedocs.io/en/stable/) for handling units.

        Args:
            unit (Unit): The new unit. You should use a Unit from :obj:`impacthpc.src.core.config.ureg`.

        Raises:
            ValueError: Raised if the value should be dimensionless to be set but is not.
        """

        if self.value.dimensionless:
            self.value *= unit  # type: ignore
            self.min *= unit  # type: ignore
            self.max *= unit  # type: ignore
            self.standard_deviation *= unit
        else:
            raise ValueError("The value is not dimensionless, so it cannot be converted to a different unit.")

    def __repr__(self) -> str:
        if self.name is not None:
            return self.name

        return self._as_formula()

    @abstractmethod
    def _as_formula(self) -> str:
        """
        Returns a string representing the formula that this ReplicableValue represents.

        See also:
            :func:`SourcedValue._as_formula`
            :func:`Operation._as_formula`
        """

        pass

    def explain[T](
        self,
        formatter: Formatter[Any, T] = TextFormatter(),
    ) -> T:
        """
        Provides an explanation of the current object using the specified formatter.

        Internally calls :func:`_explain_rec` and format the result with :meth:`Formatter.format_result`. It extracts the important values using :meth:`extract_important_values` and pass them to :func:`Formatter.format_result`.

        Args:
            formatter (impacthpc.src.core.formatters.Formatter[T]): The formatter used to format the explanation. Defaults to :class:`TextFormatter <impacthpc.src.core.formatters.TextFormatter>`.
            recursion_level (int, optional): The current recursion depth, used to control nested explanations. Defaults to 0.

        Returns:
            T: The formatted explanation of the object.
        """
        sources: dict[str, SourcedValue] = {}
        match self:
            case SourcedValue():
                sources[self.name] = self  # type: ignore name can't be None for SourcedValue but the IDE thinks it's ReplicableValue.name not SourcedValue.name
            case Operation():
                for extracted in self.extract_important_values():
                    sources[extracted.name] = extracted  # type: ignore name can't be None for SourcedValue but the IDE thinks it's ReplicableValue.name not SourcedValue.name

        # Format the extracted sources and keep only the ones marked as important
        formatted_important_values = {
            name: formatter.format_extracted_important_values(
                name=s.name,
                value=s.value,
                min=s.min,
                max=s.max,
                standard_deviation=s.standard_deviation,
                source=s.source,
                explaination=s.explaination,
                warnings=s.warnings,
                ontology=s.ontology,
            )
            for name, s in sources.items()
            if s.important
        }

        result = self._explain_rec(formatter, recursion_level=0, already_seen_values=set())
        if isinstance(result, list):
            raise ValueError(
                "Can't explain this ReplicableValue because it's not an intermediate result. use make_intermediate_result() to make it an intermediate result."
            )
        return formatter.format_result(result, list(formatted_important_values.values()))

    @abstractmethod
    def _explain_rec[T](
        self,
        formatter: Formatter[Any, T] = TextFormatter(),
        recursion_level: int = 0,
        already_seen_values: set[int] = set(),
    ) -> T | list[T]:
        """
        Recusive method called by :func:`explain` to provides an explanation of the current object using the specified formatter.

        See implementations in:
            - :func:`SourcedValue._explain_rec`
            - :func:`Operation._explain_rec`

        Args:static_usage_attributed_to_job
            formatter (impacthpc.src.core.formatters.Formatter[T]): The formatter used to format the explanation. Defaults to :class:`TextFormatter <impacthpc.src.core.formatters.TextFormatter>`.
            recursion_level (int, optional): The current recursion depth, used to control nested explanations. Defaults to 0.
            already_seen_values (set[int]): A set of hashs of the :class:`ReplicableValue` that have already been traversed when a value is duplicated and present in several branches.

        Returns:
            T: The formatted explanation of the object.
        """
        pass


class SourcedValue(ReplicableValue):
    """
    Subclass of :class:`ReplicableValue` representing a leaf of the tree, as opposed to :class:`Operation`, which represents the composed nodes of a tree.

    In addition to the attributes of ReplicableValue, Operations have an operator and operands and can represent infix operations (like a + b, where the ``+`` operator is between the two operands) or prefix operations (like ln(a), where the operator is a function name before the operands).

    Attributes:
        source (str): The source of this value, for example, a quote from a scientific article.
    """

    def __init__(
        self,
        name: str,
        value: Quantity | str,
        min: Quantity | str | None = None,
        max: Quantity | str | None = None,
        source: str = "No source available",
        standard_deviation: Quantity | str | None = None,
        warnings: List[str] = [],
        explaination: str | None = None,
        ontology: Ontology | None = None,
        important: bool = False,
    ):
        super().__init__(
            name,
            value,
            min,
            max,
            standard_deviation,
            warnings,
            explaination,
            ontology,
            important,
        )
        self.source = source

    @overload
    @staticmethod
    def from_argument(name: str, argument: ReplicableValue | str | int | float) -> ReplicableValue: ...

    @overload
    @staticmethod
    def from_argument(name: str, argument: ReplicableValue | str | int | float | None) -> ReplicableValue | None: ...

    @staticmethod
    def from_argument(name: str, argument: ReplicableValue | str | int | float | None) -> ReplicableValue | None:
        """Creates a :class:`ReplicableValue` from ``argument`` if it is not already one.

        If ``argument`` is a :class:`ReplicableValue`, it is returned as is.
        Otherwise, a new :class:`SourcedValue` is created with the name ``name``, the value ``argument``, and the source ``"Argument"``.
        If ``argument`` is None, returns None.

        Args:
            name (str): The name of the :class:`SourcedValue` created if ``argument`` is not a :class:`ReplicableValue`.
            argument (ReplicableValue | str | int | float): If it's a :class:`ReplicableValue`, it is returned as is.
                If it's a string, a :class:`SourcedValue` is created with this string as the value.
                If it is a number, it is converted into a string (with no unit) and a :class:`SourcedValue` is created.

        Returns:
            ReplicableValue: The resulting :class:`ReplicableValue`.
        """
        match argument:
            case ReplicableValue():
                return argument
            case None:
                return None
            case _ if isinstance(argument, int) or isinstance(argument, float):
                return SourcedValue(name, str(argument), source="Argument")
            case _ if isinstance(argument, str):
                return SourcedValue(name, argument, source="Argument")

    @staticmethod
    def from_config(name: str, configEntry: dict[str, Any]) -> SourcedValue:
        """Create a SourcedValue from an entry of :obj:`impacthpc.src.core.config.config`

        Example use :

        .. code-block:: python

            SourcedValue.from_config("lifetime", config["default_values_ram"]["lifetime"])

        Args:
            name (str): the name of the SourcedValue created
            configEntry (dict[str, Any]): a config entry
        """
        return SourcedValue(
            name=name,
            value=configEntry["value"],
            source=configEntry.get("source", "No source available"),
            min=configEntry.get("min", None),
            max=configEntry.get("max", None),
            standard_deviation=configEntry.get("standard_deviation", None),
            explaination=configEntry.get("explaination", None),
            ontology=Ontology.from_config(configEntry.get("ontology", None)),
            important=True,
        )

    def _as_formula(self) -> str:
        """Returns a string representing the formula this ReplicableValue represents.

        For SourcedValue, returns the :attr:`SourcedValue.name` of the Sourcedvalue or a string representation
        of its value if name is None.
        """
        return self.name if self.name is not None else f"{format_not_reduced(self.value)}"

    def _explain_rec[T](
        self,
        formatter: Formatter[Any, T] = TextFormatter(),
        recursion_level: int = 0,
        already_seen_values: set[int] = set(),
    ) -> T:
        """Provides an explanation of the current object using the specified formatter.
        Calls the :func:`Formatter.format_sourced_value` of ``formatter`` and return its results.

        Args:
            formatter (Formatter[T], optional): The formatter used to format the explanation. Defaults to :class:`TextFormatter <impacthpc.src.core.formatters.TextFormatter>`.
            recursion_level (int, optional): The current recursion depth, used to control nested explanations . Defaults to 0.

        Returns:
            T: the resutl returned by :func:`Formatter.format_sourced_value`
        """

        already_seen = hash(self) in already_seen_values
        already_seen_values.add(hash(self))

        return formatter.format_sourced_value(
            name=self.name,
            value=self.value,
            min=self.min,
            max=self.max,
            standard_deviation=self.standard_deviation,
            source=self.source,
            explaination=self.explaination,
            warnings=self.warnings,
            ontology=self.ontology,
            recursion_level=recursion_level,
            already_seen=already_seen,
            important=self.important,
        )


class Operation(ReplicableValue):
    """
    Subclass of :class:`ReplicableValue` representing the composed nodes of a tree, as opposed to :class:`SourcedValue`, which represents the leaf of the tree.

    In addition to the attributes of ReplicableValue, Operations have an operator and operands and can represent infix operations (like a + b, where the ``+`` operator is between the two operands) or prefix operations (like ln(a), where the operator is a function name before the operands).

    Attributes:
        operator (str): The operator of this operation.
        operands (List[ReplicableValue | int | float]): The list of operands. Operands can be ReplicableValues or numbers (int or float). Numbers are treated as if min = max = value, and standard_deviation = 0.
        isInfix (bool): ``True`` if the operation is infix (like a + b, where the ``+`` operator is between the two operands), ``False`` if it is prefix (like ln(a), where the operator is a function name before the operands).
    """

    def __init__(
        self,
        name: str | None,
        value: Quantity | str,
        min: Quantity | str | None,
        max: Quantity | str | None,
        operator: str,
        operands: list[ReplicableValue | int | float],
        isInfix: bool = True,
        standard_deviation: Quantity | str | None = None,
        warnings: List[str] = [],
        explaination: str | None = None,
        ontology: Ontology | None = None,
        important: bool = False,
    ):
        super().__init__(
            name,
            value,
            min,
            max,
            standard_deviation,
            warnings,
            explaination,
            ontology,
            important,
        )
        if isInfix:
            assert len(operands) == 2, "Infix operations must have exactly two operands."

        self.operator = operator
        self.operands = operands
        self.isInfix = isInfix

    def _as_formula(self) -> str:
        """
        Returns a string representing the formula that this ReplicableValue represents.

        For each operand, it is converted to a string (see :func:`ReplicableValue.__repr__`). If the operand is an intermediate result (i.e., it has a name, see :func:`ReplicableValue.make_intermediate_result`), it will return its name; otherwise, it will recursively call its :func:`ReplicableValue._as_formula` method.

        The decision to parenthesize an operand is based on the following rule:
        If an operand is not an intermediate result and it is an Operation (i.e., its string representation will be a formula), then we examine its operator. If this operator has a higher priority than ``self.operator`` according to :obj:`operator_priorities`, we parenthesize the operand. Otherwise, we do not.

        Returns:
            str: A string representing the formula that this ReplicableValue represents.
        """

        if not self.isInfix:
            operands = [str(operand) for operand in self.operands]
            return f"{self.operator}({','.join(operands)})"
        else:
            left = self.operands[0]
            right = self.operands[1]

            should_parenthesize_left = False
            should_parenthesize_right = False
            if isinstance(left, Operation) and left.isInfix and left.name is None:
                should_parenthesize_left = operator_priorities[left.operator] < operator_priorities[self.operator]
            if isinstance(right, Operation) and right.isInfix and right.name is None:
                should_parenthesize_right = operator_priorities[right.operator] < operator_priorities[self.operator]

            left = f"({left})" if should_parenthesize_left else left
            right = f"({right})" if should_parenthesize_right else right
            return f"{left} {self.operator} {right}"

    def _explain_rec[T](
        self,
        formatter: Formatter[Any, T] = TextFormatter(),
        recursion_level: int = 0,
        already_seen_values: set[int] = set(),
    ) -> T | list[T]:
        """
        Provides an explanation of the current object using the specified formatter. Uses a Depth-first search algorithm, and respect the order of the :attr:`operands` list.

        First, it calls the :func:`ReplicableValue._explain_rec` method on each of its operands. Then, it flattens the list of operands' operands to obtain the list of ReplicableValues used to compute this result.

        If the current object is an intermediate result (i.e., it has a name, see :func:`ReplicableValue.make_intermediate_result`), it calls :func:`Formatter.format_operation` with the created list.

        Otherwise, if it is not an intermediate result, it simply returns this list as is.

        For example, suppose that ``self.operator`` is "+" and ``self.operands`` is ``[A, B]``, where A and B are two ReplicableValues. If ``self.name`` is not None, then this Operation is an intermediate result. We call ``A.explain()`` and ``B.explain()``.

        Let's say A is a SourcedValue, so ``A.explain()`` returns something of the formatter's type, while ``B.explain()`` is an operation that isn't an intermediate result. Thus, ``B.explain()`` returns a list of ReplicableValues. Suppose it returns a list of two SourcedValues. We create a 3-element list with the return value of A and the two operands of B, and we pass it to :func:`Formatter.format_operation`.

        If ``self.name`` had been None, then this Operation would not be an intermediate result, and thus we would have just returned the 3-element list as is.

        Args:
            formatter (Formatter, optional): The formatter used to format the explanation. Defaults to :class:`TextFormatter <impacthpc.src.core.formatters.TextFormatter>`.
            recursion_level (int, optional): The current recursion depth, used to control nested explanations. Defaults to 0.

        Returns:
            Union[T, List[T]]: The formatted explanation of the object or a list of formatted explanations.
        """

        already_seen = hash(self) in already_seen_values
        already_seen_values.add(hash(self))

        operands: list[T] = []
        for operand in _remove_duplicates(self.operands):
            if isinstance(operand, (int, float)):
                continue

            sub = operand._explain_rec(
                formatter,
                recursion_level + (4 if self.name else 0),
                already_seen_values=already_seen_values,
            )
            if isinstance(sub, list):
                operands.extend(sub)
            else:
                operands.append(sub)

        if self.name is None:
            return operands
        else:
            return formatter.format_operation(
                formula=self._as_formula(),
                name=self.name,
                value=self.value,
                min=self.min,
                max=self.max,
                standard_deviation=self.standard_deviation,  # type: ignore
                operator=self.operator,
                operands=operands,
                isInfix=self.isInfix,
                explaination=self.explaination,
                warnings=self.warnings,
                ontology=self.ontology,
                recursion_level=recursion_level,
                already_seen=already_seen,
                important=self.important,
            )

    def extract_important_values(self) -> list[SourcedValue]:
        """Returns a list of the SourcedValues (leaves) used in the computation.

        Recursively calls :func:`extract_sourced_values` on each operand.
        """
        sourced_values = []
        for operand in self.operands:
            match operand:
                case SourcedValue():
                    sourced_values.append(operand)
                case Operation(important=important):
                    if important:
                        sourced_values.append(operand)
                    sourced_values.extend(operand.extract_important_values())

        return sourced_values


def _remove_duplicates[T](lst: list[T]) -> list[T]:
    """Remove duplicates and preserve the order

    Returns:
        list[T]: deduplicated list
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
