#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import logging
#import multiprocessing

import numpy as np

import pandas as pd
import scr.model as mo
from scipy.interpolate import interp1d
from scr.filter import filterdata
from scr.functions import (Khmodel, average_inputs, desvstd_inputs, kch4_model,
                           param_outputs)
from scr.montecarlo import gammadist, normaldist

# pool = multiprocessing.Pool(4)

def process_data(t_data, dis_data, mc_data, model_run, lakeparam, pool):
    """Run models for transect.# {{{

    Parameters
    ----------
    t_data : Transect data
    dis_data : Dissolution data
    mc_data : Mass balance data from montecarlo simulation
    model_run : Run configuration section from config_model.yml
    paramlake : Lakes parameters input from data_lake.yml file

    Returns
    -------
    TODO
    """# }}}
    allres = dict()
    r_lake = []
    r_date = []
    params = []
    model_conf = model_run['ConfModel']
    for k, lake in enumerate(t_data):
        ladate = dict()
        for j, date in enumerate(t_data[lake]):
            logging.info('Processing data from lake %s on %s', lake, date)
            surf_area, zsml, lenghtscale, radius, filt, typ, sed_area, Kz, Chyp = lakeparam[
                lake][date]
            # Filtering transect data
            f_tdata = filterdata(t_data, lake, date, filt)
            # Getting bubble dissolution data
            # Diffusive Emissions transect - k model
            model_kch4, model_Fa, Hcp, Patm = kch4_model(f_tdata, model_conf['k600_model'],
                                                         lake, surf_area, False)
            sources_avg, sources_fr = average_inputs(mc_data, dis_data, lake, date)
            sources_std = desvstd_inputs(mc_data, dis_data, lake, date)

            # Parameters for model
            Asurf = surf_area * 1E6  # Planar surface area [m2]
            Ased = sed_area * 1E6  # Sediment area
            R = np.sqrt(Asurf / np.pi)
            Kh = Khmodel(R, model_conf['Kh_model'])
            Rs = np.sqrt((Asurf - Ased) / np.pi)
            if typ == 'E':
                R = t_data[lake][date].index.values.max()  # transect lenght
                if lake == 'Baldegg':
                    coef = [
                        3.87843E-6, -5.07162E-4, 2.43899E-2, -4.79714E-1, 5.999893, -6.17280
                    ]
                    Rs = coef[0] * zsml**5 + coef[1] * zsml**4 + coef[2] * zsml**3 + coef[
                        3] * zsml**2 + coef[4] * zsml**1 + coef[5]

            modelparam = pd.DataFrame(
                {
                    'Radius': R,
                    'Rs': Rs,
                    'Asurf': Asurf,
                    'Hsml': zsml,
                    'Kh': Kh,
                    'kch4': model_kch4,
                    'Type': typ,
                    'Patm': Patm,
                    'Hcp': Hcp,
                    'Kz': Kz,
                    'Chyp': Chyp
                }, index=[0])
            if sources_fr is not None:
                Rdis = sources_fr['Diss [micro-mol/m3/d]'].mean() / 1000
            else:
                Rdis = 0
            if model_run['MonteCarlo']['perform']:
                if model_conf['mode_model']['mode'] == 'OPT':
                    logging.info('Performing Monte Carlo Simulations')
                    mcs_n = model_run['MonteCarlo']['N']
                    mcs_omp = montecarlo(lake, surf_area, f_tdata, modelparam, model_conf, sources_fr, model_run, sources_std, sources_avg, pool)
