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
        datalake['Lake'] = lake
        if i == 0:
            data = datalake
        else:
            data = pd.concat([data, datalake])
        return data


# def read_transect(conf_run):
#     """Reads Data_transect.csv file
# 
#     Parameters
#     ----------
#     conf_run : configuration information in config_model.ylm
# 
#     Returns
#     -------
#     p_data: dataframe with data on Data_transect.csv file
# 
#     """
#     for lake in conf_run['lakes']:
#         logging.info('Reading flux inputs of lake: %s', lake)
#         filename = 'Data_transect.csv'
#         folder = os.path.join(conf_run['path'], lake)
#         rfile = os.path.join(folder, filename)
#         if filename in os.listdir(folder):
#             data = pd.read_csv(rfile)
#             data = data.set_index('Distance')
#             #data = data.dropna()
#             #data.loc[(data.Fa_fc == 9999), 'Fa_fc'] = np.nan
#             #ladate.update({date: data})
#             return data
#         else:
#             logging.error('File %s for lake %s was not found in: %s', filename, lake, folder)
#             sys.exit()
# 
# 
# def read_mcmb(epath, namefile):
#     filename = os.path.join(epath, 'Results', 'Montecarlo_MB', namefile)
#     data = pd.read_excel(filename, engine='openpyxl')
#     data = data.set_index(['Lake', 'dates'])
#     return data
# 
# def read_dis(epath, lakedate):
#     dis_data = dict()
#     dpath = os.path.join(epath, 'Results', 'Bubbles', 'Results')
#     lakes = os.listdir(dpath)
#     for lake in lakes:
#         if lake in lakedate:
#             dis_data[lake] = dict()
#             for date in lakedate[lake]:
#                 filename = '_'.join(['Dissolution', 'radius', lake, date])
#                 filepath = os.path.join(dpath, lake, filename)
#                 datafile = pd.read_csv(filepath + '.csv')
#                 dis_data[lake][date]=datafile
#     return dis_data
