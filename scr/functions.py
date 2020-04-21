#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def Khmodel(L, kind):
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

def f_k600(U10, A, kind):
    """Velocity transfer coefficient k600
    U10: Wind velocity at 10m  (m/s)
    kind: 'VP' Vachon and Praire (2013)
    Return k600 (m/d)
    """
    if kind == 'VP':
        k600 = 2.51 + 1.48*U10 + 0.39*U10*np.log10(A) # (cm/h) Vachon and Praire (2013)
        k600 = k600*24/100. #(m/d)

    return k600

def f_kch4(T, k600, U10):
    # Prairie and del Giorgo 2013
    if U10 > 3.7:
        n = 1/2.
    else:
        n = 2/3.
    kch4 = k600*(600/Sc_ch4(T))**n
    return kch4.mean()

def Sc_ch4(T):
    sc = 1897.8-114.28*T+3.2902*T**2-0.039061*T**3
    return sc

def Hcp(T):
    T = T + 273.15
    H = 1.4E-5 # mol/m3/Pa Sander 2015
    lndHdt = 1750
    Hcp = H*np.exp(lndHdt*(1/T-1/298.15))*1000 # umol/l/Pa
    return Hcp
