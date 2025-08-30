"""
inverse_laplace - Numerical Inverse Laplace Transform using Talbot's Method.

This module provides efficient computation of the inverse Laplace transform using Talbot’s method,
suitable for engineering, physics, and mathematical applications.

Dependencies:
    - sympy
    - mpmath
"""

import sympy as sp
import mpmath
from functools import lru_cache
from multiprocessing import Pool, cpu_count

t, s = sp.symbols('t s', real=True)

@lru_cache(maxsize=None)
def get_lambdified_func(F):
    return sp.lambdify(s, F, 'mpmath')

def inverse_laplace(F, s, t_val):
    if t_val <= 0:
        return 0.0
    F_func = get_lambdified_func(F)
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

def pretty_ilaplace(X, s, t, prec=34):
    f = sp.inverse_laplace_transform(X, s, t)
    f = f.subs(sp.Heaviside(t), 1)
    f = f.subs(sp.cos(sp.I*t/2), sp.cosh(t/2))
    f = sp.simplify(f.subs(sp.cosh(t/2) - sp.sinh(t/2), sp.exp(-t/2)))
    f = sp.expand_trig(f)
    f = sp.simplify(f)
    f_num = sp.N(f, prec)
    terms = f_num.as_ordered_terms()
    output_terms = []
    for term in terms:
        term = sp.expand(term)
        # extract exp factor
        if term.has(sp.exp):
            exp_factors = [e for e in term.atoms(sp.exp)]
            exp_factor = 1
            for ef in exp_factors:
                exp_factor *= ef
            term_no_exp = term / exp_factor
        else:
            exp_factor = 1
            term_no_exp = term
        coeff_cos = 0
        coeff_sin = 0
        for func in term_no_exp.atoms(sp.Function):
            if isinstance(func, sp.cos):
                coeff_cos += term_no_exp.coeff(func)
            if isinstance(func, sp.sin):
                coeff_sin += term_no_exp.coeff(func)
        if coeff_cos == 0 and coeff_sin == 0:
            output_terms.append(term)
            continue
        trig_funcs = [f for f in term_no_exp.atoms(sp.Function) if isinstance(f, sp.sin) or isinstance(f, sp.cos)]
        omega = None
        if trig_funcs:
            arg = trig_funcs[0].args[0]
            omega = sp.N(arg / t, prec)  # numeric frequency
        C = sp.N(coeff_cos, prec)
        if C == 0:
            C = sp.N(coeff_sin, prec)
            k = 1.0
        else:
            k = sp.N(coeff_sin / C, prec)
        standardized = C * exp_factor * (sp.cos(omega*t) + k*sp.sin(omega*t))
        output_terms.append(standardized)
    final_expr = sp.Add(*output_terms)
    return final_expr

__all__ = ['inverse_laplace', 'pretty_ilaplace']
