#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import pandas as pd

def read_data(conf_run):
    """Reads inputs data

    Parameters
    ----------
    conf_run : dictionary containing the configuration information in config_model.ylm

    Returns
    -------
    tdata: dataframe with transect data
    pdata: dataframe with parameters data
    fdata: dataframe with fluxes data
    ddata: dataframe with bubble dissulution data

    """

    TFILE = 'Data_transect.csv'
    PFILE = 'Data_parameters.csv'
    FFILE = 'Data_inputs.csv'
    DFILE = 'Data_bubbledissolution.csv'
    allfiles = (TFILE, PFILE, FFILE, DFILE)

    logging.info('STEP 1.1: Checking datafiles')
    logging.info('STEP 1.2: Reading input files')
    tdata = read_inputs(conf_run, allfiles[0])
    pdata = read_inputs(conf_run, allfiles[1])
    fdata = read_inputs(conf_run, allfiles[2])
    ddata = read_inputs(conf_run, allfiles[3])
    return (ddata, fdata, pdata, tdata)

def read_inputs(conf_run, filename):
    """Reads file define in filename inside conf_run['path']/lake

    Parameters
    ----------
    conf_run : dictionary containing the configuration information in config_model.ylm
    filename : string containing the file name to be read it

    Returns
    -------
    data: dataframe with data in filename

    """
    data = []
    for lake in conf_run['lakes']:
        logging.info('Reading %s file of lake: %s', filename, lake)
        folder = os.path.join(conf_run['path'], lake)
        rfile = os.path.join(folder, filename)
        datalake = pd.read_csv(rfile, sep=',')
        datalake['Date'] = pd.to_datetime(datalake.Date, format='%Y-%m-%d')
        datalake.insert(0, 'Lake', lake)
        check_dates(conf_run, lake, datalake, filename)
        datalake = select_dates(conf_run, lake, datalake)
        data.append(datalake)
    data = pd.concat(data, ignore_index=True)
    return data

def check_dates(conf_run, lake, data, filename):
    err = False
    for date in conf_run['lakes'][lake]:
        date = pd.to_datetime(date, format='%Y%m%d')
        if date not in data.Date.unique():
            logging.error('Date %s not in file %s for lake: %s', date, filename, lake)
            err = True
    if err:
        sys.exit('PLEASE SEE ERROR ABOVE')

def select_dates(conf_run, lake, data):
    seldata = []
    for date in conf_run['lakes'][lake]:
        datadate = data[data.Date == date]
        seldata.append(datadate)
    seldata = pd.concat(seldata, ignore_index=True)
    return seldata
