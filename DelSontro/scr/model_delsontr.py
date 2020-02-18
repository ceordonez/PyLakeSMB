#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import logging
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
    Ty : type (round R or elongated E)
    kop:
    kht: horizontal diffusivite (Peeters and Hofmann 2015 = 0
        Lawrence et al 1995 = 1)
    """
    x = np.linspace(0, r, 50)
    if kht == 0:
        Kh = 1.4*10**(-4)*L**(1.07)*86400 #(m2/d)
    elif kht == 1:
        Kh = 3.2*10**(-4)*L**(1.10)*86400 #(m/d)

    lda = np.sqrt((k600/Zml + kop)/Kh)
    indmin = C.index.min()
    indmax = C.index.max()

    if Ty == 'R':
        Cc = C.loc[indmax]
        Cx = Cc*iv(0, lda*x)

    elif Ty == 'E':
        Cc = C.loc[indmin]
        Cr = Cc
        Cx = Cc*np.exp(-lda*x) + Cr*np.exp(-lda*(2*r-x))
    return Cx, x, lda, Kh

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


def pross_data(data, clake, Kh_model, Bio_model):
    r_lake = []
    r_date = []
    params = []
    allres = dict()
    ladate = dict()
    for lake in data:
        for date in data[lake]:
            logging.info('Processing data from lake %s on %s', lake, date)
            L = clake[lake][date][2]
            r = clake[lake][date][3]
            filt = clake[lake][date][4]
            tym = clake[lake][date][5]
            zml = clake[lake][date][1]
            A = clake[lake][date][0]
            if filt:
                find = data[lake][date].index[filt]
                fdata = data[lake][date].drop(find)
            else:
                fdata = data[lake][date]
            C = fdata.CH4
            dC = fdata.dCH4
            ds, pol0 = keeling(C, dC)
            b0, b1 = fractionation(C, dC, ds)
            U10 = fdata.U10.mean()
            k600 = f_k600(U10, A)
            if Bio_model:
                kop = f_kop(b0, b1, k600, zml)
                Cx, x, lda, Kh = delsontro(C, L, k600, r, kop, zml, tym, Kh_model)
            else:
                Cx, x, lda, Kh = delsontro(C, L, k600, r, 0, zml, tym, Kh_model)
            datares = {'CH4': Cx}
            datares = pd.DataFrame(datares, index=x)
            r_lake.append(lake)
            r_date.append(date)
            params.append([k600, Kh, kop, lda, b0, b1, ds, pol0])
            ladate.update({date: datares})
        allres.update({lake: ladate})
    nameres = ['k600', 'Kh', 'kop', 'lda', 'b0', 'b1', 'ds', 'pol0']
    pindex = [np.array(r_lake), np.array(r_date)]
    paramres = pd.DataFrame(data = params, columns = nameres,
                            index=pindex)
    return allres, paramres

