# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Copyright 2025 Airbus Defence and Space SAS

"""A class to create the Hexaly external function."""

from collections.abc import Iterable

from gemseo.algos.optimization_problem import OptimizationProblem
from numpy import atleast_1d
from numpy import float64
from numpy import full
from numpy import nan
from numpy import ravel


class HexalyFunction:
    """The class used as Hexaly external function."""

    __optimization_problem: OptimizationProblem
    """The optimization problem."""

    __output_variable_names: list[str]
    """The output variable names to consider."""

    __normalize_design_space: bool
    """Whether the design space is normalized."""

    def __init__(
        self,
        optimization_problem: OptimizationProblem,
        normalize_design_space: bool = True,
    ) -> None:
        """
        Args:
            optimization_problem: The optimization problem.
            normalize_design_space: Whether the design space is normalized.
        """  # noqa: D205, D212, D415
        self.__optimization_problem = optimization_problem
        self.__normalize_design_space = normalize_design_space

        self.__output_variable_names = [
            self.__optimization_problem.standardized_objective_name,
            *self.__optimization_problem.constraints.get_names(),
        ]

    @property
    def output_variable_names(self) -> list[str]:
        """The output variable names."""
        return self.__output_variable_names

    def evaluate(self, input_values: Iterable[float]) -> list[float64]:
        """Evaluate the optimization problem.

        Args:
            arg_values: The input values.

        Returns:
            The output values for the Hexaly External Function.
        """
        try:
            outputs = self.__optimization_problem.evaluate_functions(
                atleast_1d(input_values), self.__normalize_design_space
            )[0]

        except ValueError:
            outputs = {}
            for variable_name in self.__output_variable_names:
                # This may raise an error if
                # the dimension was not explicitely declared by GEMSEO,
                # or if the design space has no current value
                # permitting to evaluate the function.
                #
                dimension = self.__optimization_problem.get_function_dimension(
                    variable_name
                )
                outputs[variable_name] = full(dimension, nan)

        # All outputs must be scalar values.
        return [
            x for name in self.__output_variable_names for x in ravel(outputs[name])
        ]
