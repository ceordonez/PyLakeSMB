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
    check_files(conf_run, allfiles)
    logging.info('STEP 1.2: Reading input files')
    tdata = read_inputs(conf_run, allfiles[0])
    pdata = read_inputs(conf_run, allfiles[1])
    fdata = read_inputs(conf_run, allfiles[2])
    ddata = read_inputs(conf_run, allfiles[3])
    return tdata, pdata, fdata, ddata


def check_files(conf_run, allfiles):
    err= False
    for lake in conf_run['lakes']:
        folder = os.path.join(conf_run['path'], lake)
        for filename in allfiles:
            if filename in os.listdir(folder):
                logging.info('File %s found for lake: %s', filename, lake)
            else:
                logging.error('File %s for lake %s was not found in: %s', filename, lake, folder)
                err = True
    if err:
        sys.exit('PLEASE SEE ERROR ABOVE')


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
    for i, lake in enumerate(conf_run['lakes']):
        logging.info('Reading %s file of lake: %s', filename, lake)
        folder = os.path.join(conf_run['path'], lake)
        rfile = os.path.join(folder, filename)
        datalake = pd.read_csv(rfile, sep=',')
        datalake['Date'] = pd.to_datetime(datalake.Date, format='%Y-%m-%d')
        datalake.insert(0, 'Lake', lake)
        check_dates(conf_run, lake, datalake, filename)
        datalake = select_dates(conf_run, lake, datalake)
        if i == 0:
            data = datalake
        else:
            data = pd.concat([data, datalake], ignore_index=True)
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
    for i, date in enumerate(conf_run['lakes'][lake]):
        datadate = data[data.Date == date]
        if i == 0:
            seldata = datadate
        else:
            seldata = pd.concat([seldata, datadate], ignore_index=True)
    return seldata
