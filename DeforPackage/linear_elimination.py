# coding: utf8

import deforsys
from sage.rings.integer_ring import ZZ
from sage.misc.randstate import set_random_seed
import systems_manipulations as sysman


my_factors_seq = sysman.my_factors_seq


def find_lin_eq(self,step=2):
    """
    Looks for an equation in a DeforSys which is linear in a variable

    Looks for a polynomial P in the system such that P=D*v+N
    The coefficient D of the variable should be a product of factors in ineqs

    Returns a list: [P,v,D,N]. If nothing is found, returns  [-1,-1,0,0]
    """
    sys = self.eqs
    ineqs = self.ineqs
    filter(lambda p : p!=0, sys)

    # L'ensemble des polynôme qui ont une variable linéaire
    l=[[pol,pol.variables()] for pol in sys if 1 in pol.degrees()];
    
    
    lin_eq_poss=[];
    estimated_degree_max=[]
    estimated_degree_sum = []

    #We try every substitution
    for [P,vars] in l:
        lv=[v for v in vars if P.degree(v)==1];#the list of linear variables
        cpv=[self.ring(P.coefficient(v)) for v in lv];#and their coefficients
        for i,pol in enumerate(cpv):
            lfcomp=filter(lambda p : not p in ineqs, my_factors_seq(pol))
            if lfcomp==[]:#We found a possble substitution
                lin_eq_poss.append([P,lv[i],pol,P.subs({lv[i]:0})]);
    
    #Then we sum up
    if lin_eq_poss==[]:
        print 'Perdu'
        return [-1,-1,0,0];
    else:
        #Now we estimate the degree after susbstitution
        #step defines the maximal admissible jump in degree (default 2)
        #On pourrait paralléléliser...
        dmax = max([pol.degree() for pol in sys if pol != 0])+step
        for poss in lin_eq_poss:
            substi = []
            deglist = []
            for pol in sys:
                newpol = self.ring(pol.subs({poss[1]:-poss[3]/poss[2]}).numerator())
                if newpol != 0:
                    d = newpol.degree()
                    if d>dmax:#On peut arréter, on est trop haut en degré
                        deglist+=[d]
                        break
                    else:
                        substi += [newpol]
                        deglist += [d]

            degmax = max(deglist)
            if degmax<dmax:
                dmax = degmax

            degsum = 0
            for d in deglist:
                degsum += d

            estimated_degree_max.append(degmax)
            estimated_degree_sum.append(degsum)

        meilleur_poss = [[poss, degsum] for poss,d,degsum in \
            zip(lin_eq_poss,estimated_degree_max,estimated_degree_max)
            if d == dmax]
        if meilleur_poss==[]:
            print 'Perdu'
            return [-1,-1,0,0];
        dsum = min([m[1] for m in meilleur_poss])
        meilleur_poss = [poss for poss,d in meilleur_poss if d == dsum]
        if len(meilleur_poss)==1:
            meilleur = meilleur_poss[0]
        else:
            meilleur = meilleur_poss[ZZ.random_element(0,len(meilleur_poss) - 1)]
    print "         Il y avait %i possibilités de substitution linéaire"%len(lin_eq_poss)
    print '         Une possibilité retenue parmi %i meilleure(s) ; variable %s'%(len(meilleur_poss),str(meilleur[1]));
    return meilleur


