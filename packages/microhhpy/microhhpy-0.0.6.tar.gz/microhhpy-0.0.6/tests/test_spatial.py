#
#  MicroHH
#  Copyright (c) 2011-2024 Chiel van Heerwaarden
#  Copyright (c) 2011-2024 Thijs Heus
#  Copyright (c) 2014-2024 Bart van Stratum
#
#  This file is part of MicroHH
#
#  MicroHH is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MicroHH is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MicroHH.  If not, see <http://www.gnu.org/licenses/>.
#

# Standard library

# Third-party.
from matplotlib import use
import pytest

# Local library
from microhhpy.spatial import Domain, plot_domains


def test_domain_noproj():
    """
    Domain definition without spatial projection.
    """
    d0 = Domain(
        xsize=3200,
        ysize=3200,
        itot=32,
        jtot=32,
        n_ghost=3,
        n_sponge=4,
        )

    d1 = Domain(
        xsize=1600,
        ysize=1600,
        itot=32,
        jtot=32,
        n_ghost=3,
        n_sponge=4,
        parent=d0,
        center_in_parent=True,
        )

    plot_domains([d0, d1])


def test_domain_proj():
    """
    Domain definition with spatial projection.
    """

    lat = 51.97
    lon = 4.92

    proj_str = f'+proj=lcc +lat_1={lat-1} +lat_2={lat+1} +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

    d0 = Domain(
        xsize=512_000,
        ysize=512_000,
        itot=64,
        jtot=64,
        n_ghost=3,
        n_sponge=5,
        lon=lon,
        lat=lat,
        anchor='center',
        proj_str=proj_str
        )

    d1 = Domain(
        xsize=256_000,
        ysize=256_000,
        itot=64,
        jtot=64,
        n_ghost=3,
        n_sponge=3,
        parent=d0,
        center_in_parent=True
        )

    plot_domains([d0, d1], use_projection=True)