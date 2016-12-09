# coding: utf8

from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.rings.fraction_field import FractionField
from sage.matrix.constructor import matrix


def replace_p(P,listP,FractionField):
    """
    Take a rational fraction P and a list of rational fractions

    and try to find the simplest product or quotient
    """
    if P==0:
        return P
    Q = FractionField(P)
    d = Q.numerator().degree()+Q.denominator().degree()
    case = 0
    ind =-1
    for i,PP in enumerate(listP):
        PP = FractionField(PP)
        if not(PP==P):
            QQ1 = P*PP
            dd1 = QQ1.numerator().degree()+QQ1.denominator().degree()
            if dd1<d:
                Q=QQ1
                d = Q.numerator().degree()+Q.denominator().degree()
                case = 1
                ind = i
            QQ2 = PP/P
            dd2 = QQ2.numerator().degree()+QQ2.denominator().degree()
            if dd2<d:
                Q=QQ2
                d = Q.numerator().degree()+Q.denominator().degree()
                case = -1
                ind = i
    return FractionField(Q),[case,ind]

def compacte_liste(listP,FractionField):
    """
    Take a list of rational fractions

    and return the an equivalent list with minimal degrees.
    """
    check = matrix.zero(ZZ, len(listP))
    Res = [P for P in listP]
    for i,P in enumerate(listP):
        P = FractionField(P)
        Q,[case,ind] = replace_p(P,listP,FractionField)
        check[i,i] = 1
        if case != 0:
            check2 = check
            check2[i,ind] = case

            if check2.rank()<check.rank():#On vérifie qu'on n'oublie pas une équation!
                Q = P
            else:
                check = check2
        if not(Q in Res):
            Res.remove(P)
            if Q.numerator().degree()+Q.denominator().degree() == 0: 
                #(in case we had to proportional equations
                pass
            else:
                Res += [Q]
    return Res

def find_monom_eqs(sys):
    """
    Take a list of polynomials (seen as equations P=0

    and returns the list A/B where P = A-B and A, B are monomials
    """
    if sys == []:
        return sys
    P = sys[0]
    Ring = P.parent()# On vérifie le type
    for Q in sys[1:]:
        if not (Q.parent() == Ring):
            print "Problème de type"
            return []

    Monom = []
    Others = []
    Field = FractionField(Ring)
    for P in sys:
        MON = P.monomials()
        if len(MON)==2:
            Monom.append(Field(
                -P.monomial_coefficient(MON[0])/P.monomial_coefficient(MON[1])
                        *MON[0]/MON[1]))
        else:
            Others.append(P)
    return Monom, Others, Field

def monomial_simplify_sys(sys):
    """
    Take a list of polynomials (seen as equations P=0)

    and returns an equivalent list where the monomial equations have
    been simplified by product or division.
    """
    Monom,Others,F = find_monom_eqs(sys)

    Monom = compacte_liste(Monom,F)

    Monom_eq = [P.numerator() - P.denominator() for P in Monom]

    return Monom_eq + Others
