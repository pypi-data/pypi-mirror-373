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
from __future__ import annotations

import pytest
from hexaly.optimizer import HexalyOptimizer


def has_license() -> bool:
    """Check whether tests can use Hexaly, through the existence of the license.

    Returns:
        True if there is a license. False otherwise.
    """
    try:
        HexalyOptimizer()
    except:  # noqa: E722
        return False

    return True


SKIP_LICENSE = pytest.mark.skipif(has_license() is False, reason="No Hexaly license.")
