# coding: utf8

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
#from sage.rings.integer_ring import ZZ
#from sage.rings.rational_field import QQ
#from sage.rings.fraction_field import FractionField

def get_variables(eqs):
    """
    Returns the list of actually appearing variables in eqs
    
    Assume that eqs is a system of equations having the same parent
    """
    if eqs == []:
        return []
        
    ring = eqs[0].parent()
    if False in [eq.parent() == ring for eq in eqs]:
        print "Polynomial ring of the system not well defined"
        return eqs
        
    #We define the set of used variables
    variables = set(eqs[0].variables())
    for eq in eqs[1:]:
        variables = variables.union(set(eq.variables()))
        
    #We want to preserve the order given in ring.
    return [va for va in ring.gens() if va in variables]
    
def change_var_order(self,var_list):
    """
    Change the order on variables of a DeforSystem. Assumes that the 
    var_list is a permutations of self.curr_variables.
    
    Updates in place the DeforSystem self.curr_ring, self.curr_variables,
    self.curr_eqs and self.relevant_ineqs
    """
    if set(var_list)!=set(self.curr_variables):
        print "Wrong variables. Check self.curr_variables to know which to sort."
    else:
        self.curr_variables = var_list
        self.curr_ring = PolynomialRing(self.base_ring,self.curr_variables)
        self.curr_eqs = [self.curr_ring(eq) for eq in self.curr_eqs]
        self.relevant_ineqs = set(p for p in self.ineqs 
                if set(p.variables()).issubset(set(self.curr_variables)))

