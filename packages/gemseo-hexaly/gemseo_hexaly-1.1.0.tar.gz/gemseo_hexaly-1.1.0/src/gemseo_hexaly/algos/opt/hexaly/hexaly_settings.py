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

"""Settings for the Hexaly library."""

from __future__ import annotations

from gemseo.algos.opt.base_optimizer_settings import BaseOptimizerSettings
from pydantic import Field
from pydantic import NonNegativeInt
from pydantic import StrictBool
from pydantic import conint

from gemseo_hexaly.algos.opt.hexaly._core.hexaly_callback import (
    HexalyCallback,  # noqa: TC001, RUF101
)


class HexalySettings(BaseOptimizerSettings):
    """The Hexaly settings."""

    activate_surrogate: StrictBool = Field(
        default=False,
        description="""Whether to activate the internal surrogate model.""",
    )

    warm_start: StrictBool = Field(
        default=False,
        description="""Whether to consider the current value of the design space
        as the initial solution.""",
    )

    callback: HexalyCallback | None = Field(
        default=None,
        description=(
            """The callback function called during the optimization algorithm.
            If ``None``, no callback is given to the Hexaly solver."""
        ),
    )

    verbosity: conint(ge=0, le=2) = Field(
        default=0,
        description="""The verbosity level of the optimizer.
        0: All the traces are disabled.
        1: Normal verbosity. This is the default level.
        2: Detailed verbosity. Displays statistics during the search.""",
    )

    nb_threads: NonNegativeInt = Field(
        default=0,
        description="""The number of threads used by Hexaly.
        If 0,  the number of threads is automatically adapted to your computer
        and to your optimization model..""",
    )

    seed: NonNegativeInt | None = Field(
        default=None,
        description="""The random seed for the optimizer.
        If ``None``, use GEMSEO initial seed.""",
    )

    use_reproducible_surrogate: bool = Field(
        default=False,
        description="""Whether the surrogate model is reproducible.
        If ``True``, the solver may be less performant.""",
    )
