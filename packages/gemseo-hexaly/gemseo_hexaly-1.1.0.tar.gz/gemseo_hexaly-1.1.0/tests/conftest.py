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

"""The module fixtures."""

import pytest
from gemseo_optimization_problems.knapsack import Knapsack
from numpy import array


@pytest.fixture(scope="module")
def knapsack_max_items() -> Knapsack:
    """Create a :class:`.Knapsack` optimization problem.

    Returns:
        A Knapsack instance constrained by the number of items.
    """
    values = array([55.0, 10.0, 47.0, 5.0, 4.0, 50.0, 8.0, 61.0, 85.0, 87.0])
    weights = array([95.0, 4.0, 60.0, 32.0, 23.0, 72.0, 80.0, 62.0, 65.0, 46.0])
    knapsack = Knapsack(
        values,
        weights,
        capacity_items=5,
    )
    knapsack.solution = (array([1, 0, 0, 0, 0, 1, 0, 1, 1, 1]), array([-338.0]))
    return knapsack
