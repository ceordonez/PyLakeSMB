#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

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

def kch4_model(f_tdata, k600_model, lake, surf_area, fa, mcs=False):
    Hch4 = Hcp(f_tdata.Temp.mean()).mean() # umol/l/Pa
    Patm = f_tdata.CH4_atm.mean() # Atmospheric Partial Pressure (Pa)
    if mcs:
        kch4_fc = fa/(f_tdata.CH4.mean()-Hch4*Patm)
        return kch4_fc
    else:
        kch4_fc = f_tdata.Fa_fc.mean()/(f_tdata.CH4.mean() - Hch4*Patm) # kch4 from flux chambers
        if 'kAVG' in k600_model:
            kch4 = kch4_fc.mean()
            if np.isnan(kch4):
                k600 = f_k600(f_tdata.U10.mean(), surf_area, 'kOPT', lake)
                kch4 = f_kch4(f_tdata.Temp.mean(), k600, f_tdata.U10.mean())
            if '05' in k600_model:
                kch4 = 0.5*kch4
            elif '15' in k600_model:
                kch4 = 1.5*kch4
        else:
            k600 = f_k600(f_tdata.U10.mean(), surf_area, k600_model, lake)
            kch4 = f_kch4(f_tdata.Temp.mean(), k600, f_tdata.U10.mean())
        model_Fa = kch4*(f_tdata.CH4.mean() - Hch4*Patm) # Flux k model data transect
        model_Fa = np.mean(model_Fa)
        return kch4, model_Fa, Hch4, Patm

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

def average_inputs(mc_data, dis_data, lake, date):

    if lake in dis_data:
        sources_fr = dis_data[lake][date]
    else:
        sources_fr = None
    newdate = date[0:4] +'-'+date[4:6] + '-' +date[6:]
    Fsed = mc_data.loc[lake, newdate].SedF_avg # Sediment flux [mmol/m2/d]
    OMP = mc_data.loc[lake, newdate].OMP_avg # OMP [umol/m3/d]
    SurfF = mc_data.loc[lake, newdate].SurfF_avg # Surface diffusive flux [mmol/m2/d]
    Fhyp = mc_data.loc[lake, newdate].Fhyp_avg # Hypolimnetic diffusive flux [mmol/m2/d]
    sources_avg = pd.DataFrame({'OMP': OMP, 'Fsed': Fsed, 'SurfF': SurfF, 'Fhyp': Fhyp}, index=[0])
    return sources_avg, sources_fr

def desvstd_inputs(mc_data, dis_data, lake, date):

    newdate = date[0:4] +'-'+date[4:6] + '-' +date[6:]
    Fsed = mc_data.loc[lake, newdate].SedF_std # Sediment flux [mmol/m2/d]
    OMP = mc_data.loc[lake, newdate].OMP_std # OMP [umol/m3/d]
    SurfF = mc_data.loc[lake, newdate].SurfF_std # Surface diffusive flux [mmol/m2/d]
    Fhyp = mc_data.loc[lake, newdate].Fhyp_std # Hypolimnetic diffusive flux [mmol/m2/d]
    sources_std = pd.DataFrame({'OMP': OMP, 'Fsed': Fsed, 'SurfF': SurfF, 'Fhyp': Fhyp}, index=[0])
    return sources_std

def param_outputs(cxavg, sources_avg, Rdis, f_tdata, modelparam, model_conf, opt=None, fa_opt=None, varname_opt=None):
    OMP = sources_avg.OMP.values[0]
    Fsed = sources_avg.Fsed.values[0]
    SurfF = sources_avg.SurfF.values[0]
    Fhyp = sources_avg.Fhyp.values[0]
    Cavg = f_tdata.CH4.mean()
    zsml = modelparam.Hsml.values[0]
    Kh = modelparam.Kh.values[0]
    kch4 = modelparam.kch4.values[0]
    R = modelparam.Radius.values[0]
    Rs = modelparam.Rs.values[0]
    t_end = model_conf['t_end']
    if model_conf['mode_model']['mode'] == 'OPT' :
        if model_conf['mode_model']['var'] == 'FSED':
            OMP = 0
        param = [opt[0], fa_opt, cxavg, Cavg, OMP, Fsed, SurfF, Fhyp, Rdis, zsml, Kh, kch4,
            R, Rs, t_end]
        nameres = [varname_opt, 'Fa_opt', 'Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF', 'Fz', 'Rdis',
                'Hsml', 'Kh', 'kch4', 'R', 'Rs', 't_end']
    if model_conf['mode_model']['mode'] == 'EVAL':
        param = [cxavg, Cavg, OMP, Fsed, SurfF, Fhyp, Rdis, zsml, Kh, kch4, R, Rs, t_end]
        nameres = ['Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF', 'Fz', 'Rdis', 'Hsml', 'Kh', 'kch4',
                'R', 'Rs', 't_end']
    return param, nameres

