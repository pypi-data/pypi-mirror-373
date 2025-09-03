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

from typing import Optional
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from gemseo import execute_algo
from gemseo.problems.optimization.power_2 import Power2
from gemseo.problems.optimization.rosenbrock import Rosenbrock
from gemseo_optimization_problems.analytic_bivariate_quadratic import (
    AnalyticBivariateQuadratic,
)
from numpy import allclose

from gemseo_hexaly.algos.opt.hexaly._core.hexaly_callback import HexalyCallback
from gemseo_hexaly.algos.opt.hexaly.hexaly import HexalyOpt
from tests import SKIP_LICENSE


@SKIP_LICENSE
@pytest.mark.parametrize(
    ("opt_problem_class", "problem_options", "max_iter"),
    [
        (Power2, {}, 200),
        (Rosenbrock, {"scalar_var": True}, 5_300),
        (Rosenbrock, {}, 5_300),
        (AnalyticBivariateQuadratic, {}, 10),
    ],
)
def test_execute_multi_problems(opt_problem_class, problem_options, max_iter):
    """Test the use of a Hexaly model."""
    optimization_problem = opt_problem_class(**problem_options)
    expected_x, expected_f = optimization_problem.get_solution()
    output = execute_algo(
        optimization_problem,
        "opt",
        algo_name="HEXALY",
        max_iter=max_iter,
        normalize_design_space=True,
        activate_surrogate=False,
    )

    if not optimization_problem.minimize_objective:
        expected_f = -expected_f

    assert allclose(output.f_opt, expected_f, atol=1e-2)
    assert allclose(
        output.x_opt,
        expected_x,
        atol=1e-2,
    )


@SKIP_LICENSE
@pytest.mark.parametrize("normalize_design_space", [True, False])
@pytest.mark.parametrize(("activate_surrogate", "max_time"), [(True, 5), (False, 0.0)])
@pytest.mark.parametrize("warm_start", [True, False])
@pytest.mark.parametrize("callback", [None, HexalyCallback()])
def test_execute_multi_parameters(
    normalize_design_space: bool,
    activate_surrogate: bool,
    max_time: float,
    warm_start: bool,
    callback: Optional[HexalyCallback],
):
    """Test the execution of Hexaly as a Gemseo library."""
    problem = Power2()
    x_sol, f_sol = problem.get_solution()
    out = execute_algo(
        problem,
        "opt",
        algo_name="HEXALY",
        normalize_design_space=normalize_design_space,
        activate_surrogate=activate_surrogate,
        max_time=max_time,
        warm_start=warm_start,
        callback=callback,
    )
    assert allclose(
        x_sol,
        out.x_opt,
        rtol=1e-2,
    )

    assert allclose(
        f_sol,
        out.f_opt,
        rtol=1e-2,
    )


@SKIP_LICENSE
@pytest.mark.skip(
    reason=(
        "Test nothing. The first element is computed "
        "from the design space within the _pre_run."
        "Please find another way to test this."
    )
)
@pytest.mark.parametrize(
    (
        "warm_start",
        "normalize_design_space",
        "initial_value",
    ),
    [
        (False, False, 1),
        (False, True, 1),
        (True, False, 1),
        (True, True, 1),
        (True, False, -1),
        (True, True, -1),
        (True, True, 0),
    ],
)
def test_use_warm_start(
    warm_start: bool,
    normalize_design_space: bool,
    initial_value: int,
):
    """Test whether the warm start is used.

    We use a specific Hexaly callback to register the first point tested by Hexaly.
    """
    problem = Power2(initial_value=initial_value)
    design_values = problem.design_space.get_current_value()
    out = execute_algo(
        problem,
        algo_name="HEXALY",
        max_iter=1,  # Unfortunately, the first iteration is computed before the solver.
        normalize_design_space=normalize_design_space,
        warm_start=warm_start,
    )

    assert (out.x0_opt == design_values).all()


@SKIP_LICENSE
@pytest.mark.parametrize("seed", [None, 0, 1, 3])
def test_reproducibility(seed: int):
    """Test the reproducibility parameter."""
    problem = Rosenbrock()
    hexaly_opt = HexalyOpt("HEXALY")
    optimizer_mock = MagicMock()
    optimizer_mock.model = MagicMock()

    with patch(
        "gemseo_hexaly.algos.opt.hexaly.hexaly.HexalyOptimizer", new=optimizer_mock
    ) as mocker:
        # The algorithm execution should be triggered and stopped by GEMSEO,
        # but since we are mocking the behavior of this code,
        # we reach a situation that should not happen in real world scenarios.
        with pytest.raises(ValueError):
            # An error is expected here due to the mocked behavior,
            # indicating that the solver was not properly executed by GEMSEO.
            hexaly_opt.execute(
                problem,
                nb_threads=1,
                seed=seed,
                verbosity=0,
                use_reproducible_surrogate=True,
            )

        optimizer_mocked = mocker().__enter__()
        assert optimizer_mocked.param.seed == (seed or 0)
        assert optimizer_mocked.param.set_advanced_param.called
        assert optimizer_mocked.param.set_advanced_param.call_args[0] == (
            "bbInnerSolverChoiceForReproducibility",
            1,
        )
