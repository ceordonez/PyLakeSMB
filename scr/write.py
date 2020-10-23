#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

import pandas as pd

from openpyxl import load_workbook
from datetime import datetime

def write_results(modelparam, path_res):
    for model in modelparam:
        pathmodel = os.path.join(path_res, 'Results', 'Modelling', model)
        if not os.path.exists(pathmodel):
            os.makedirs(pathmodel)
        logging.info('Saving %s results in: %s', model, pathmodel)
        now = datetime.now().strftime('%Y%m%d-%H')
        filename = '_'.join(['Results', model, now])
        fileres = os.path.join(pathmodel,  filename + '.xlsx')
        data = modelparam[model]
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
