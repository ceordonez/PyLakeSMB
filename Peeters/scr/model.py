#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import pdb
import logging

def transport_model(OMP, Fsed, hsml, kh, ks, R, dt, tf, Patm, Hcp, Rs, typ, x=None,
                    opt=False):
    dr = np.round(np.sqrt(kh*dt/0.25))
    t = np.arange(0, tf+dt, dt)
    Ma = 0
    r = np.arange(0, R+dr, dr) # From 0 to R
    C = np.ones((len(r), len(t)))*Patm*Hcp
    C[0, :] = C[1, 0]
    for n in range(len(t)-1):
        for a in range(len(r)-2):
            i = len(r) - a - 2
            if r[i]<=Rs:
                Fs = 0
                H = hsml
                m = 0
            else:
                Fs = Fsed
                m = -hsml/(r.max()-Rs)
                H = m*r[i] + hsml*r.max()/(r.max()-Rs)
                #H = hsml/2.
            k = ks
            P = OMP
            if typ == 'R':
                C[i,n+1] = (1/(dr**2))*kh*dt*(C[i+1,n] -2*C[i,n] + C[i-1,n]) + \
                    kh*dt/(2*dr)*(1/r[i] + m/H)*(C[i+1,n] - C[i-1,n]) + \
                    C[i,n] - (C[i,n]-Patm*Hcp)*dt*k/H + Fs*dt/H +\
                    P*1E-3*dt
            if typ == 'E':
                C[i,n+1] = (1/(dr**2))*kh*dt*(C[i+1,n] -2*C[i,n] + C[i-1,n]) + \
                    kh*dt/(2*dr)*(m/H)*(C[i+1,n] - C[i-1,n]) + \
                    C[i,n] - (C[i,n]-Patm*Hcp)*dt*k/H + Fs*dt/H +\
                    P*1E-3*dt

    #Ma += np.sum(np.pi*R**2*C[:,n].mean())*k*dt
        C[0, n+1] = C[1, n+1]
        C[-1, n+1] = C[-2, n+1]
    r = r.max() - r
    C = C[:, -1]
    Fa = k*(C-Hcp*Patm)
    Fa = Fa.mean()
    if opt:
#        f = interp1d(r, C, kind = 'cubic')
        p = np.polyfit(r, C, 10) #kind = 'cubic')
        f = np.poly1d(p)
        C = f(x)
        return C
    else:
        return r, C, Fa

    #M = 0
    #for i in range(len(r)-2):
    #    Mi = np.pi*(r[i+1]**2-r[i]**2)*hsml*(C[i+1,-1]+C[i,-1])/2
    #    M += Mi
    #Ms = Fsed*2*np.pi*R*t[-1]*hsml
    #Mt = np.sum(M)
#    Fa = k*(C-Hcp*Patm)
#    Fa = Fa.mean()
    #return r, t, C, Mt, Ma, Ms
