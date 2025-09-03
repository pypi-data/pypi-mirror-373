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

import pytest
from gemseo.algos.design_space import DesignSpace
from gemseo.algos.optimization_problem import OptimizationProblem
from gemseo.core.mdo_functions.mdo_function import MDOFunction
from gemseo.problems.optimization.power_2 import Power2
from gemseo.problems.optimization.rosenbrock import Rosenbrock
from numpy import array
from numpy import isnan
from numpy import ndarray

from gemseo_hexaly.algos.opt.hexaly._core.hexaly_function import HexalyFunction


@pytest.fixture
def hx_func_rosenbrock_scalar() -> HexalyFunction:
    """The Hexaly Function based on the Rosenbrock problem."""
    return HexalyFunction(Rosenbrock(scalar_var=True), normalize_design_space=False)


@pytest.fixture
def hx_func_power2() -> HexalyFunction:
    """The Hexaly Function based on the Power2 problem."""
    return HexalyFunction(Power2())


@pytest.fixture
def hx_func_knapsack(knapsack_max_items) -> HexalyFunction:
    """The Hexaly Function based on the Knapsack problem."""
    return HexalyFunction(knapsack_max_items)


def test_evaluate(hx_func_rosenbrock_scalar: HexalyFunction) -> None:
    """Test the evaluation of the function."""
    assert hx_func_rosenbrock_scalar.evaluate([0.1, 0]) == [
        pytest.approx(0.82, abs=1e-15)
    ]


@pytest.mark.parametrize(
    ("hx_func_name", "variable_names"),
    [
        ("hx_func_rosenbrock_scalar", ["rosen"]),
        ("hx_func_power2", ["pow2", "ineq1", "ineq2", "eq"]),
        ("hx_func_knapsack", ["-knapsack", "items_surpass"]),
    ],
)
def test_output_variable_names(hx_func_name: str, variable_names, request) -> None:
    """Test the property: `output_variable_names`."""
    hx_func: HexalyFunction = request.getfixturevalue(hx_func_name)
    assert hx_func.output_variable_names == variable_names


class ErrorProblem(OptimizationProblem):
    """Optimization problem raising ValueError.

    The ValueError is raised whenever first component of its vector input is 0.
    """

    def __init__(
        self,
    ) -> None:
        design_space = DesignSpace()
        design_space.add_variable(
            "x", 2, lower_bound=-5.0, upper_bound=5, value=1, type_="integer"
        )

        super().__init__(design_space)
        self.objective = MDOFunction(
            self.__objective_function,
            dim=2,
            name="objective",
            f_type="obj",
            expr="[x[0]-1, x[1]]",
            input_names=["x"],
        )

        self.add_constraint(
            MDOFunction(
                self.__constraint_function,
                dim=1,
                f_type=MDOFunction.ConstraintType.INEQ,
                name="constraint",
                expr="x[0]",
                input_names=["x"],
            )
        )

    def __objective_function(self, x_dv: ndarray) -> ndarray:
        if x_dv[0] == [0]:
            msg = "The first component of x is 0"
            raise ValueError(msg)
        return array([x_dv[0] - 1, x_dv[1]])

    def __constraint_function(self, x_dv: ndarray) -> ndarray:
        return array([x_dv[1]])


def test_value_error_catching() -> None:
    """Test the evaluation of the function when a ``ValueError`` is raised."""
    result = HexalyFunction(ErrorProblem()).evaluate([0, 1])
    assert len(result) == 3
    assert all(isnan(item) for item in result)
