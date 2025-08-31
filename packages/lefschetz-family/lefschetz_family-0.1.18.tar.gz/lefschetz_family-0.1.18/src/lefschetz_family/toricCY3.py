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

from .numperiods.integerRelations import IntegerRelations
from ore_algebra import *

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import QQ
from sage.rings.qqbar import QQbar
from sage.functions.other import factorial
from sage.matrix.constructor import matrix
from sage.arith.misc import gcd
from sage.rings.integer_ring import ZZ
from sage.matrix.special import identity_matrix
from sage.matrix.special import diagonal_matrix
from sage.matrix.special import block_matrix
from sage.matrix.special import zero_matrix
from sage.misc.flatten import flatten
from sage.interfaces.mathematica import mathematica
from sage.schemes.toric.weierstrass import WeierstrassForm_P1xP1
from sage.misc.misc_c import prod

from ore_algebra import OreAlgebra

from .voronoi import FundamentalGroupVoronoi
from .integrator import Integrator
from .context import Context
from .ellipticSurface import EllipticSurface
from .monodromyRepresentation import MonodromyRepresentation

import logging
import time

logger = logging.getLogger(__name__)


def derivative(P, A, v):
    k = ZZ((A(1,1,1).degree()+3)/3)
    newnum = 1/k*P*A.derivative(v) - A*P.derivative(v)
    return newnum

