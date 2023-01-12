#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from datetime import datetime

def write_results(modelparam, modeldata, conf_run):

    path_res = conf_run['path_res']
    conf_model = conf_run['ConfModel']
    modelmode = '_'.join([conf_model['mode_model']['mode'], conf_model['mode_model']['var']])
    modelparameters = '_'.join([conf_model['Kh_model'], conf_model['k600_model']])
    modelname = '_'.join([modelmode, modelparameters]).upper()
    now = datetime.now().strftime('%Y%m%d-%H')

    if conf_run['Montecarlo']['perform']:
        filename = '_'.join(['Results', 'MonteCarlo', modelname, now])
        save_results(modeldata, path_res, modelname, filename)
    else:
        t_filename = '_'.join(['Results', 'Transect', modelname, now])
        p_filename = '_'.join(['Results', modelname, now])
        save_results(modeldata, path_res, modelname, t_filename)
        save_results(modelparam, path_res, modelname, p_filename)

def save_results(modeldata, path_res, modelname, filename):
    for lake in modeldata.Lake.unique():
        pathmodel = os.path.join(path_res, lake, modelname)
        fileres = os.path.join(pathmodel,  filename + '.csv')
        if not os.path.exists(pathmodel):
            os.makedirs(pathmodel)
        logging.info('Saving %s results in: %s', modelname, pathmodel)
        datalake = modeldata.loc[modeldata.Lake == lake]
        datalake.to_csv(fileres, float_format='%.3f', index=False)
