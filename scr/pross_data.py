#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import logging

import numpy as np
import pandas as pd
import scr.model as mo
from scr.filter import filterdata
from scr.functions import (Khmodel, average_inputs, desvstd_inputs, kch4_model,
                           param_outputs, Hcp)
from scr.montecarlo import gammadist, normaldist


def process_data(t_data, d_data, f_data, conf_run, p_data, pool):
    """Run models for transect

    Parameters
    ----------
    t_data    : Transect data
    d_data    : Dissolution data
    f_data    : Mass balance data from montecarlo simulation
    conf_run  : Run configuration section from config_model.yml
    paramlake : Lakes parameters input from data_lake.yml file

    Returns
    -------
    TODO
    """

    allres = dict()
    r_lake = []
    r_date = []
    params = []
    model_conf = conf_run['ConfModel']
    for k, lake in enumerate(conf_run['lakes']):
        ladate = dict()
        for j, date in enumerate(conf_run['lakes'][lake]):
            logging.info('Processing data from lake %s on %s', lake, date)
            date = pd.to_datetime(date, format='%Y%m%d')

            ## Selecting data for lake and date
            p_lddata = p_data.loc[((p_data.Lake == lake) & (p_data.Date == date))]
            t_lddata = t_data.loc[((t_data.Lake == lake) & (t_data.Date == date))]
            d_lddata = d_data.loc[((d_data.Lake == lake) & (d_data.Date == date))]
            f_lddata = f_data.loc[((f_data.Lake == lake) & (f_data.Date == date))]

            # Parameters for model
            Aa = p_lddata.Aa * 1E6  # Planar surface area [m2]
            As = p_lddata.As * 1E6  # Sediment area [m2]
            p_lddata.insert(len(p_lddata.columns), 'R', np.sqrt(Aa / np.pi))
            p_lddata.insert(len(p_lddata.columns), 'Kh', Khmodel(p_lddata['R'].values, model_conf['Kh_model']))
            p_lddata.insert(len(p_lddata.columns), 'Rs', np.sqrt((Aa - As) / np.pi))
            p_lddata.insert(len(p_lddata.columns), 'Hcp', Hcp(t_lddata.Tw.mean()))
            p_lddata.insert(len(p_lddata.columns), 'pCH4atm', t_lddata.pCH4atm.mean())
            p_lddata.insert(len(p_lddata.columns), 'kch4', kch4_model(t_lddata, model_conf['k600_model'], p_lddata, False))

            if d_data is not None:
                Rdis = d_lddata['Diss'].mean() / 1000
            else:
                Rdis = 0

            if conf_run['MonteCarlo']['perform']:
                if model_conf['mode_model']['mode'] == 'OPT':
                    logging.info('Performing Monte Carlo Simulations')
                    mcs_n = conf_run['MonteCarlo']['N']
                    mcs_omp = montecarlo(conf_run, f_lddata, p_lddata, d_lddata, t_lddata, pool)
                    mcs_date = [date]*mcs_n
                    mcs_lake = [lake]*mcs_n
                    res_mcs = pd.DataFrame({'Lake': mcs_lake, 'Date': mcs_date, 'mcs_omp': mcs_omp})
                    if j == 0:
                        mcs_omp_date = res_mcs
                    else:
                        mcs_omp_date = pd.concat([mcs_omp_date, res_mcs])

            elif model_conf['mode_model']['mode'] == 'OPT':
                logging.info('Looking for Opt value')
                inputs = [p_lddata.kch4.values[0], f_lddata.Fs_avg.values[0], f_lddata.Fz_avg.values[0]]
                rx, Cx, Fa, opt, varname_opt = mo.opt_test(model_conf, t_lddata, d_lddata, p_lddata, inputs)
                datares = {'C': Cx}
                Cxavg = Cx.mean()
                param, nameres = param_outputs(Cxavg, f_lddata, Rdis, t_lddata,
                        p_lddata, model_conf, opt, Fa, varname_opt)
                params.append(param)

            elif model_conf['mode_model']['mode'] == 'EVAL':
                if model_conf['mode_model']['var'] == 'OMP':
                    OMP = f_lddata.P_avg.values[0]
                else:
                    OMP = 0
                Fsed = f_lddata.Fs_avg
                Fhyp = f_lddata.Fz_avg
                rx, Cx, Fa = mo.transport_model(OMP, Fsed, Fhyp, d_lddata, p_lddata, model_conf)
                Cxavg = Cx.mean()
                datares = {'C': Cx}
                param, nameres = param_outputs(Cxavg, f_lddata, Rdis, t_lddata,
                        p_lddata, model_conf)
                params.append(param)

            if not conf_run['MonteCarlo']['perform']:
                datares = pd.DataFrame(datares, index=rx)
                ladate.update({date: datares})
                r_lake.append(lake)
                r_date.append(date)

        if not conf_run['MonteCarlo']['perform']:
            allres.update({lake: ladate})
        else:
            if k == 0:
                mcs_omp_lake = mcs_omp_date
            else:
                mcs_omp_lake = pd.concat([mcs_omp_lake, mcs_omp_date])

    if not conf_run['MonteCarlo']['perform']:
        pindex = [np.array(r_lake), np.array(r_date)]
        paramres = pd.DataFrame(data=params, columns=nameres, index=pindex)
        paramres.index.names = ['Lake', 'Date']
        return allres, paramres

    else:
        return mcs_omp_lake, None

def montecarlo(conf_run, f_lddata, p_lddata, d_lddata, t_lddata, pool):

    model_conf = conf_run['ConfModel']
    mcs_n = conf_run['MonteCarlo']['N']
    mcs_fa = gammadist(f_lddata['Fa_avg'], f_lddata['Fa_std'], mcs_n)
    mcs_fs = gammadist(f_lddata['Fs_avg'], f_lddata['Fs_std'], mcs_n)
    mcs_fz = normaldist(f_lddata['Fz_avg'], f_lddata['Fz_std'], mcs_n)
    mcs_kch4 = kch4_model(t_lddata, model_conf['k600_model'], p_lddata, True, mcs_fa)
    partial_mcs = functools.partial(mo.opt_test, model_conf, t_lddata, d_lddata, p_lddata)
    task = [*zip(mcs_kch4, mcs_fs, mcs_fz)]
    res = pool.map(partial_mcs, task)
    opt = [aux[3][0] for aux in res]
    return opt
