#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import numpy as np
import logging

import pdb

def read_excel(epath, lakes):
    alldata = dict()
    for lake in lakes:
        ladate = dict()
        for date in lakes[lake]:
            logging.info('Reading lake: %s on %s', lake, date)
            filename = 'CH4-CO2-dC_Calculations_' + lake + '_' + date + '.xlsx'
            filepath = os.path.join(epath, lake, 'Results', 'CH4-CO2-dC', filename)
            data = pd.read_excel(filepath, sheet_name='Transect', skiprows=2,
                                 usecols=[0, 3, 4, 5, 6, 9, 11, 12, 21], skipfooter=5,
                                 names = ['Sample', 'Depth', 'Distance', 'CH4', 'dCH4', 'Temp',
                                          'CH4_atm', 'U10', 'Fa_fc'])
            data = data.set_index('Distance')
            data = data.dropna()
            data.loc[(data.Fa_fc == 9999), 'Fa_fc'] = np.nan
            ladate.update({date: data})
        alldata.update({lake: ladate})
    return alldata

def read_mcmb(epath, namefile):
    filename = os.path.join(epath, 'Results', 'Montecarlo_MB', namefile)
    data = pd.read_excel(filename)
    data = data.set_index(['Lake', 'dates'])
    return data
