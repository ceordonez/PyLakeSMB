#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pdb
import logging
import pandas as pd
from openpyxl import load_workbook
import os

def write_res(path_out, param_data, clake, ExpName, saveres):
    if saveres:
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        param_data = param_data.drop(['pol0'], axis=1)
        filename = os.path.join(path_out, 'Results_DelSontro_' + ExpName + '.xlsx')
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        param_data.to_excel(writer, sheet_name='Results')
        workbook = writer.book
        worksheet = writer.sheets['Results']
        numformat = workbook.add_format({'num_format':'0.00'})
        formatb = workbook.add_format()
        numformat.set_align('center')
        numformat.set_align('vcenter')
        formatb.set_align('center')
        formatb.set_align('vcenter')
        worksheet.set_column('C:I', 10, numformat)
        worksheet.set_column('A:B', 15, formatb)
        writer.save()
        logging.info('Data saved in: %s', path_out)
    else:
        logging.warning('Result were not saved')