# {{{
                    # for i in range(model_run['MonteCarlo']['N']):
                    #     mcs_fa = gammadist(sources_avg['SurfF'], sources_std['SurfF'], 1)
                    #     mcs_fs = gammadist(sources_avg['Fsed'], sources_std['Fsed'], 1)
                    #     mcs_fz = normaldist(sources_avg['Fhyp'], sources_std['Fhyp'], 1)
                    #     sources_mcs = pd.DataFrame({'SurfF': mcs_fa, 'Fsed': mcs_fs, 'Fhyp': mcs_fz}, index=[0])
                    #     _, _, _, opt, varname_opt = mo.opt_test(f_tdata, sources_mcs, sources_fr, modelparam, model_conf, levellog=10)
                    #     mcs_omp.append(opt[0])}}}
                    mcs_date = [date]*mcs_n
                    mcs_lake = [lake]*mcs_n
                    res_mcs = pd.DataFrame({'Lake': mcs_lake, 'Date': mcs_date, 'mcs_omp': mcs_omp})
                    if j == 0:
                        mcs_omp_date = res_mcs
                    else:
                        mcs_omp_date = pd.concat([mcs_omp_date, res_mcs])
            elif model_conf['mode_model']['mode'] == 'OPT':
                logging.info('Looking for Opt value')
                rx, Cx, Fa, opt, varname_opt = mo.opt_test(f_tdata, sources_avg, sources_fr,
                                                           modelparam, model_conf)
                datares = {'C': Cx}
                Cxavg = Cx.mean()
                param, nameres = param_outputs(Cxavg, sources_avg, Rdis, f_tdata,
                                               modelparam, model_conf, opt, Fa, varname_opt)
                params.append(param)
            elif model_conf['mode_model']['mode'] == 'EVAL':
                if model_conf['mode_model']['var'] == 'OMP':
                    OMP = sources_avg.OMP.values[0]
                else:
                    OMP = 0
                Fsed = sources_avg.Fsed
                Fhyp = sources_avg.Fhyp
                SurfF = sources_avg.SurfF
                Cavg = f_tdata.CH4.mean()
                rx, Cx, Fa = mo.transport_model(OMP, Fsed, Fhyp, sources_fr, Kh, model_kch4,
                                                modelparam, model_conf)
                Cxavg = Cx.mean()
                datares = {'C': Cx}
                param, nameres = param_outputs(Cxavg, sources_avg, Rdis, f_tdata,
                                               modelparam, model_conf)
                params.append(param)
            if not model_run['MonteCarlo']['perform']:
                datares = pd.DataFrame(datares, index=rx)
                ladate.update({date: datares})
                r_lake.append(lake)
                r_date.append(date)
        if not model_run['MonteCarlo']['perform']:
            allres.update({lake: ladate})
        else:
            if k == 0:
                mcs_omp_lake = mcs_omp_date
            else:
                mcs_omp_lake = pd.concat([mcs_omp_lake, mcs_omp_date])
    if not model_run['MonteCarlo']['perform']:
        pindex = [np.array(r_lake), np.array(r_date)]
        paramres = pd.DataFrame(data=params, columns=nameres, index=pindex)
        paramres.index.names = ['Lake', 'Date']
        return allres, paramres
    else:
        return mcs_omp_lake, None

def montecarlo(lake, surf_area, f_tdata, modelparam, model_conf, sources_fr, model_run, sources_std, sources_avg, pool):
    mcs_n = model_run['MonteCarlo']['N']
    mcs_fa = gammadist(sources_avg['SurfF'], sources_std['SurfF'], mcs_n)
    mcs_fs = gammadist(sources_avg['Fsed'], sources_std['Fsed'], mcs_n)
    mcs_fz = normaldist(sources_avg['Fhyp'], sources_std['Fhyp'], mcs_n)
    mcs_kch4 = kch4_model(f_tdata, model_conf['k600_model'], lake, surf_area, mcs_fa, True)
    partial_mcs = functools.partial(mo.opt_test, f_tdata, sources_fr, modelparam, model_conf)
    task = [*zip(mcs_kch4, mcs_fs, mcs_fz)]
    res = pool.map(partial_mcs, task)
    opt = [aux[3][0] for aux in res]
    # sources_mcs = pd.DataFrame({'SurfF': mcs_fa, 'Fsed': mcs_fs, 'Fhyp': mcs_fz}, index=[0])
    # _, _, _, opt, _= mo.opt_test(f_tdata, sources_fr, modelparam, model_conf, sources_mcs)
    return opt
