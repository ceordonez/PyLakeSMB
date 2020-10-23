#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pandas as pd

import DelSontro.scr.model_delsontr as ds
import Peeters.scr.model as pe
import scr.model as co
from scr.functions import *

from scipy.interpolate import interp1d

def process_data(t_data, clake, Kh_model, k600_model, mc_data, dt, t_end, models):
    """ Function to run models for transect
    t_data: Transect data
    clake: Lakes input from config_lake file
    Kh_model: Horizontal diffusivity model (Kh)
    mc_data: Mass balance data from montecarlo simulation
    dt: Time interval (days)
    t_end: Time end (days)
    models: Models to run
    """
    modeldata = dict()
    modelparam = dict()
    for mod in models:
        mod = '-'.join([mod, k600_model])
        logging.info('Processing data %s model', mod)
        mod = mod.upper()
        allres = dict()
        ladate = dict()
        r_lake = []
        r_date = []
        params = []
        for lake in t_data:
            for date in t_data[lake]:
                logging.info('Processing data from lake %s on %s', lake, date)
                A, zsml, L, r, filt, typ = clake[lake][date][0:6]
                if filt: #Filter data
                    ld_data = t_data[lake][date].reset_index()
                    fdata = ld_data.drop(filt)
                    fdata = fdata.set_index(['Distance'])
                else:
                    fdata = t_data[lake][date]
                # Getting data from transect file
                tC = fdata.CH4
                T = fdata.Temp
                U10 = fdata.U10.mean()
                Hch4 = Hcp(T).mean() # umol/l/Pa
                Patm = fdata.CH4_atm.mean() # Atmospheric Partial Pressure (Pa)
                Fa_fc = fdata.Fa_fc.mean() # Flux from chambers transect
                Cavg = tC.mean() # mean surface concentration
                kch4_fc = fdata.Fa_fc/(Cavg - Hch4*Patm) # kch4 from flux chambers
                kch4_fc = kch4_fc.mean()
                # Processing data transect main parameters
                if 'kAVG' in k600_model:
                    kch4 = kch4_fc
                    if np.isnan(kch4):
                        k600 = f_k600(U10, A, 'kOPT', lake)
                        kch4 = f_kch4(T.mean(), k600, U10)
                    if '05' in k600_model:
                        kch4 = 0.5*kch4
                    elif '15' in k600_model:
                        kch4 = 1.5*kch4
                else:
                    k600 = f_k600(U10, A, k600_model, lake)
                    kch4 = f_kch4(T.mean(), k600, U10)
                Tavg = T.mean()
                Kh = Khmodel(L, Kh_model)
                # Diffusive Emissions transect - k model
                Fa = kch4*(tC - Hch4*Patm) # Flux k model data transect
                Fa = np.mean(Fa)

                if 'DELSONTRO' in mod:
                    Cx, x, lda,_ = ds.delsontro(tC, L, kch4, r, 0, zsml, typ, Kh)
                    Fads = kch4*(Cx - Hch4*Patm) # Flux from model DelSontro
                    Fads = np.mean(Fads)
                    datares = pd.DataFrame({'C':Cx}, index=x)
                    ladate.update({date: datares})
                    Cxavg = Cx.mean()
                    params.append([Cxavg, Cavg, k600, kch4, Tavg, U10, Fa, Fads, Fa_fc, kch4_fc, Patm,
                        Hch4, Kh])
                    nameres = ['Cmod', 'Cavg', 'k600', 'kch4', 'Temp', 'U10', 'Fa', 'Fa_ds', 'Fa_fc',
                            'kch4_fc', 'Patm','Hcp','Kh']

                elif 'CO' in mod or 'PEETERS' in mod:
                    newdate = date[0:4] +'-'+date[4:6] + '-' +date[6:]
                    Fsed = mc_data.loc[lake, newdate].SedF_avg
                    OMP = mc_data.loc[lake, newdate].OMP_avg
                    SurfF = mc_data.loc[lake, newdate].SurfF_avg
                    A = A*1E6 # Planar surface area
                    As = clake[lake][date][6]*1E6 #Sediment area
                    R = np.sqrt(A/np.pi)
                    if typ == 'E':
                        R = t_data[lake][date].index.values.max() # transect lenght
                    if 'CO' in mod:
                        if 'CORR' in mod:# {{{
                            Ac = As/(np.pi*2*R*zsml)
                        else:
                            Ac = 1
                        if 'OPT' in mod:
                            rx, Cx, Fa, opt, varname_opt = co.opt_test(mod, fdata, OMP, Fsed, zsml, Kh,
                                    kch4, R, dt, t_end, Patm, Hch4, Ac, typ)
                            datares = {'C': Cx}
                            Cxavg = Cx.mean()
                            params.append([opt[0], Fa, Cxavg, Cavg, OMP, Fsed, SurfF, zsml, Kh, kch4,
                                Ac, R, t_end])
                            nameres = [varname_opt, 'Fa_opt', 'Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF',
                                    'Hsml', 'Kh', 'kch4', 'Ac', 'R', 't_end']
                        elif 'SENS' in mod:
                            varOMP = [OMP, OMP, OMP]
                            varKh = [Kh, Kh, Kh]
                            varFsed = [Fsed, Fsed, Fsed]
                            vark = [kch4, kch4, kch4]
                            test = np.array([1, 0.5, 2])
                            if 'KH' in mod:
                                varKh = varKh * test
                            elif 'KCH4' in mod:
                                vark = varK * test
                            elif 'FSED' in mod:
                                varFsed = varFsed * test
                            elif 'OMP' in mod:
                                varOMP = varOMP * test
                            Rs = np.sqrt((A-As)/np.pi)
                            rx1, Cx1, Fa1 = pe.transport_model(0, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, Rs, typ)
                            r1, C, Fa1 = pe.transport_model(varOMP[0], varFsed[0], zsml, varKh[0],
                                    vark[0], R, dt, t_end, Patm, Hch4, Rs, typ)
                            r2, C_05, Fa2 = pe.transport_model(varOMP[1], varFsed[1], zsml, varKh[1],
                                    vark[1], R, dt, t_end, Patm, Hch4, Rs, typ)
                            r, C_2, Fa3 = pe.transport_model(varOMP[2], varFsed[2], zsml, varKh[2],
                                    vark[2], R, dt, t_end, Patm, Hch4, Rs, typ)
                            params.append([Fa1, Fa2, Fa3])
                            nameres = (['Fa', '0.5Fa', '2Fa'])
                            if 'KH' in mod:
                                f1 = interp1d(r1, C, kind='cubic')
                                f2 = interp1d(r2, C_05, kind='cubic')
                                C = f1(r)
                                C_05 = f2(r)
                            datares = {'C': C, 'C_05': C_05, 'C_2': C_2}
                        else:
                            # Run model with inputs values
                            rx, Cx, Fa = co.transport_model(OMP, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, typ, Ac)
                            datares = {'C': Cx}
                            Cxavg = Cx.mean()
                            params.append([OMP, Fsed, SurfF, Cxavg, Cavg, zsml, Kh, kch4, Ac, R,
                                t_end])
                            nameres = ['OMP', 'Fsed', 'SurfF', 'Cmod', 'Cavg', 'Hsml', 'Kh', 'kch4',
                                    'Ac', 'R', 't_end']# }}}
                    elif 'PEETERS' in mod:
                        Rs = np.sqrt((A-As)/np.pi)
                        if typ == 'E':
                            if lake == 'Baldegg':
                                coef = [3.87843E-6, -5.07162E-4, 2.43899E-2, -4.79714E-1, 5.999893, -6.17280]
                            Rs = coef[0]*zsml**5 + coef[1]*zsml**4 + coef[2]*zsml**3 + coef[3]*zsml**2 + coef[4]*zsml**1 + coef[5]
                        if '-OPT' in mod:
                            logging.info('Looking for Opt value')
                            rx, Cx, Fa, opt, varname_opt = pe.opt_test(mod, fdata, OMP, Fsed, zsml, Kh,
                                    kch4, R, dt, t_end, Patm, Hch4, Rs, typ)
                            datares = {'C': Cx}
                            Cxavg = Cx.mean()
                            if 'FSED' in mod:
                                params.append([opt[0], Fa, Cxavg, Cavg, 0, Fsed, SurfF, zsml, Kh, kch4,
                                    R, Rs, t_end])
                                nameres = [varname_opt, 'Fa_opt', 'Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF',
                                        'Hsml', 'Kh', 'kch4', 'R', 'Rs', 't_end']
                            else:
                                params.append([opt[0], Fa, Cxavg, Cavg, OMP, Fsed, SurfF, zsml, Kh, kch4,
                                    R, Rs, t_end])
                                nameres = [varname_opt, 'Fa_opt', 'Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF',
                                        'Hsml', 'Kh', 'kch4', 'R', 'Rs', 't_end']
                        elif 'COMP' in mod:
                            kch4 = 0
                            Fsed = 1
                            Ac = As/(np.pi*2*R*zsml)
                            rx1, Cx1, Fa1 = pe.transport_model(0, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, Rs, typ)
                            rx2, Cx2, Fa2 = co.transport_model(0, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, typ, Ac)
                            Cxavg1 = Cx1.mean()
                            Cxavg2 = Cx2.mean()
                            import matplotlib.pyplot as plt
                            print(Cxavg1,Cxavg2)
                            plt.figure(figsize=(5,3))
                            plt.plot(rx1, Cx1, label = 'Peeters')
                            plt.plot(rx2, Cx2, label = 'CO')
                            plt.xlabel('Distance from shore (m)')
                            plt.legend()
                            plt.ylabel(u'CH$_4$ (\u03BCmol/l)')
                            plt.tight_layout()
                            plt.savefig('Comparison_CO-Peeters.png', format='png', dpi=300)
                            plt.show()
                            __import__('pdb').set_trace()
                            params.append([Cxavg, Cavg, 0, Fsed, SurfF, zsml, Kh, kch4, R, Rs,
                                t_end])
                            nameres = ['Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh', 'kch4',
                                    'R', 'Rs', 't_end']
                            datares = {'C': Cx}
                        elif 'SENS' in mod:
                            varOMP = [OMP, OMP, OMP]
                            varKh = [Kh, Kh, Kh]
                            varFsed = [Fsed, Fsed, Fsed]
                            vardt = [dt, dt, dt]
                            vark = [kch4, kch4, kch4]
                            test = np.array([1, 0.5, 2])
                            if 'KH' in mod:
                                varKh = varKh * test
                                vardt = vardt * test
                            elif 'KCH4' in mod:
                                vark = vark * test
                            elif 'FSED' in mod:
                                varFsed = varFsed * test
                            elif 'OMP' in mod:
                                varOMP = varOMP * test
                            Rs = np.sqrt((A-As)/np.pi)
                            r1, C, Fa1 = pe.transport_model(varOMP[0], varFsed[0], zsml, varKh[0],
                                    vark[0], R, vardt[0], t_end, Patm, Hch4, Rs, typ)
                            r2, C_05, Fa2 = pe.transport_model(varOMP[1], varFsed[1], zsml, varKh[1],
                                    vark[1], R, vardt[1], t_end, Patm, Hch4, Rs, typ)
                            rx, C_2, Fa3 = pe.transport_model(varOMP[2], varFsed[2], zsml, varKh[2],
                                    vark[2], R, vardt[2], t_end, Patm, Hch4, Rs, typ)
                            Cxavg = C.mean()
                            datares = {'r1': r1,'C': C, 'r2': r2, 'C_05': C_05, 'r3': rx, 'C_2': C_2}
                            params.append([Cxavg, Cavg, 0, Fsed, SurfF, zsml, Kh, kch4, R, Rs,
                                t_end])
                            nameres = ['Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh', 'kch4',
                                    'R', 'Rs', 't_end']
                        else:
                            if 'OMP' in mod:
                                OMP = OMP
                            else:
                                OMP = 0
                            rx, Cx, Fa = pe.transport_model(OMP, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, Rs, typ)
                            Cxavg = Cx.mean()
                            params.append([Cxavg, Cavg, OMP, Fsed, SurfF, zsml, Kh, kch4, R, Rs,
                                t_end])
                            nameres = ['Cmod', 'Cavg', 'OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh', 'kch4',
                                    'R', 'Rs', 't_end']
                            datares = {'C': Cx}
                    if 'SENS' not in mod:
                        datares = pd.DataFrame(datares, index=rx)
                    ladate.update({date: datares})
                r_lake.append(lake)
                r_date.append(date)
            allres.update({lake: ladate})
        pindex = [np.array(r_lake), np.array(r_date)]
        paramres = pd.DataFrame(data = params, columns=nameres, index=pindex)
        paramres.index.names =  ['Lake', 'Date']
        modeldata[mod] = allres
        modelparam[mod] = paramres
    return modeldata, modelparam
