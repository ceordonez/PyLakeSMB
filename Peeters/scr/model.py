#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

def transport_model(OMP, Fsed, Fhyp, Fdis, Hsml, Kh, Kch4, R, dt, tf, dr, Patm, Hcp, Rs, typ, x=None,
                    opt=False):
    """Calculate the lateral tranport from methane C(x,t) from a 1-D model based on finete difference approach.# {{{

    Prameters
    ---------
    OMP : TODO
    Fsed : TODO
    Fhyp : TODO
    Hsml : TODO
    Kh : TODO
    Kch4 : TODO
    R : TODO
    dt : TODO
    tf : TODO
    dr : TODO
    Patm : TODO
    Hcp : TODO
    typ : TODO
    x : TODO
    opt : TODO

    Returns
    -------
    C, r : CH4 concentration along a transect.

    """# }}}
    t = np.arange(0, tf+dt, dt)
    r = np.arange(0, R+dr, dr) # From 0 to R
    Fs = np.zeros(len(r))
    Fz = np.zeros(len(r))
    h = np.ones(len(r))*Hsml
    m = np.zeros(len(r))

    Fs[r>Rs] = Fsed
    m[r>Rs] = -Hsml/(r.max() - Rs)
    h[r>Rs] = m[r>Rs]*(r[r>Rs] - r.max())
    h[-1]=1E10000
    Fz[r<Rs] = Fhyp

    # Initial Conditions
    C = np.ones((len(r), len(t)))*Patm*Hcp
    p1 = np.zeros(len(r)-1)
    p2 = np.ones(len(r))
    p3 = np.zeros(len(r)-1)
    # Type of lake elongated ('E') and round ('R')
    if typ == 'R':
        type_dev = 1/r[1:-1] + m[1:-1]/h[1:-1]
    if typ == 'E':
        type_dev = m[1:-1]/h[1:-1]
    #Crating matrix
    p1[:-1] = -Kh*dt/(dr**2) + Kh*dt/(2*dr)*(1/r[1:-1] + m[1:-1]/h[1:-1])
    p2[1:-1] = 1 + 2*Kh*dt/(dr**2) + Kch4*dt/h[1:-1]
    p3[1:] = -Kh*dt/(dr**2) - Kh*dt/(2*dr)*(1/r[1:-1] + m[1:-1]/h[1:-1])
    B = np.diag(p1, k=-1) + np.diag(p2) + np.diag(p3, k=1)
    Bp = np.linalg.inv(B)
    Ssed = Fs*dt/h
    Shyp = Fz*dt/h
    Ssed[-1] = 0 # Sediment flux = 0 at the sediment
    Somp = OMP*1E-3*np.ones(len(Ssed))*dt
    if Fdis is not None:
        f_dis = interp1d(Fdis['Radius [m]'], Fdis['Diss [micro-mol/m3/d]'], kind='nearest', fill_value='extrapolate')
        """
        plt.plot(r, f_dis(r))
        plt.plot(Fdis['Radius [m]'], Fdis['Diss [mmol/m3/d]'], 'o')
        plt.show()
        __import__('pdb').set_trace()
        """
        Sdis = f_dis(r)*dt/1000.
    else:
        Sdis = np.zeros(len(Ssed))
    Somp[0] = 0
    Sdis[0] = 0
    for n in range(len(t)-1):
        C[1:-1, n+1] = Bp.dot(C[:, n] + Ssed + Somp + 0*Sdis + Shyp)[1:-1]
        # Border conditions
        C[0, n+1] = C[1, n+1]
        C[-1, n+1] = C[-2, n+1]
    C = C[:,-1]
    Fa = Kch4*(C-Hcp*Patm)
    Fa = Fa.mean()
    r = r.max() - r
    if opt:
#        f = interp1d(r, C, kind = 'cubic')
        p = np.polyfit(r, C, 10) #kind = 'cubic')
        f = np.poly1d(p)
        C = f(x)
        return C
    else:
        """
        fig, ax = plt.subplots()
        ax1 = ax.twinx()
        ax.plot(r, C, 'ko')
        ax1.plot(r, f_dis(r))
        plt.show()
        __import__('pdb').set_trace()
        """
        return r, C, Fa
# }}}
def opt_test(exp, sdata, OMP, Fsed, Fhyp, Rdis, hsml, kh, ks, R, dt, tf, dr, Patm, Hcp, Rs, typ):# {{{
    s_r = sdata.index.values.copy()
    s_r[s_r>R] = R
    s_C = sdata.CH4.values.copy()
    if 'FSED' in exp:
        opt, cov = curve_fit(lambda ds_r, Fsed: \
                             transport_model(0, Fsed, Fhyp, Rdis, hsml, kh, ks,
                                             R, dt, tf, dr, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                              bounds=(0, np.inf))
        r, C, Fa = transport_model(0, opt, Fhyp, Rdis, hsml, kh, ks, R, dt, tf, dr, Patm,
                                   Hcp, Rs, typ)
        var = 'Fsed_opt'
    elif 'OMP' in exp:
        logging.info('Fitting OMP')
        opt, cov = curve_fit(lambda s_r, OMP: \
                             transport_model(OMP, Fsed, Fhyp, Rdis, hsml, kh, ks,
                                             R, dt, tf, dr, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(-np.inf, np.inf))
        r, C, Fa = transport_model(opt, Fsed, Fhyp, Rdis, hsml, kh, ks, R, dt, tf, dr, Patm,
                                   Hcp, Rs, typ)
        var = 'OMP_opt'
    elif 'KH' in exp:
        opt, cov = curve_fit(lambda s_r, Kh: \
                             transport_model(0, Fsed, Fhyp, Rdis, hsml, Kh, ks,
                                             R, dt, tf, dr, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(kh/10.,kh*10))
        r, C, Fa = transport_model(0, Fsed, Fhyp, Rdis, hsml, opt, ks, R, dt, tf, dr, Patm,
                                   Hcp, Rs, typ)
        var = 'kh_opt'
    elif 'KCH4' in exp:
        opt, cov = curve_fit(lambda s_r, ks: \
                             transport_model(0, Fsed, Fhyp, Rdis, hsml, kh, ks,
                                             R, dt, tf, dr, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(0, np.inf))
        r, C, Fa = transport_model(0, Fsed, Fhyp, Rdis, hsml, kh, opt, R, dt, tf, dr, Patm,
                                   Hcp, Rs, typ, Ac)
        var = 'kch4_opt'
    return r, C, Fa, opt, var# }}}
