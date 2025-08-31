# -*- coding: utf-8 -*-

# lefschetz-family
# Copyright (C) 2021  Eric Pichon-Pharabod

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sage.all

from .numperiods.family import Family
from .numperiods.integerRelations import IntegerRelations
from ore_algebra import *

from sage.modules.free_module_element import vector
from sage.rings.qqbar import QQbar
from sage.functions.other import factorial
from sage.functions.other import floor
from sage.matrix.constructor import matrix
from sage.rings.integer_ring import ZZ
from sage.matrix.special import identity_matrix
from sage.matrix.special import diagonal_matrix
from sage.matrix.special import block_matrix
from sage.matrix.special import block_diagonal_matrix
from sage.matrix.special import zero_matrix

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import QQ
from sage.schemes.toric.weierstrass import WeierstrassForm
from sage.misc.flatten import flatten

from sage.modules.free_quadratic_module_integer_symmetric import IntegralLattice

from .voronoi import FundamentalGroupVoronoi
from .integrator import Integrator
from .util import Util
from .context import Context
from .hypersurface import Hypersurface
from .monodromyRepresentationEllipticSurface import MonodromyRepresentationEllipticSurface

import logging
import time

logger = logging.getLogger(__name__)


class AllowableLoop(object):
    def __init__(self, surface, loop, **kwds):
        """surface, an elliptic surface, loop an allowable loop.

        This class aims at computing an effective basis of the homology group H_n(X), 
        given as lifts of paths through a Lefschetz fibration.
        """
        
        self.ctx = Context(**kwds)
        
        self._surface = surface
        self._loop = loop
        
        
    def __str__(self):
        sP= str(self.surface.P)
        if len(sP) >40:
            sP = sP[:20] +"<...>"+ sP[-20:]
        s = "Elliptic surface with defining equation " + sP + " and a loop"
        return s
    
    def __repr__(self):
        sP= str(self.P)
        if len(sP) >40:
            sP = sP[:20] +"<...>"+ sP[-20:]
        s = "Elliptic surface with defining equation " + sP + " and a loop"
        return s
    
    @property
    def surface(self):
        return self._surface

    def unwinding_braid(self, loop):
        """Given a loop as a product of simple loops, determine the braid that puts this loop in simples form gamma1...gammak"""