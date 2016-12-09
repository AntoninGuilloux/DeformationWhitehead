# coding: utf8

import io
import rur
from sage.structure.sage_object import SageObject
import linear_elimination as le
import systems_manipulations as sysman
import variables_manipulations as varman
import monomial_manipulations as mm
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing


class DeforSystem(SageObject):
    #####Initialisation######
    def __init__(self,eqs,ineqs,proj,manifold,N,**init_data):
        if 'init' in init_data:
            self.initial = init_data['init']
        else:
            self.initial = [eqs,ineqs,proj]
            
        self.actual_manifold = manifold
        self.N = N #We study representations in SL(N)
        
        self.ring = self.initial[0][0].parent()
        
        self.eqs = [self.ring(eq) for eq in eqs]
        self.ineqs = set(self.ring(ineq) for ineq in ineqs)
        self.proj = proj
        self.base_ring = self.ring.base_ring()
 
        self._simplify()

##################### Requested methods (representation and latex #####
        
    def _repr_(self):
        return """
System defining a deformation variety, in variables %s, with %i equations
        """%(self.curr_variables, len(self.eqs))
        
    def _latex_(self):
        return "\mathrm{Deformation variety ideal}"
        
   
    #################### Methods #############################
    def _update_curr(self):
        self.curr_variables = varman.get_variables(self.eqs)
        self.curr_ring = PolynomialRing(self.base_ring,self.curr_variables)
        self.curr_eqs = [self.curr_ring(eq) for eq in self.eqs]
        self.relevant_ineqs = set(p for p in self.ineqs 
                if set(p.variables()).issubset(set(self.curr_variables)))
        
        
########################## I/O #############################
    #Simply a method to export in a txt file
    export = io.save
        
    ####### Simplication methods #######
    # Perform a monomial simplify sys step.
    def _monomial_simplify_sys_(self):
        self.eqs = mm.monomial_simplify_sys(self.eqs)
    
    #Sort the equations
    def _simple_sort(self):
        self.eqs = sysman.my_sort(self.eqs)
        self._update_curr()
    
    #clean the equations (remove exponents and ineqs factor    
    def _clean_sys(self):
        """
        Applies clean_pol to a DeforSystem (list of polynomials)
        """
        loceqs = self.eqs
        self.eqs = [sysman.clean_pol(P,self.ineqs,self.ring) 
                            for P in loceqs]
        self._update_curr()
        
    #Combines the three methods above
    def _clean_sort(self):
        self._clean_sys()
        self._monomial_simplify_sys_()
        self._simple_sort()
        
    #Recursively apply simplifications
    def _simplify(self):
        eqs1 = self.eqs
        self._clean_sort()
        eqs2 = self.eqs
        while (eqs2 != eqs1):
            eqs1 = self.eqs
            self._clean_sort()
            eqs2 = self.eqs
    
    #To change the order of variables in the current state
    change_var_order = varman.change_var_order 

    #To add an equation
    def add_eq(self,eq):
        try:
            self.eqs.append(self.eqs[0].parent()(eq))
            self._update_curr()
        except TypeError:
            print "Variables non compliant"
    
    #Look in the eqs for factorizable equations and then splits the system.
    factor = sysman.factor
    
    ###### The linear elimination, the key point for those systems
    #Find a suitable linear substitution
    _find_lin_eq = le.find_lin_eq
    
    #Apply it
    _linear_elim_step = le.linear_simplify_sys_one_step
    
    #The linear elimination boucle
    linear_elim = le.linear_elimination
    
#############  Retrieving and checking the RUR components ##############    

    rur_components = rur.components

    rur_check = rur.check #A faire    
        
    
    
