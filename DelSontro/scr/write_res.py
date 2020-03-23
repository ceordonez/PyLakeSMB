#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pdb
import numpy as np
import logging
import pandas as pd
from openpyxl import load_workbook
import os

def transform_input(clake):
    lakes = []
    dates = []
    Area = []
    hmls = []
    L = []
    LType = []
    for lake in clake:
        for date in clake[lake]:
            Area.append(clake[lake][date][0])
            hmls.append(clake[lake][date][1])
            L.append(clake[lake][date][2])
            LType.append(clake[lake][date][5])
            lakes.append(lake)
            dates.append(date)
    data = {'Area':Area, 'Hmls':hmls, 'L':L,
            'Lake Type':LType}
    pindex = [np.array(lakes), np.array(dates)]
    inputs = pd.DataFrame(data, index = pindex)
    return inputs

def write_res(path_out, param_data, clake, ExpName, saveres):
    if saveres:
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        inputs = transform_input(clake)
        param_data = param_data.drop(['pol0'], axis=1)
        inputs = inputs.sort_index()
        param_data = param_data.sort_index()
        allres = pd.concat([param_data, inputs], axis=1, sort=False)

        filename = os.path.join(path_out,'Results', 'Transect',
                                'Results_DelSontro_' + ExpName + '.xlsx')
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        allres.to_excel(writer, sheet_name='Results')
        workbook = writer.book
        worksheet = writer.sheets['Results']
        numformat = workbook.add_format({'num_format':'0.00'})
        formatb = workbook.add_format()
        numformat.set_align('center')
        numformat.set_align('vcenter')
        formatb.set_align('center')
        formatb.set_align('vcenter')
        worksheet.set_column('C:M', 10, numformat)
        worksheet.set_column('A:B', 15, formatb)
        worksheet.set_column('N:N', 15, formatb)
        writer.save()
        logging.info('Data saved in: %s', path_out)
    else:
        logging.warning('Result were not saved')


