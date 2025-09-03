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

"""Callback that can be used within Hexaly."""

from abc import abstractmethod
from typing import ClassVar

from hexaly.optimizer import HexalyOptimizer
from hexaly.optimizer import HxCallbackType


class HexalyCallback:
    """A Hexaly callback."""

    _CALLBACK_TYPE: ClassVar[HxCallbackType] = HxCallbackType.ITERATION_TICKED
    """The type of callback."""

    _N_ITERATIONS_BETWEEN_TICKS: ClassVar[int] = 1
    """The number of iterations between ticks."""

    @abstractmethod
    def execute_callback(
        self, optimizer: HexalyOptimizer, callback_type: HxCallbackType
    ) -> None:
        """Execute the callback.

        Args:
            optimizer: The Hexaly optimizer.
            callback_type: The callback type.
        """
