#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
import pdb

import scr.read_results as rd
from scr.logging_conf import logging_conf
from scr.model_delsontr import pross_data
from scr.plot_ds import plot_transect
from config_delsontro import *

def main():
    logging_conf()
    logging.info('STEP 1: Reading data')
    data = rd.read_excel(path, lakes)
    logging.info('STEP 2: Processing data')
    cx_data, param_data = pross_data(data)
    logging.info('STEP 3: Making figures')
    plot_transect(data, cx_data, param_data)

if __name__ == '__main__':
    main()
