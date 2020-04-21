#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import pdb
import logging

def transport_model(OMP, Fsed, hsml, kh, ks, R, dt, tf, Patm, Hcp, Rs, typ, Ac, mod='CO', x=None,
                    opt=False):
    dr = round(np.sqrt(kh*dt/0.25))
    t = np.arange(0, tf+dt, dt)
    Ma = 0
    if Fsed == 0: aux=1
    else: aux = 2
    r = np.arange(0, R+aux*dr, dr) # From 0 to R+dr
    C = np.ones((len(r),len(t)))*10 #*Patm*Hcp
    C[0,:] = C[1,0]
    for n in range(len(t)-1):
        for a in range(len(r)-2):
            i = len(r) - a - 2
            if r[i]>R:
                Fs = Fsed
                P = OMP
                k = 0
            else:
                P = OMP
                k = ks
                Fs = 0
#               if r[i] <= R:
#                  Fs = 0
#                  H = hsml
#              else:
#                  Fs = Fsed
#                  H = hsml/2.
#              k=ks
#              P=OMP
            if typ =='R':
                C[i,n+1] = (1/(dr**2))*kh*dt*(C[i+1,n] - 2*C[i,n] + C[i-1,n]) + \
                    kh*dt/(2*r[i]*dr)*(C[i+1,n] - C[i-1,n]) + \
                    C[i,n] - (C[i,n]-Patm*Hcp)*dt*k/hsml + Fs*dt*2*(R+dr)/(dr*(2*R+dr))*Ac +\
                    P*1E-3*dt
            elif typ == 'E':
                C[i,n+1] = (1/(dr**2))*kh*dt*(C[i+1,n] -2*C[i,n] + C[i-1,n]) + \
                    C[i,n] - (C[i,n]-Patm*Hcp)*dt*k/hsml + Fs*dt*2/dr +\
                    P*1E-3*dt
        C[0,n+1] = C[1,n+1]
        C[-1,n+1] = C[-2,n+1]
    r = R - r[:-aux]
    C = C[:-aux,-1]
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

def pross_transport(t_data, ds_param, mc_data, ds_data, clake, dt, tf, exp_name):
    """
    t_data: Measured transect concentrations
    ds_data: Concentrations from DelSontro
    ds_param: Results from DelSontro
    mc_data: Montercarlo results data
    """

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
                    """
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
                    """
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

def opt_test(exp, sdata, la_ds_data, OMP, Fsed, hsml, kh, ks, R, dt, tf, Patm, Hcp, Rs, Ac, typ):
    """
    sdata: Sampled data per lake per date
    la_ds_data: Data per lake per date from DelSontro"
    """

    s_r = sdata.index.values
    s_C = sdata.CH4.values
    if exp == 'Fsed-Opt-ds':
        ds_r = la_ds_data.index.values
        ds_C = la_ds_data.CH4.values
        opt, cov = curve_fit(lambda ds_r, Fsed: \
                             transport_model(0, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ, Ac, 'CO',
                                             ds_r, True),
                             ds_r, ds_C)
        r, C, Fa = transport_model(0, opt, hsml, kh, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ, Ac)
    elif exp == 'Fsed-Opt':
        opt, cov = curve_fit(lambda ds_r, Fsed: \
                             transport_model(0, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ, Ac, 'CO',
                                             s_r, True), s_r, s_C,
                              bounds=(0, np.inf))
        r, C, Fa = transport_model(0, opt, hsml, kh, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ, Ac)
    elif exp == 'OMP-Opt':
        opt, cov = curve_fit(lambda s_r, OMP: \
                             transport_model(OMP, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ, Ac, 'CO',
                                             s_r, True), s_r, s_C,
                             bounds=(0, np.inf))
        r, C, Fa = transport_model(opt, Fsed, hsml, kh, ks, R, dt, tf, Patm,
                                   Hcp, Rs, typ, Ac)
    elif exp == 'k-Opt':
        opt, cov = curve_fit(lambda s_r, ks: \
                             transport_model(0, Fsed, hsml, kh, ks,
                                             R, dt, tf, Patm, Hcp, Rs, typ, Ac, 'CO',
                                             s_r, True), s_r, s_C,
                             bounds=(0, np.inf))
        r, C, Fa = transport_model(0, Fsed, hsml, kh, opt, R, dt, tf, Patm,
                                   Hcp, Rs, typ, Ac)
    return r, C, Fa, opt
