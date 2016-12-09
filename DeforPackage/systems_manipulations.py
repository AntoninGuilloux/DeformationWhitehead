# coding: utf8

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
#from sage.rings.integer_ring import ZZ
#from sage.rings.rational_field import QQ
#from sage.rings.fraction_field import FractionField
import deforsys

def my_factors_seq(pol):
    """
    Returns the list of factors (without exponents) appearing in pol
    """
    ring = pol.parent()
    if pol==0:
        return ring(0)
    else:
        return [ring(l[0]) for l in pol.factor()]


def factor(self):
    """
    Tries to split a DeforSystem by searching polynomials which can be factorized.
    Does not mind exponents in factorization.
    
    Returns a list of systems.
    """
    if self.curr_eqs == []:
        print "There is no equation!"
        return []
    
    factors = [my_factors_seq(eq) for eq in self.curr_eqs]
    num_fac = [len(fac) for fac in factors]
    
    systems_list = [[fac] for fac in factors[0]]
    for i in range(1,len(factors)):
        new_facs = factors[i]
        new_systems_list = []
        
        for system in systems_list:
            new_systems_list += [system+[fac] for fac in new_facs]
        systems_list = new_systems_list
    
    DeforSys_list = [deforsys.DeforSystem(new_eqs,
                                self.ineqs,
                                self.proj,
                                self.actual_manifold,
                                self.N
                                init = self.initial
                                )
                                        for new_eqs in systems_list]
        
    return DeforSys_list
    

def my_sort(eqs):
    """
    Sort a list of polynomials by lexicographical order on (degree,#vars)
    """
    premiere_etape=sorted(eqs,key=lambda p:p.degree());#Sort by degree
    return sorted(premiere_etape,key=lambda p: len(p.variables()));#And by number of vars
    
    
def clean_pol(pol,ineqs,ring):
    """
    Cleans pol of squared factors or factors belonging to ineqs.

    Returns the product of factors appearing in pol, without squares
    and without the factors that belong to ineqs (a list of prime polynomials).

    Assumes that all polynomials are child of ring
    """
    # If pol=0 nothing to do
    if (pol==0):
        return 0
    else:
        lf = [ring(l[0]) for l in pol.factor() if not (l[0] in ineqs)];
        p = ring(1);
        for fac in lf:
            p = ring(p*fac);
        # the returned polynomial lies in the same ring as pol
        return p;
    
def clean_sys(self):
    """
    Applies clean_pol to a DeforSystem (list of libsingular polynomials)
    """
    self.eqs = [clean_pol(P,self.ineqs,self.ring) for P in self.eqs]
    self._update_curr()
