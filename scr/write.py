#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

import pandas as pd

from openpyxl import load_workbook
from datetime import datetime

def write_results(modelparam, modeldata, conf_run):
    path_res = conf_run['path_res']
    conf_model = conf_run['ConfModel']
    modelmode = '_'.join([conf_model['mode_model']['mode'], conf_model['mode_model']['var']])
    modelparameters = '_'.join([conf_model['Kh_model'], conf_model['k600_model']])
    modelname = '_'.join([modelmode, modelparameters]).upper()
    if conf_run['MonteCarlo']['perform']:
        results_mcs(modeldata, path_res, modelname)
    else:
        results_transect(modeldata, path_res, modelname)
        results_params(modelparam, path_res, modelname)

def results_mcs(modeldata, path_res, modelname):
    pathmodel = os.path.join(path_res, 'Results', 'Modelling', modelname)
    if not os.path.exists(pathmodel):
        os.makedirs(pathmodel)
    logging.info('Saving %s results in: %s', modelname, pathmodel)
    now = datetime.now().strftime('%Y%m%d-%H')
    filename = '_'.join(['Results', 'MonteCarlo', modelname, now])
    fileres = os.path.join(pathmodel,  filename + '.csv')
    #writer = pd.ExcelWriter(fileres)
    modeldata.to_csv(fileres, index=False, float_format='%.3f')#, sheet_name='MonteCarlo')
    # wb = writer.book
    # ws = writer.sheets['MonteCarlo']
    # numformat = wb.add_format({'num_format':'0.00'})
    # numformat.set_align('center')
    # numformat.set_align('vcenter')
    # formatb = wb.add_format()
    # ws.set_column('A:B', 15, formatb)
    # ws.set_column('C:C', 15, numformat)
    # writer.save()

def results_transect(modeldata, path_res, modelname):
    pathmodel = os.path.join(path_res, 'Results', 'Modelling', modelname)
    if not os.path.exists(pathmodel):
        os.makedirs(pathmodel)
    logging.info('Saving %s results in: %s', modelname, pathmodel)
    now = datetime.now().strftime('%Y%m%d-%H')
    filename = '_'.join(['Results', 'Transect', modelname, now])
    fileres = os.path.join(pathmodel,  filename + '.xlsx')
    writer = pd.ExcelWriter(fileres)
    for lake in modeldata:
        data = []
        for date in modeldata[lake]:
            if not len(data):
                data = modeldata[lake][date]
            else:
                data = pd.concat([data, modeldata[lake][date]], axis=1)
            data = data.rename(columns={"C": date})
        data.to_excel(writer, sheet_name=lake)
        # wb = writer.book
        # ws = writer.sheets[lake]
        # numformat = wb.add_format({'num_format':'0.00'})
        # numformat.set_align('center')
        # numformat.set_align('vcenter')
        # formatb = wb.add_format()
        # ws.set_column('A:D', 15, formatb)
    writer.save()

def results_params(modelparam, path_res, modelname):
    pathmodel = os.path.join(path_res, 'Results', 'Modelling', modelname)
    if not os.path.exists(pathmodel):
        os.makedirs(pathmodel)
    logging.info('Saving %s results in: %s', modelname, pathmodel)
    now = datetime.now().strftime('%Y%m%d-%H')
    filename = '_'.join(['Results', modelname, now])
    fileres = os.path.join(pathmodel,  filename + '.xlsx')
    data = modelparam
    data = data.sort_index()
    #writer = pd.ExcelWriter(fileres, engine='xlsxwriter', index=False)
    writer = pd.ExcelWriter(fileres)
    data.to_excel(writer, sheet_name='Results')
    wb = writer.book
    ws = writer.sheets['Results']
    numformat = wb.add_format({'num_format':'0.00'})
    numformat.set_align('center')
    numformat.set_align('vcenter')
    formatb = wb.add_format()
    ws.set_column('A:B', 15, formatb)
    ws.set_column('B:Q', 15, numformat)
    writer.save()
