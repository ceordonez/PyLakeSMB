#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pdb
import pandas as pd

from scipy.special import iv

def delsontro(C, L, k600, r, kop, Zml, Ty, kht=0):
    """
    C: Concentration (umol/l)
    L: Lenght scale (m)
    r: lake radio (m)
    Zml: Mixed layer depth (m)
    Ty : type (round 0 or elongated 1)
    kop:
    kht: horizontal diffusivite (Peeters and Hofmann 2015 = 0
        Lawrence et al 1995 = 1)
    """

    x = np.linspace(0,r,50)
    if kht == 0:
        Kh = 1.4*10**(-4)*L**(1.07)*86400 #(m2/d)
    elif kht == 1:
        Kh = 3.2*10**(-4)*L**(1.10)*86400 #(m/d)
    lda = np.sqrt((k600/Zml + kop)/Kh)
    Cc = C.iloc[-1]

    if Ty == 'R':
        Cx = Cc*iv(0,lda*x)
    elif Ty == 'E':
        Cr = Cc
        Cx = Cc*np.exp(-lda*x) + Cr*np.exp(-lda*(2*r-x))
    return Cx, x, k600, Kh, lda

def keeling(C, dC):
    pol = np.polyfit(1/C, dC, 1)
    ds = pol[1]
    return ds, pol[0]

def f_k600(U10, A):
    """
    A: Lake area (km2)
    U10: wind speed at 10m (m/s)
    """
    k600 = 2.51 + 1.48*U10 + 0.39*U10*np.log10(A) # (cm/h) Vachon and Praire (2013)
    k600 = k600*24/100. #(m/d)
    return k600

def fractionation(C, dC, ds, a=1.02):
    y = np.log(((a-1)*1000)-(dC-ds))
    pol = np.polyfit(np.log(C), y, 1)
    b0 = pol[1]
    b1 = pol[0]
    return b0, b1

def f_kop(b0, b1, k600, Zml):
    kop = b1*k600/Zml/(1-b1)
    return kop


def pross_data(data):
    r_lake = []
    r_date = []
    r_k600 = []
    r_Kh = []
    r_lda = []
    r_b0 = []
    r_b1 = []
    r_ds = []
    r_pol0 = []
    for lake in data:
        for date in data[lake]:
            C = data[lake][date]['CH4']
            dC = data[lake][date]['dCH4']
            L = data[lake][date]['Distance'].max()
            r = data[lake][date]['Distance'].max()
            C = C.drop(1)
            dC = dC.drop(1)
            ds, pol0 = keeling(C, dC)
            b0, b1 = fractionation(C, dC, ds)
            k600 = f_k600(1, 5.2)
            kop = f_kop(b0, b1, k600, 4)
            Cx, x, k600, Kh, lda = delsontro(C, L, k600, r, kop, 4.0, 'E', 0)
            datares = {'Distance': x, 'CH4': Cx}
            datares = pd.DataFrame(datares)
            allres = {lake: {date: datares}}
            r_lake.append(lake)
            r_date.append(date)
            r_k600.append(k600)
            r_Kh.append(Kh)
            r_lda.append(lda)
            r_b0.append(b0)
            r_b1.append(b1)
            r_ds.append(ds)
            r_pol0.append(pol0)

    pindex = [np.array(r_lake), np.array(r_date)]
    paramres = {'k600': k600, 'Kh': Kh, 'lda': lda, 'b0': b0, 'b1': b1,
                'ds': ds, 'pol0': pol0}
    paramres = pd.DataFrame(data = paramres,
                            index=pindex)
    pdb.set_trace()
    return allres, paramres

