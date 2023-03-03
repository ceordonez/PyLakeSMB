#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import numpy as np

def Khmodel(lscale, kind):
    """Horizontal diffusion coefficient (Kh)

    Parameters
    ----------
    lscale : Lenght scale (m)
    kind   : P from Peeters and Hofmann (2015) or L from Lawrence et al 1995

    Return
    ----------
    Kh : Horizontal dispersion coefficient (md-1)
    """

    if kind == 'P':
        Kh = 1.4*10**(-4)*lscale**(1.07)*86400 # (m2/d) (Peeters and Hofmann (2015)
    elif kind == 'L':
        Kh = 3.2*10**(-4)*lscale**(1.10)*86400 # (m2/d) (Lawrence et al 1995)
    return Kh

def f_k600(u10, Aa, k600_model):
    """Calculates velocity transfer coefficient k600

    Parameters
    ----------
    U10  : Wind velocity at 10m  (ms-1)
    k600_model : 'VP' Vachon and Praire (2013)
           'MA-NB' MacIntyre et al. (2010) negative bouyancy
           'MA-PB' MacIntyre et al. (2010) positive bouyancy
           'MA-MB' MacIntyre et al. (2010) mixed bouyancy
           'CC' Cole and caraco (1998)

    Return
    ----------
    k600 : velocity transfer coefficient (md-1)
    """

    if k600_model == 'VP': # Vachon and Praire (2013)
        k600 = 2.51 + 1.48*u10 + 0.39*u10*np.log10(Aa) # (cm/h)
    elif k600_model == 'CC': # Cole and Caraco 1998
        k600 = 2.07 + 0.215*u10**1.7
    elif k600_model == 'MA-NB': # cooling (negative bouyancy) MacIntyre 2010
        k600 = 2 + 2.04*u10
    elif k600_model == 'MA-PB': # warming (positive bouyancy) MacIntyre 2010
        k600 = 1.74*u10 - 0.15
    elif k600_model == 'MA-MB': # mixed model MacIntyre 2010
        k600 = 2.25*u10 + 0.16
    k600 = k600*24/100. #(m/d)
    return k600

def kch4_model(t_lddata, k600_model, p_lddata, mcs=False, fa_mcs=None):

    Hch4 = Hcp(t_lddata.Tw.mean()).mean() # umol/l/Pa
    Patm = t_lddata.pCH4atm.mean() # Atmospheric Partial Pressure (Pa)

    if mcs:
        kch4_fc = fa_mcs/(t_lddata.CH4.mean()-Hch4*Patm)
        return kch4_fc

    kch4_fc = t_lddata.Fa.mean()/(t_lddata.CH4.mean() - Hch4*Patm) # kch4 from flux chambers
    if 'kAVG' in k600_model:
        kch4 = kch4_fc.mean()
        if np.isnan(kch4):
            logging.error('No flux chamber data')
            sys.exit()
        if '05' in k600_model:
            kch4 = 0.5*kch4
        elif '15' in k600_model:
            kch4 = 1.5*kch4
    else:
        k600 = f_k600(t_lddata.U10.mean(), p_lddata.Aa * 1E6, k600_model)
        kch4 = f_kch4(t_lddata.Tw.mean(), k600, t_lddata.U10.mean())
    return kch4

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

def param_outputs(cxavg, f_lddata, Rdis, t_lddata, p_lddata, model_conf, opt=None, fa_opt=None, varname_opt=None):
    Pnet = f_lddata.P_avg.values[0]
    Fsed = f_lddata.Fs_avg.values[0]
    SurfF = f_lddata.Fa_avg.values[0]
    Fhyp = f_lddata.Fz_avg.values[0]
    Cavg = t_lddata.CH4.mean()
    zsml = p_lddata.Hsml.values[0]
    Kh = p_lddata.Kh.values[0]
    kch4 = p_lddata.kch4.values[0]
    R = p_lddata.R.values[0]
    Rs = p_lddata.Rs.values[0]
    t_end = model_conf['t_end']
    if model_conf['mode_model']['mode'] == 'OPT' :
        if model_conf['mode_model']['var'] == 'FSED':
            Pnet = 0
        param = [opt[0], fa_opt, cxavg, Cavg, Pnet, Fsed, SurfF, Fhyp, Rdis, zsml, Kh, kch4,
            R, Rs, t_end]
        nameres = [varname_opt, 'Fa_opt', 'Cmod', 'Cavg', 'Pnet', 'Fsed', 'SurfF', 'Fz', 'Rdis',
                'Hsml', 'Kh', 'kch4', 'R', 'Rs', 't_end']
    if model_conf['mode_model']['mode'] == 'EVAL':
        param = [cxavg, Cavg, Pnet, Fsed, SurfF, Fhyp, Rdis, zsml, Kh, kch4, R, Rs, t_end]
        nameres = ['Cmod', 'Cavg', 'Pnet', 'Fsed', 'SurfF', 'Fz', 'Rdis', 'Hsml', 'Kh', 'kch4',
                'R', 'Rs', 't_end']
    return param, nameres