def linear_simplify_sys_one_step(self,found_lin_sys):
    """
    In a DeforSystem, makes a substitution a found linear equation.

    Updates the equations, the inequations and the dictionnary proj
    keeping tracks of the substitutions already made

    Modify the DeforSys in place.
    """
    eqs_ori = self.eqs
    ineqs_ori = self.ineqs
    proj_ori = self.proj
    ring = self.ring
    
    # We want to perform the following substitution
    proj={found_lin_sys[1]:-found_lin_sys[3]/found_lin_sys[2]}
    eqs=[P for P in eqs_ori if P!=found_lin_sys[0]]# on enlève l'équation qui nous sert à projeter
    eqs=list(set([ring((P.substitute(proj)).numerator()) for P in eqs_ori])); # on met à jour les équations
    eqs = [eq for eq in eqs if eq!=0]

    self.eqs = eqs

    # Maintenant les inéquations
    ineqs = list(ineqs_ori);#On garde les anciennes
    for p in ineqs_ori:# on met à jour les inéquations existantes
        ineqs += my_factors_seq((p.substitute(proj)).numerator())
        ineqs += my_factors_seq((p.substitute(proj)).denominator())
        ineqs += my_factors_seq(found_lin_sys[2])
        ineqs += my_factors_seq(-found_lin_sys[3])
        ineqs += my_factors_seq(found_lin_sys[2]+found_lin_sys[3])
        # on ne garde que la liste des facteurs
    filter(lambda p: p!=1,ineqs);
    ineqs = set(ineqs)
    self.ineqs = ineqs

    if 0 in ineqs:
        print 'Erreur impossible'   ;

    # Et la projection
    for k in proj_ori.keys():# on met à jour les anciennes valeurs du dictionnaire
        proj[k]=(proj_ori[k]).substitute(proj);
    self.proj = proj

    self._simplify()
    
def linear_elimination(self, filename = '', limit = 10, seed = 0,step = 2):
    """
    Recursively subsitutes linear variables in the DeforSys

    using find_linear_equation search for a suitable variable
    then apply linear_simplify_sys_one_step

    limit is an int which specify the maximal number of steps. By default 10
    
    step is the maximal acceptable jump in degree when performing one step

    Returns a DeforSystem
    """
    log = False
    if filename != '':
        try:
            logfile = open(filename,'w')
            log = True
        except IOError:
            print """
############## Attention ################
      The log file is not valid
#########################################
                    """
    
    [eqs_ori,ineqs_ori,proj_ori]=[self.eqs,self.ineqs,self.proj]
    sys_treated=[]
    
    compteur=0 #Pour donner des infos
    set_random_seed(seed) # pour la reproductibilité
    while (compteur<limit) :
        compteur+=1
        
        #Feedback
        print "Etape %i"%compteur
        print "    Le degré est %i"%max(pol.degree() for pol in self.eqs)
        print "    Le nombre d'équations est %i"%len(self.eqs)
        
        if log:
            logfile.write("""
Step %i
            
    The degree is %i.
    The number of equations is %i
                
            """%(compteur,max(pol.degree() for pol in self.eqs),len(self.eqs))
            )
        
        #We search a linear substitution
        fle= self._find_lin_eq(step=step);

        if fle[1]==-1:# If none, we are done
            
            #Feedback
            print "No possibilities without augmenting the degree"
            
            if log:
                logfile.write("""
    No further possible substitutions without augmenting
    too much the degree
                    
                """)
            break #We exit the while loop
            
        else:# if there is a substitution, we apply it.
            
            self._linear_elim_step(fle)
            
            #Logging
            if log:
                #Details in another file
                with open(filename + "_subs_%i"%compteur,'w') as sublogfile:
                    sublogfile.write("""
#substituted variable
%s
                    
#Polynomial used
%s
                    """%(fle[1],fle[0])
                    )
                #We advert this in the main file
                logfile.write("""
    We made a substitution, see file %s
                
                """%(filename + "_subs_%i"%compteur)
                )
        
        
        #Feedback    
        new_deg = max(pol.degree() for pol in self.eqs)
        new_number =  len(self.eqs)
        print "Fin de l'étape %i"%compteur
        print "    Le degré est %i"%new_deg
        print "    Le nombre d'équations est %i"%new_number
        print ""
        
        if log:
            logfile.write("""
Fin de l'étape %i
    Le degré est %i
    Le nombre d'équations est %i

            """%(compteur,new_deg,new_number))
    
    #At the end, we close the log file
    if log:
        logfile.close()
