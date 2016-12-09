# coding: utf8

import snappy
from . import deforsys
from . import monomial_manipulations as mm
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import QQ
from sage.rings.fraction_field import FractionField

def construire_equation(r,Ring):
    p=1;
    for i in range(len(r)):
        p=p*(Ring.gens()[i])**(r[i])
    return p-1;

def const_sys(self,n):
    """
    self is a Defor manifold.
    
    Return the system (a DeforSystem) defining its Deformation Variety
    together with inequations.
    """
    Eq=self.manifold.gluing_equations_pgl(N=n,equation_type='non_peripheral')#On récupère les equations d'aretes et de faces
    Mat=Eq.matrix;#c'est la matrice des exposants dans les equations
    variabl=Eq.explain_columns;#On récupère les variables
    ring=PolynomialRing(QQ,variabl);#On définit l'anneau des polynômes où on travaille
    field = FractionField(ring)
    
    ineqs = set([x for x in ring.gens()]+[x-1 for x in ring.gens()]);
    proj = {};
    
    sys1 = [ construire_equation(r,ring) for r in Mat.rows() ];
    sys2=[ring.gens()[3*i]*ring.gens()[3*i+1]*ring.gens()[3*i+2] +1  for i in range(len(variabl)/3)];
    sys3=[ring.gens()[3*i]*(1-ring.gens()[3*i+2])-1 for i in range(len(variabl)/3)] +\
        [ring.gens()[3*i+1]*(1-ring.gens()[3*i])-1 for i in range(len(variabl)/3)] +\
        [ring.gens()[3*i+2]*(1-ring.gens()[3*i+1])-1 for i in range(len(variabl)/3)]
    eqs = sys1 + sys2 + sys3
    
    return deforsys.DeforSystem(eqs,ineqs,proj,self.manifold,n)


class DeforManifold(snappy.Manifold):
    """
    A snappy manifold with an additional method to construct its Deformation
    variety
    """
    def __init__(self,M):
        self.manifold = snappy.Manifold(M).identify()[0]
        
    deformation_variety = const_sys

    
