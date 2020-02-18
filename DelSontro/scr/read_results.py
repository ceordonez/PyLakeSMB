#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
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
                                 usecols=[0, 3, 4, 5, 6, 12], skipfooter=5,
                                 names = ['Sample', 'Depth', 'Distance', 'CH4', 'dCH4',
                                          'U10'])
            data = data.set_index('Distance')
            data = data.dropna()
            ladate.update({date: data})
        alldata.update({lake: ladate})
    return alldata
