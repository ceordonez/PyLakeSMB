#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
from scipy.special import iv # Modified Bessel function first kind


def Kh(L, kind):
    """Horizontal diffusion coefficient (Kh)
    L: Lenght scale (m)
    kind: P from Peeters and Hofmann (2015)
          L from Lawrence et al 1995
    Return Kh (m/d)
    """
    if kind == 'P':
        Kh = 1.4*10**(-4)*L**(1.07)*86400 # (m2/d) (Peeters and Hofmann (2015)
    elif kind == 'L':
        Kh = 3.2*10**(-4)*L**(1.10)*86400 # (m2/d) (Lawrence et al 1995)
    return Kh


def k600(U10, A, kind):
    """Velocity transfer coefficient k600
    U10: Wind velocity at 10m  (m/s)
    kind: 'VP' Vachon and Praire (2013)
    Return k600 (m/d)
    """
    if kind == 'VP':
        k600 = 2.51 + 1.48*U10 + 0.39*U10*np.log10(A) # (cm/h) Vachon and Praire (2013)
        k600 = k600*24/100. #(m/d)

    return k600