#    if opt:
#        f = interp1d(r, C, kind = 'cubic')
#        p = np.polyfit(r, C, 10) #kind = 'cubic')
#        f = np.poly1d(p)
#        C = f(x)
#        return C
#    else:
#        return r, C, Fa
def opt_test(exp, sdata, OMP, Fsed, hsml, kh, ks, R, dt, tf, Patm, Hcp, Rs, typ):
    
    s_r = sdata.index.values.copy()
    s_r[s_r>R] = R
    s_C = sdata.CH4.values.copy()

    if 'FSED' in exp:
        opt, cov = curve_fit(lambda ds_r, Fsed: \
                             transport_model(0, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                              bounds=(0, np.inf))
        r, C, Fa = transport_model(0, opt, hsml, kh, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ)
        var = 'Fsed_opt'
    elif 'OMP' in exp:
        logging.info('Fitting OMP')
        opt, cov = curve_fit(lambda s_r, OMP: \
                             transport_model(OMP, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(-np.inf, np.inf))
        r, C, Fa = transport_model(opt, Fsed, hsml, kh, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ)
        var = 'OMP_opt'
    elif 'KH' in exp:
        opt, cov = curve_fit(lambda s_r, Kh: \
                             transport_model(0, Fsed, hsml, Kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(kh/10.,kh*10))
        r, C, Fa = transport_model(0, Fsed, hsml, opt, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ)
        var = 'kh_opt'
    elif 'KCH4' in exp:
        opt, cov = curve_fit(lambda s_r, ks: \
                             transport_model(0, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ,
                                             s_r, True), s_r, s_C,
                             bounds=(0, np.inf))
        r, C, Fa = transport_model(0, Fsed, hsml, kh, opt, R, dt, tf, Patm,
                                   Hcp, Rs, typ, Ac)
        var = 'kch4_opt'
    return r, C, Fa, opt, var

"""
def pross_transport(data, ds_param, mc_data, ds_data, clake, dt, tf, exp_name):
    ds_data: Concentrations from DelSontro
    ds_param: Results from DelSontro
    data: Measured concentrations
    mc_data: Montercarlo results data

    allexp = dict()
    optres = []
    for exp in exp_name:
        var_lake = []
        var_fa = []
        var_date = []
        var_opt = []
        allres = dict()
        logging.info('Processing experiment %s:', exp)
        for lake in data:
            ladate = dict()
            for date in data[lake]:
                logging.info('Processing data from lake %s on %s', lake, date)
                la_ds_data = ds_data[lake][date]
                kh = ds_param.loc[lake, date].Kh
                hsml = clake[lake][date][1]
                typ = clake[lake][date][5]
                A = clake[lake][date][0]*1E6 # Total Surface Area (m2)
                As = clake[lake][date][6]*1E6 # Area Sediment (m2)
                R = np.sqrt(A/np.pi)
                Rs = np.sqrt((A-As)/np.pi)
                Ac = As/(np.pi*2*R*hsml)
                ks = ds_param.loc[lake, date].kch4
                Patm = ds_param.loc[lake, date].Patm
                Hcp = ds_param.loc[lake, date].Hcp
                #R = clake[lake][date][3]
                #R = data[lake][date].index.max()
                sdata = data[lake][date]
                newdate = date[0:4] +'-'+date[4:6] + '-' +date[6:]
                Fsed = mc_data.loc[lake, newdate].SedF_avg
                OMP = mc_data.loc[lake, newdate].OMP_avg
                varOMP = [OMP, OMP, OMP]
                varKh = [kh, kh, kh]
                varFsed = [Fsed, Fsed, Fsed]
                vark = [ks, ks, ks]
                test = np.array([1, 0.5, 2])
                if exp == 'Kh':
                    varKh = varKh * test
                elif exp == 'k':
                    vark = varK * test
                elif exp == 'Fsed':
                    varFsed = varFsed * test
                elif exp == 'OMP':
                    varOMP = varOMP * test
                if 'Sens' in exp:
                    r1, C, Fa1 = transport_model(varOMP[0], varFsed[0], hsml, varKh[0],
                                                vark[0], R, dt, tf, Patm, Hcp, Rs, typ)
                    r2, C_05, Fa2 = transport_model(varOMP[1], varFsed[1], hsml, varKh[1],
                                                   vark[1], R, dt, tf, Patm, Hcp, Rs, typ)
                    r, C_2, Fa3 = transport_model(varOMP[2], varFsed[2], hsml, varKh[2],
                                                 vark[2], R, dt, tf, Patm, Hcp, Rs, typ)
                    if exp == 'Kh':
                        f1 = interp1d(r1, C, kind='cubic')
                        f2 = interp1d(r2, C_05, kind='cubic')
                        C = f1(r)
                        C_05 = f2(r)

                    datares = {'C': C, 'C_05': C_05, 'C_2': C_2}
                elif 'Peeters' in exp:
                    r1, C1, Fa1 = transport_model(0, 0, hsml, kh, 1, R, dt, tf,
                            Patm, Hcp, Rs, typ, Ac, 'Peeters')
                    r2, C2, Fa2 = transport_model(0, 0, hsml, kh, 1, R, dt, tf,
                            Patm, Hcp, Rs, typ, Ac, 'CO')
                    print(C1.mean())
                    print(C2.mean())
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(1,1,figsize=(5,3), tight_layout=True)
                    ax.plot(r1, C1, label='Peeters')
                    ax.plot(r2, C2, label='CO')
                    ax.set_xlabel('Distance from shore (m)')
                    ax.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
                    plt.legend()
                    fig.savefig('Fsed_0_OMP_0_k_1.png', format='png', dpi=300)
                    plt.show()
                    pdb.set_trace()
                elif 'Opt' in exp:
                    r, C, Fa, opt = opt_test(exp, sdata, la_ds_data, OMP, Fsed, hsml, kh, ks, R, dt, tf, Patm, Hcp, Rs, Ac, typ)
                    var_fa.append(Fa)
                    var_opt.append(opt[0])
                    var_lake.append(lake)
                    var_date.append(date)
                    datares = {'C': C}
                datares = pd.DataFrame(datares, index=r)
                ladate.update({date: datares})
            allres.update({lake: ladate})
        if 'Opt' in exp:
            if not len(optres):
                optres = {'Lake': var_lake, 'Date': var_date}
                optres = pd.DataFrame(optres)
            optres[exp] = var_opt
            optres['Fa_'+exp] = var_fa
        allexp.update({exp: allres})
    if 'Opt' in exp:
        optres = optres.set_index(['Lake', 'Date'])
    return allexp, optres
"""

