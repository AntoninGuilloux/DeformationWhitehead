# coding: utf8

import deforsys
from sage.misc.sage_eval import sage_eval

def dumps(self):
    """
    Transform a DeforSystem in a string, as described in the save method
    """
    variables_string = "# Variables\n"
    for varia in self.ring.gens():
        variables_string += "%s\n"%varia
        
    eqs_string = "# Equations\n"
    for eq in self.eqs:
        eqs_string += "%s\n"%eq
            
    ineqs_string = "# Inequations\n"
    for ineq in list(self.ineqs):
        ineqs_string += "%s\n"%ineq
    
    proj_string = "# Projections\n"
    for ke,val in self.proj.items():
        proj_string += "%s:%s\n"%(ke,val)
        
    initial_string = "# Initial Data\n%s"%self.initial
    
    return_string = "# Manifold\n%s\n"%self.manifold + "\n" +\
                    "# TO SL(N)n%s\n"%self.N + "\n" +\
                    "# Base ring\n%s\n"%self.base_ring + "\n" +\
                    variables_string + "\n" +\
                    eqs_string + "\n" +\
                    ineqs_string + "\n" +\
                    proj_string + "\n" +\
                    initial_string + "\n"
                    
    return return_string
    
    

def save(self,filename):
    """
    Transform a DeforSystem in a string and save it in a file.
    
    Format of the Data:
    
    # Manifold 
    Snappy identification of the manifold
    
    #To SL(N)
    N
    
    # Base ring
    A ring
    
    # Variables
    var1
    var2
    ...
    
    # Equations
    eq1
    eq2
    ...
    
    # Inequations
    ineq1
    ineq2
    ...
    
    # Projections
    key1:val1
    key2:val2
    ...
    
    # Initial Data
    a big string!
    
    """
    with open(filename,'w') as f:
        f.write(self._dumps())
        
def load(filename):
    with open(filename,'r') as f:
        if f.next() != "# base_ring\n":
            raise IOError("Not a valid file for describing a DeforSys")
        base_ring = sage_eval(f.next()[:-1])
        f.next()
        
        if f.next()!="# Variables\n":
            raise IOError("Not a valid file for describing a DeforSys")
        variables = [f.next()[:-1]]
        while f.next() != "\n":
            variables += [f.next()[:-1]]
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
        ring = PolynomialRing(base_ring, variables)
        
        local_eval = {st : va for st,va in zip(variables,ring.gens())}
        
        if f.next()!="# Equations\n":
            raise IOError("Not a valid file for describing a DeforSys")
        eqs = [sage_eval(f.next()[:-1],locals = local_eval)]
        while f.next() != "\n":
            eqs += [sage_eval(f.next()[:-1], locals = local_eval)]
            
        if f.next()!="# Inequations\n":
            raise IOError("Not a valid file for describing a DeforSys")
        ineqs = [sage_eval(f.next()[:-1], locals = local_eval)]
        while f.next() != "\n":
            ineqs += [sage_eval(f.next()[:-1], locals = local_eval)]
        ineqs = set(ineqs)
        
        if f.next()!="# Projecions\n":
            raise IOError("Not a valid file for describing a DeforSys")
        [ke,val] = f.next()[:-1].split(':')
        proj = {sage_eval(ke, locals = local_eval):sage_eval(val, locals = local_eval)}
        while f.next() != "\n":
            [ke,val] = f.next()[:-1].split(':')
            proj[sage_eval(ke, locals = local_eval)] = sage_eval(val, locals = local_eval)
            
        if f.next()!="# # Initial Data\n":
            raise IOError("Not a valid file for describing a DeforSys")
        initial = sage_eval(f.next(), locals = local_eval)
        
    return DeforSystem(eqs,ineqs,proj,init = initial)
        
        

        
    
