#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
import logging
import pandas as pd

import DelSontro.scr.model_delsontr as ds
import Peeters.scr.model as pe
import scr.model as co
from scr.functions import *

def process_data(t_data, clake, Kh_model, mc_data, dt, t_end, models):
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
                kch4_fc = fdata.Fa_fc/(tC - Hch4*Patm) # kch4 from flux chambers
                kch4_fc = kch4_fc.mean()

                # Processing data transect main parameters
                k600 = f_k600(U10, A, 'VP')
                kch4 = f_kch4(T, k600, U10)
                Tavg = T.mean()
                Kh = Khmodel(L, Kh_model)
                # Diffusive Emissions transect - k model
                Fa = kch4*(tC - Hch4*Patm) # Flux k model data transect
                Fa = np.mean(Fa)

                if mod == 'DELSONTRO':
                    Cx, x, lda,_ = ds.delsontro(tC, L, kch4, r, 0, zsml, typ, Kh)
                    Fads = kch4*(Cx - Hch4*Patm) # Flux from model DelSontro
                    Fads = np.mean(Fads)
                    datares = pd.DataFrame({'CH4':Cx}, index=x)
                    ladate.update({date: datares})
                    params.append([k600, kch4, Tavg, U10, Fa, Fads, Fa_fc, kch4_fc, Cavg, Patm, Hch4, Kh])
                    nameres = ['k600', 'kch4', 'Temp', 'U10', 'Fa', 'Fa_ds', 'Fa_fc', 'kch4_fc', 'Cavg', 'Patm','Hcp','Kh']

                elif 'CO' in mod or 'PEETERS' in mod:
                    newdate = date[0:4] +'-'+date[4:6] + '-' +date[6:]
                    Fsed = mc_data.loc[lake, newdate].SedF_avg
                    OMP = mc_data.loc[lake, newdate].OMP_avg
                    SurfF = mc_data.loc[lake, newdate].SurfF_avg
                    A = A*1E6
                    As = clake[lake][date][6]*1E6
                    ## CHECK CASE ELONGATED SHAPE
                    R = np.sqrt(A/np.pi)
                    Rs = np.sqrt((A-As)/np.pi)
                    if 'CO' in mod:
                        if 'corr' in mod:
                            Ac = As/(np.pi*2*R*zsml)
                        else:
                            Ac = 1
                        if 'OPT' in mod:
                            r, C, Fa, opt, varname_opt = co.opt_test(mod, fdata, OMP, Fsed, zsml, Kh,
                                    kch4, R, dt, t_end, Patm, Hch4, Rs, Ac, typ)
                            datares = {'C': C}
                            params.append([opt[0], Fa, OMP, Fsed, SurfF, zsml, Kh, kch4, Ac, R, Rs,
                                t_end])
                            nameres = [varname_opt, 'Fa_opt', 'OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh',
                                    'kch4', 'Ac', 'R', 'Rs', 't_end']
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
                            r1, C, Fa1 = co.transport_model(varOMP[0], varFsed[0], zsml, varKh[0],
                                    vark[0], R, dt, t_end, Patm, Hch4, Rs, Ac, typ)
                            r2, C_05, Fa2 = co.transport_model(varOMP[1], varFsed[1], zsml, varKh[1],
                                    vark[1], R, dt, t_end, Patm, Hch4, Rs, Ac, typ)
                            r, C_2, Fa3 = co.transport_model(varOMP[2], varFsed[2], zsml, varKh[2],
                                    vark[2], R, dt, t_end, Patm, Hch4, Rs, Ac, typ)
                            params.append([Fa1, Fa2, Fa3])
                            nameres = (['Fa', '0.5Fa', '2Fa'])
                            if 'KH' in mod:
                                f1 = interp1d(r1, C, kind='cubic')
                                f2 = interp1d(r2, C_05, kind='cubic')
                                C = f1(r)
                                C_05 = f2(r)
                            datares = {'C': C, 'C_05': C_05, 'C_2': C_2}
                        else:
                            r, C, Fa = co.transport_model(OMP, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                    Patm, Hch4, Rs, Ac, typ)
                            datares = {'C': C}
                            params.append([OMP, Fsed, SurfF, zsml, Kh, kch4, Ac, R, Rs,
                                t_end])
                            nameres = ['OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh', 'kch4', 'Ac',
                                    'R', 'Rs', 't_end']
                    elif 'PEETERS' in mod:
                        r, C, Fa = pe.transport_model(OMP, Fsed, zsml, Kh, kch4, R, dt, t_end,
                                Patm, Hch4, Rs, typ)
                        params.append([OMP, Fsed, SurfF, zsml, Kh, kch4, R, Rs,
                            t_end])
                        nameres = ['OMP', 'Fsed', 'SurfF', 'Hsml', 'Kh', 'kch4', 'R',
                                'Rs', 't_end']
                        datares = {'C': C}
                    datares = pd.DataFrame(datares, index=r)
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
