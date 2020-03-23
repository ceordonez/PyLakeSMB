#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
import pdb

from scr.read_results import read_excel
from scr.logging_conf import logging_conf
from scr.model_delsontr import pross_data
from scr.plot_ds import plot_results
from scr.write_res import write_res
from config_delsontro import *
from config_lake import *

def main():
    logging_conf()
    logging.info('STEP 1: Reading data')
    data = read_excel(path, lakes)
    logging.info('STEP 2: Processing data')
    cx_data, param_data = pross_data(data, clake, Kh_model, Bio_model)
    logging.info('STEP 3: Making figures')
    plot_results(path_fig, data, cx_data, param_data, clake, savefig, filtfig,
                 ExpName)
    logging.info('STEP 4: Writing results')
    write_res(path_res, param_data, clake, ExpName, saveres)
if __name__ == '__main__':
    main()
