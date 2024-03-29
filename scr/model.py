#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy as np

from scipy.interpolate import interp1d
from scipy.optimize import curve_fit


def transport_model(pnet, fsed, fhyp, fdis, k_h, kch4, modelparam, model_conf, x=None,
                    opt=False, levellog=20):
    """Calculate the concentration C(x,t) using 1-D lateral tranport model using
    finite difference approach.

    Prameters
    ---------
    pnet : float
           Internal net producition in the water column (umolm-3d-1)
    fsed : float
           Littoral sediment flux (mmolm-2d-1)
    fhyp : float
           Vertical flux through the base of the SML (mmolm-2-d)
    fdis : dataframe
           Spatial distribution of bubble dissolution (umolm-3d-1)
    k_h  : float
           Horizontal dispersion coefficient (md-1)
    kch4 : float
           Mass transfer coefficient (md-1)
    modelparam: dataframe
                Lake paramenters
    model_conf: dict()
                Information about the model defined in config_model.ylm
    x : TODO
    opt : TODO

    Returns
    -------
    C, r : CH4 concentration along a transect.

    """

    dr = model_conf['dr']
    tf = model_conf['t_end']
    dt = model_conf['dt']

    R = modelparam.R.values[0]
    Hsml = modelparam.Hsml.values[0]
    Rs = modelparam.Rs.values[0]
    Hcp = modelparam.Hcp.values[0]
    Patm = modelparam.pCH4atm.values[0]
    Kz = modelparam.Kz.values[0]
    Chyp = modelparam.Chyp.values[0]
    #typ = modelparam.Type.values[0]

    t = np.arange(0, tf + dt, dt)
    r = np.arange(0, R + dr, dr)  # From 0 to R
    Fs = np.zeros(len(r))
    kz = np.zeros(len(r))
    #Fz = np.zeros(len(r))
    h = np.ones(len(r)) * Hsml
    m = np.zeros(len(r))

    Fs[r > Rs] = fsed
    m[r > Rs] = -Hsml / (r.max() - Rs)
    h[r > Rs] = m[r > Rs] * (r[r > Rs] - r.max())
    h[-1] = 1E10000
    kz[r < Rs] = Kz * 60 * 60 * 24  # m/d
    #Fz[r < Rs] = fhyp

    # Initial Conditions
    C = np.ones((len(r), len(t))) * Patm * Hcp
    p1 = np.zeros(len(r) - 1)
    p2 = np.ones(len(r))
    p3 = np.zeros(len(r) - 1)
    # Type of lake elongated ('E') and round ('R')
    #if typ == 'R':
    #    type_dev = 1 / r[1:-1] + m[1:-1] / h[1:-1]
    #if typ == 'E':
    #    type_dev = m[1:-1] / h[1:-1]
    #Crating matrix
    p1[:-1] = -k_h * dt / (dr**2) + k_h * dt / (2 * dr) * (1 / r[1:-1] + m[1:-1] / h[1:-1])
    p2[1:-1] = 1 + 2 * k_h * dt / (dr**2) + kch4 * dt / h[1:-1] + Kz / h[1:-1]
    p3[1:] = -k_h * dt / (dr**2) - k_h * dt / (2 * dr) * (1 / r[1:-1] + m[1:-1] / h[1:-1])
    B = np.diag(p1, k=-1) + np.diag(p2) + np.diag(p3, k=1)
    Bp = np.linalg.inv(B)
    Ssed = Fs * dt / h
    Shyp = kz * Chyp * dt / h
    Ssed[-1] = 0  # Sediment flux = 0 at the sediment
    Somp = pnet * 1E-3 * np.ones(len(Ssed)) * dt
    if not (fdis.Diss == 0).all():
        f_dis = interp1d(fdis['Radius'], fdis['Diss'], kind='nearest',
                         fill_value='extrapolate')
        Sdis = f_dis(r) * dt / 1000.
    else:
        Sdis = np.zeros(len(Ssed))
    Somp[0] = 0
    Sdis[0] = 0
    sources = Ssed + Somp + Sdis + Shyp  #Kz*Chyp/h
    n = 0
    err = np.ones(len(t)) * np.inf

    while True:
        C[1:-1, n + 1] = Bp.dot(C[:, n] + sources)[1:-1]
        # Border conditions
        C[0, n + 1] = C[1, n + 1]
        C[-1, n + 1] = C[-2, n + 1]
        err[n + 1] = abs(C[1:-1, n + 1].mean() - C[1:-1, n].mean())
        if n >= len(t) - 2:
            C = C[:, :n + 2]
            if not opt:
                logging.log(levellog, 'Mean model concentration %.2f', C[:, -1].mean())
                logging.log(levellog,'Model finish at maximun days')
            break
        if err[n + 1] < 0.0001:
            C = C[:, :n + 2]
            if not opt:
                logging.log(levellog,'Mean model concentration %.2f', C[:, -1].mean())
                logging.log(levellog,'Model finish after %.0f days', t[n + 1])
            break
        n += 1

    C = C[:, -1]
    Fa = kch4 * (C - Hcp * Patm)
    Fa = Fa.mean()
    r = r.max() - r
    if opt:
        p = np.polyfit(r, C, 10)  #kind = 'cubic')
        f = np.poly1d(p)
        C = f(x)
        return C
    else:
        return r, C, Fa

def opt_test(model_conf, lddata, inputs, levellog=10):

    d_lddata = lddata[0]
    p_lddata = lddata[2]
    t_lddata = lddata[3]
    s_r = t_lddata.Distance.values.copy()
    s_C = t_lddata.CH4.values.copy()
    s_r[s_r > p_lddata.R.values[0]] = p_lddata.R
    Kh = p_lddata.Kh.values[0]
    kch4 = inputs[0]
    Fsed = inputs[1]
    Fhyp = inputs[2]
    if model_conf['mode_model']['var'] == 'FSED':
        opt, _ = curve_fit(lambda ds_r, Fsed: \
                             transport_model(0, Fsed, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, s_r, True, levellog), s_r, s_C,
                              bounds=(0, np.inf))
        r, C, Fa = transport_model(0, opt, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, levellog=levellog)
        var = 'Fsed_opt'

    elif model_conf['mode_model']['var'] == 'PNET':
        logging.log(levellog, 'Fitting Pnet')
        opt, _ = curve_fit(lambda s_r, Pnet: \
                             transport_model(Pnet, Fsed, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, s_r, True, levellog), s_r, s_C,
                             bounds=(-np.inf, np.inf))
        r, C, Fa = transport_model(opt, Fsed, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, levellog=levellog)
        var = 'Pnet_opt'

    elif model_conf['mode_model']['var'] == 'KH':
        opt, _ = curve_fit(lambda s_r, Kh: \
                             transport_model(0, Fsed, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, s_r, True, levellog), s_r, s_C,
                             bounds=(Kh/10.,Kh*10))
        r, C, Fa = transport_model(0, Fsed, Fhyp, d_lddata, opt, kch4, p_lddata, model_conf, levellog=levellog)
        var = 'kh_opt'

    elif model_conf['mode_model']['var'] == 'KCH4':
        opt, _ = curve_fit(lambda s_r, ks: \
                             transport_model(0, Fsed, Fhyp, d_lddata, Kh, kch4, p_lddata, model_conf, s_r, True, levellog), s_r, s_C,
                             bounds=(0, np.inf))
        r, C, Fa = transport_model(0, Fsed, Fhyp, d_lddata, Kh, opt, p_lddata, model_conf, levellog=levellog)
        var = 'kch4_opt'

    return r, C, Fa, opt, var
