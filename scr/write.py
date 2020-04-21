#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import logging
from openpyxl import load_workbook
import os

def write_results(opt_data, path_res, filenameOPT, ExpNames):
    if len(opt_data):
        expname = '_'.join(ExpNames)
        respath = os.path.join(path_res, 'Results', 'Modelling')
        logging.info('Saving optimization results in: %s', respath)
        if not os.path.exists(respath):
            os.makedirs(respath)
        fileres = os.path.join(respath, filenameOPT + '_'+ expname + '.xlsx')
        opt_data = opt_data.sort_index()
        writer = pd.ExcelWriter(fileres, engine='xlsxwriter')
        opt_data.to_excel(writer, sheet_name='Results')
        wb = writer.book
        ws = writer.sheets['Results']
        numformat = wb.add_format({'num_format':'0.00'})
        numformat.set_align('center')
        numformat.set_align('vcenter')
        formatb = wb.add_format()
        ws.set_column('B:L', 15, numformat)
        ws.set_column('A:B', 15, formatb)
        writer.save()
    else:
        logging.warning('No optimization results to save')
