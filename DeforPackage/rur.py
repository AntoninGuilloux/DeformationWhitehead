# coding: utf8
###############

def components(self):
    """
    Returns a lists of RUR described components of unipotent solutions
    to the DeforSystem self.
    
    Such a component is a couple (dict, ring) suitable for substitution
    in self.eqs.
    
    Checks first if it has not been already computed.
    """
    try:
        return self.rur_comp#we check if it has been created
        
    except AttributeError:#else we constuct it
        M = self.actual_manifold
        
        Pt = M.ptolemy_variety(self.N,obstruction_class = 'all')
        
        C = Pt.retrieve_solutions(verbose = False)
        
        Comps = []
        for comp in C:#We only keep the 0-dim component, for which a Rur is computed
            Comps += [c for c in comp if c.dimension == 0]
        
        X = [c.cross_ratios() for c in Comps]
        
        #We now transform it in a list of actual substitutionnable dictionnaries
        ######################################################################
        
        #First we pass from PolMod to sage polynomial in a suitable ring
        DefPoly = [dic[self.ring.variable_names()[0]].mod() for dic in X]
        Rings = [self.ring.extension(
                        self.ring[str(pol.variable())](pol),
                        names = str(pol.variable())
                        ) for pol in DefPoly]
        #Then we change the keys of the dic to be suitable for substitutions
        SubsX= [    {
                        ri.base_ring()(key) : ri(va.lift())
                        for key, va in dic.items()
                    } 
                    for dic,ri in zip(X,Rings)
                ]
                
        # We now create the rur_comp attribute
        self.rur_comp = zip(SubsX,Rings)
        #And return it
        return self.rur_comp
        
def check(self):
    """
    Takes a DeforSystem
    
    Tries to retrieve the rur unipotent components for the manifold (if
    not already done).
    
    Check which components verify self.eqs
    Return a list of boolean
    """
    Comps = self.rur_components()
    
    CheckRur = []
    for (sub, ri) in Comps:
        subs_eqs = set([ri.base_ring()(eq).subs(sub) for eq in self.eqs])
        CheckRur.append (subs_eqs == set([0]))
    return CheckRur

