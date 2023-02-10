#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import logging

import numpy as np
import pandas as pd
import scr.model as mo
from scr.functions import Khmodel, kch4_model, param_outputs, Hcp
from scr.montecarlo import gammadist, normaldist


def process_data(conf_run, data, pool):
    """Run models for transect

    Parameters
    ----------
    conf_run : dict
               Configuration information from config_model.yml
    data : tuple
           (ddata, fdata, pdata, tdata)
           ddata is a DataFrame with bubble dissolution data
           fdata is a DataFrame with fluxes data
           pdata is a DataFrame with lakes parameters
           tdata is a DataFrame with transect data
    pool : core numer to run montecarlo simulations (default all cores of computer)
           see main.py file to change it

    Returns
    -------
    modeldata : DataFrame
                Not Montecarlo simulation case return the imulated surface concentration along the transect
                Montecarlo simulation return the optimun value of variable defined in var
    modelparam : DataFrame, None
                 Not Montecarlo simulation case return the optimum value or/and average results from the simulation
                 Montecarlo simulation case return None
    """

    if conf_run['Montecarlo']['perform']:
        modeldata = process_montecarlo(conf_run, data, pool)
        modelparam = None
    else:
        modeldata, modelparam = process_opteval(conf_run, data)

    return modeldata, modelparam

def process_opteval(conf_run, data):
    allres = []
    paramres = []
    model_conf = conf_run['ConfModel']
    for lake in conf_run['Lakes']:
        modelresdate = []
        paramdate = []
        for date in conf_run['Lakes'][lake]:
            logging.info('Processing data from lake %s on %s', lake, date)
            ddate = pd.to_datetime(date, format='%Y%m%d')
            lddata = selec_lakedate(model_conf, data, ddate, lake)
            if lddata[0] is not None:
                fdis = lddata[0]['Diss'].mean() / 1000
            else:
                fdis = 0

            if model_conf['mode_model']['mode'] == 'OPT':
                logging.info('Looking for Opt value')
                inputs = [lddata[2].kch4.values[0], lddata[1].Fs_avg.values[0],
                        lddata[1].Fz_avg.values[0]]
                rx, model_c, Fa, opt, varname_opt = mo.opt_test(model_conf, lddata, inputs)
                model_cavg = model_c.mean()
                param, nameres = param_outputs(model_cavg, lddata[1], fdis, lddata[3],
                        lddata[2], model_conf, opt, Fa, varname_opt)

            elif model_conf['mode_model']['mode'] == 'EVAL':
                if model_conf['mode_model']['var'] == 'PNET':
                    pnet = lddata[1].P_avg.values[0]
                else:
                    pnet = 0
                fsed = lddata[1].Fs_avg
                fhyp = lddata[1].Fz_avg
                k_h = lddata[2].Kh.values[0]
                kch4 = lddata[2].kch4.values[0]
                rx, model_c, Fa = mo.transport_model(pnet, fsed, fhyp, lddata[0], k_h, kch4, lddata[2], model_conf)
                Cxavg = model_c.mean()
                param, nameres = param_outputs(Cxavg, lddata[1], fdis, lddata[3],
                        lddata[2], model_conf)
            param.insert(0, ddate)
            nameres.insert(0, 'Date')
            paramdate.append(param)
            modelres = {'Date': ddate, 'Distance': rx, 'Cmodel': model_c}
            modelres = pd.DataFrame(modelres)
            modelresdate.append(modelres)

        params = pd.DataFrame(data=paramdate, columns=nameres)
        params.insert(0, 'Lake', lake)
        modelres = pd.concat(modelresdate)
        modelres.insert(0, 'Lake', lake)
        allres.append(modelres)
        paramres.append(params)

    paramres = pd.concat(paramres)
    allres = pd.concat(allres)
    return allres, paramres

def process_montecarlo(conf_run, data, pool):

    model_conf = conf_run['ConfModel']
    logging.info('Performing Monte Carlo Simulations')
    mcs_pnet_lake = []

    for lake in conf_run['Lakes']:
        mcs_pnet_date = []

        for date in conf_run['Lakes'][lake]:
            logging.info('Processing data from lake %s on %s', lake, date)
            ddate = pd.to_datetime(date, format='%Y%m%d')
            lddata = selec_lakedate(model_conf, data, ddate, lake)
            mcs_pnet = montecarlo(conf_run, lddata, pool)
            varname = 'mcs_%s' % model_conf['mode_model']['var']
            res_mcs = pd.DataFrame({'Lake': lake, 'Date': ddate, varname: mcs_pnet})
            mcs_pnet_date.append(res_mcs)
        mcs_pnet_lake.append(pd.concat(mcs_pnet_date))
    mcs_pnet_lake = pd.concat(mcs_pnet_lake)
    return mcs_pnet_lake

def selec_lakedate(model_conf, data, date, lake):

    p_data = data[2]
    t_data = data[3]
    f_data = data[1]
    d_data = data[0]

    ## Selecting data for lake and date
    p_lddata = p_data.loc[((p_data.Lake == lake) & (p_data.Date == date))]
    t_lddata = t_data.loc[((t_data.Lake == lake) & (t_data.Date == date))]
    d_lddata = d_data.loc[((d_data.Lake == lake) & (d_data.Date == date))]
    f_lddata = f_data.loc[((f_data.Lake == lake) & (f_data.Date == date))]

    # Parameters for model
    p_lddata.insert(len(p_lddata.columns), 'R', np.sqrt(p_lddata.Aa * 1E6 / np.pi))
    p_lddata.insert(len(p_lddata.columns), 'Kh',
            Khmodel(p_lddata['R'].values, model_conf['Kh_model']))
    p_lddata.insert(len(p_lddata.columns), 'Rs',
            np.sqrt((p_lddata.Aa - p_lddata.As) * 1E6 / np.pi))
    p_lddata.insert(len(p_lddata.columns), 'Hcp', Hcp(t_lddata.Tw.mean()))
    p_lddata.insert(len(p_lddata.columns), 'pCH4atm', t_lddata.pCH4atm.mean())
    p_lddata.insert(len(p_lddata.columns), 'kch4',
            kch4_model(t_lddata, model_conf['k600_model'], p_lddata, False))
    lddata = (d_lddata, f_lddata, p_lddata, t_lddata)

    return lddata

def montecarlo(conf_run, lddata, pool):

    f_lddata = lddata[1]
    p_lddata = lddata[2]
    t_lddata = lddata[3]
    model_conf = conf_run['ConfModel']
    mcs_n = conf_run['Montecarlo']['N']
    mcs_fa = gammadist(f_lddata['Fa_avg'], f_lddata['Fa_std'], mcs_n)
    mcs_fs = gammadist(f_lddata['Fs_avg'], f_lddata['Fs_std'], mcs_n)
    mcs_fz = normaldist(f_lddata['Fz_avg'], f_lddata['Fz_std'], mcs_n)
    mcs_kch4 = kch4_model(t_lddata, model_conf['k600_model'], p_lddata, True, mcs_fa)
    partial_mcs = functools.partial(mo.opt_test, model_conf, lddata)
    task = [*zip(mcs_kch4, mcs_fs, mcs_fz)]
    res = pool.map(partial_mcs, task)
    opt = [aux[3][0] for aux in res]

    return opt
