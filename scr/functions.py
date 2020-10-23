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

def f_k600(U10, A, kind, lake=False):
    """Velocity transfer coefficient k600
    U10: Wind velocity at 10m  (m/s)
    kind: 'VP' Vachon and Praire (2013)
    Return k600 (m/d)
    """
    if kind == 'VP': # Vachon and Praire (2013)
        k600 = 2.51 + 1.48*U10 + 0.39*U10*np.log10(A) # (cm/h)
    elif kind == 'CC': # Cole and Caraco 1998
        k600 = 2.07 + 0.215*U10**1.7
    elif kind == 'MA-NB': # cooling (negative bouyancy) MacIntyre 2010
        k600 = 2 + 2.04*U10
    elif kind == 'MA-PB': # warming (positive bouyancy) MacIntyre 2010
        k600 = 1.74*U10 - 0.15
    elif kind == 'MA-MB': # mixed model MacIntyre 2010
        k600 = 2.25*U10 + 0.16
    elif kind == 'kOPT':
        if lake == 'Baldegg':
            pol = [1.1091, 0.0528]
        elif lake == 'Bretaye':
            pol = [0.5229, 0.7927]
        elif lake == 'Chavonnes':
            pol = [0.7886, 1.1077]
        elif lake == 'Hallwil':
            pol = [0.3215, 0.6378]
        elif lake == 'Lioson':
            pol = [-0.2514, 2.9929]
        elif lake == 'Noir':
            pol = [0.2121, 1.1814]
        elif lake == 'Soppen':
            pol = [0.2898, 0.3834]
        k600 = pol[1] + pol[0]*U10
        k600 = k600*100/24.
    k600 = k600*24/100. #(m/d)
    return k600


def f_kch4(T, k600, U10, a=1):
    # Prairie and del Giorgo 2013
    if U10 > 3.7:
        n = 1/2.
    else:
        n = 2/3.
    kch4 = k600*(600/Sc_ch4(T))**(a*n)
    return kch4

def Sc_ch4(T):
    sc = 1897.8-114.28*T+3.2902*T**2-0.039061*T**3
    return sc

def Hcp(T):
    T = T + 273.15
    H = 1.4E-5 # mol/m3/Pa Sander 2015
    lndHdt = 1750
    Hcp = H*np.exp(lndHdt*(1/T-1/298.15))*1000 # umol/l/Pa
    return Hcp