class ToricCY3(object):
    def __init__(self, defining_polynomial, basepoint=None, basepoint_CY3=None, fibration=None, **kwds):
        assert all([defining_polynomial.degree(v)<=2 for v in list(defining_polynomial.parent().gens())[:2]]), "defining equation not quadratic in variables"
        self.defining_equation = defining_polynomial
        self.variables = list(defining_polynomial.parent().gens())[:-1]
        self.basepoint = 1 if basepoint==None else basepoint
        self.basepoint_CY3 = 1 if basepoint_CY3==None else basepoint_CY3
        self._fibration = fibration

        self.ctx = Context(**kwds)

    @property
    def specialisation_homomorphism(self):
        if not hasattr(self, "_specialisation_homomorphism"):
            R = PolynomialRing(QQ, ["X","Y","Z"])
            X,Y,Z = R.gens()
            Suv = PolynomialRing(R,["t","z","w"])
            _, z, w = Suv.gens()
            St = PolynomialRing(R, "t")
            t = St.gen(0)

            self._specialisation_homomorphism = Suv.hom([self.basepoint_CY3, t, self.basepoint], St)
        return self._specialisation_homomorphism

    @property
    def defining_equation_fibre(self):
        if not hasattr(self, "_defining_equation_fibre"):
            param = PolynomialRing(QQ, ["t","z","w"])
            t,z,w = param.gens()
            Rel = PolynomialRing(param, ["x0","x1","y0","y1"])
            x0,x1,y0,y1 = Rel.gens()
            biquadric = Rel(self.defining_equation(x0/x1,y0/y1,z,w,t)*x1**2*y1**2)
            p,q = [param(m) for m in WeierstrassForm_P1xP1(biquadric, [x0, x1, y0, y1])]

            proj = self.specialisation_homomorphism
            X,Y,Z = proj.domain().base_ring().gens()
            t, z, w = proj.domain().gens()

            self._defining_equation_fibre = -Z*Y**2 + X**3 + p(t,z,w)*X*Z**2 + q(t,z,w)*Z**3
        return self._defining_equation_fibre
        

    @property
    def fibre(self):
        if not hasattr(self, "_fibre"):
            self._fibre = EllipticSurface(self.specialisation_homomorphism(self.defining_equation_fibre), fibration=self._fibration, nbits=self.ctx.nbits)
        return self._fibre
    
    @property
    def forms_to_integrate_fibre(self):
        if not hasattr(self, "_forms_to_integrate_fibre"):
            logger.info("Computing cohomology forms.")
            begin = time.time()
            P = self.defining_equation_fibre
            R = P.parent()
            t,z,w = R.gens()
            forms = []
            for l in range(4):
                logger.info("Derivative of order %d/3 in t."% (l))
                formsl = []
                for k in range(len(self.fibre.transcendental_lattice)):
                    # logger.info("Derivative of order %d/3 in t and %d/%d in w."% (l, k, len(self.fibre.transcendental_lattice)-1))
                    if l==0 and k==0:
                        formsl += [P.parent(1)]
                    elif k==0:
                        formsl += [derivative(P, forms[-1][0], t)]
                    else:
                        formsl += [derivative(P(R(self.basepoint_CY3),z,w), formsl[-1](R(self.basepoint_CY3),z,w), w)]
                forms += [formsl]
            end = time.time()
            duration_str = time.strftime("%H:%M:%S",time.gmtime(end-begin))
            logger.info("Cohomology forms computed -- total time: %s."% (duration_str))
            self._forms_to_integrate_fibre = [[self.specialisation_homomorphism(A) for A in formsl] for formsl in forms]
        return self._forms_to_integrate_fibre
    

    @property
    def period_matrix_fibre(self):
        if not hasattr(self, "_period_matrix_fibre"):
            forms = self.forms_to_integrate_fibre
            logger.info("Integrating periods of K3 fibre.")
            begin = time.time()
            integrated_forms = self.fibre.integrate_forms(flatten(forms))
            primary_periods = integrated_forms * matrix(self.fibre.extensions).transpose()
            periods_tot = block_matrix([[primary_periods, zero_matrix(primary_periods.nrows(), len(flatten(self.fibre.components_of_singular_fibres))+2)]])
            self._period_matrix_fibre = periods_tot * matrix(self.fibre.primary_lattice).inverse()

            end = time.time()
            duration_str = time.strftime("%H:%M:%S",time.gmtime(end-begin))
            logger.info("K3 periods computed -- total time: %s."% (duration_str))
        return self._period_matrix_fibre

    @property
    def picard_fuchs_equations(self):
        if not hasattr(self, "_picard_fuchs_equations"):
            logger.info("Computing Picard-Fuchs equations.")
            begin = time.time()
            Qt = PolynomialRing(QQ, "w")

            St = OreAlgebra(Qt, "Dw")
            picard_fuchs_equations = []
            mathematica("f="+str(self.defining_equation))
            for k in range(4):
                begin_step = time.time()
                mathematica("R = D[1/f, {t, "+str(k)+"}] /. {t -> "+str(self.basepoint_CY3)+"}")
                mathematica("ann = Annihilator[R, {Der[x], Der[y], Der[z], Der[w]}]")
                mathematica("ann1 = CreativeTelescoping[ann, Der[x], { Der[y], Der[z], Der[w] }][[1]]")
                mathematica("ann2 = CreativeTelescoping[ann1, Der[y],{ Der[z], Der[w] }][[1]]")
                mathematica("ann3 = CreativeTelescoping[ann2, Der[z],{ Der[w] }][[1]]")
                Llist = mathematica("ann3[[1]]")[1].sage()
                L = sum([Qt(str(c)) * St.gen()**ZZ(p[0]) for c, p in Llist])
                picard_fuchs_equations += [L]
                end_step = time.time()
                duration_str = time.strftime("%H:%M:%S",time.gmtime(end_step-begin_step))
                logger.info("Picard-Fuchs equation of derivative of order %d computed -- total time: %s."% (k, duration_str))
            self._picard_fuchs_equations = picard_fuchs_equations

            end = time.time()
            duration_str = time.strftime("%H:%M:%S",time.gmtime(end-begin))
            logger.info("Picard-Fuchs equations computed -- total time: %s."% (duration_str))

        return self._picard_fuchs_equations
    
    @property
    def critical_values(self):
        if not hasattr(self, "_critical_vaues"):
            singular_K3_locus = gcd([L.leading_coefficient() for L in self.picard_fuchs_equations])
            self._critical_values = singular_K3_locus.roots(QQbar, multiplicities=False)
        return self._critical_values
    
    @property
    def fundamental_group(self):
        if not hasattr(self, "_fundamental_group"):
            fundamental_group = FundamentalGroupVoronoi(self.critical_values, self.basepoint)
            self._critical_values = [self.critical_values[i] for i in fundamental_group.sort_loops()]
            self._fundamental_group = fundamental_group
        return self._fundamental_group

    @property
    def monodromy_matrices(self):
        if not hasattr(self, "_monodromy_matrices"):
            L = self.picard_fuchs_equations[0]
            integrator = Integrator(self.fundamental_group, L, self.ctx.nbits)
            transition_matrices = integrator.transition_matrices

            pM = self.period_matrix_fibre.submatrix(0,0,len(self.fibre.transcendental_lattice)) * matrix(self.fibre.transcendental_lattice).transpose()
            
            integration_correction = diagonal_matrix([1/ZZ(factorial(k)) for k in range(len(self.fibre.transcendental_lattice))])
            monodromy_matrices = [(pM.inverse() * integration_correction.inverse() * tM * integration_correction * pM).change_ring(ZZ) for tM in transition_matrices]

            Minfinity = prod(list(reversed(monodromy_matrices))).inverse().change_ring(ZZ)
            if Minfinity != 1:
                self._critical_values = self.critical_values + ["infinity"]
                monodromy_matrices += [Minfinity]

            self._monodromy_matrices = monodromy_matrices
        return self._monodromy_matrices
    
    @property
    def monodromy_representation(self):
        if not hasattr(self, "_monodromy_representation"):
            IP_fibre = matrix(self.fibre.transcendental_lattice) * self.fibre.intersection_product * matrix(self.fibre.transcendental_lattice).transpose()
            self._monodromy_representation = MonodromyRepresentation(self.monodromy_matrices, IP_fibre)
        return self._monodromy_representation
    
    @property
    def extensions(self):
        return self.monodromy_representation.extensions

    @property
    def integrated_thimbles(self):
        if not hasattr(self, "_integrated_thimbles"):
            logger.info("Integrating thimbles.")
            begin = time.time()
            integrated_thimbles_all = []
            for i, L in enumerate(self.picard_fuchs_equations):
                s = len(self.fibre.transcendental_lattice)
                periods_fibre = self.period_matrix_fibre.submatrix(i*s,0,s)

                L = L* L.parent().gens()[0]
                integrator = Integrator(self.fundamental_group, L, self.ctx.nbits)
                transition_matrices = integrator.transition_matrices
                transition_matrices += [prod(list(reversed(transition_matrices))).inverse()] # infinity
                
                pM = periods_fibre * matrix(self.fibre.transcendental_lattice).transpose()
                integration_correction = diagonal_matrix([1/ZZ(factorial(k)) for k in range(s+1)])
                
                derivatives_at_basepoint = zero_matrix(1,s).stack(identity_matrix(s))
                
                initial_conditions = integration_correction * derivatives_at_basepoint  * pM
                initial_conditions = initial_conditions.submatrix(0,0,transition_matrices[0].ncols())
                integrated_thimbles = []
                for i, ps in enumerate(self.monodromy_representation.permuting_cycles):
                    integrated_thimbles += [(transition_matrices[i] * initial_conditions * p)[0] for p in ps]
                integrated_thimbles_all += [integrated_thimbles]
            end = time.time()
            duration_str = time.strftime("%H:%M:%S",time.gmtime(end-begin))
            logger.info("Thimbles integrated -- total time: %s."% (duration_str))
            self._integrated_thimbles =  matrix(integrated_thimbles_all)
        return self._integrated_thimbles
    
    @property
    def period_matrix(self):
        if not hasattr(self, "_period_matrix"):
            homology_mat = matrix(self.monodromy_representation.extensions).transpose()
            integrated_thimbles =  self.integrated_thimbles
            self._period_matrix = integrated_thimbles * homology_mat
        return self._period_matrix
    
    @property
    def intersection_product(self):
        if not hasattr(self, "_intersection_product"):
            self._intersection_product = self.monodromy_representation.intersection_product_extensions
        return self._intersection_product
    
    @property
    def transcendental_lattice(self):
        if not hasattr(self, "_transcendental_lattice"):
            vanishing_periods = IntegerRelations(self.period_matrix.transpose()).basis
            transcendental_lattice = (vanishing_periods * self.intersection_product).right_kernel_matrix()
            self._transcendental_lattice = transcendental_lattice.columns()
        return self._transcendental_lattice
