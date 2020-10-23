#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pdb

#from DelSontro.scr.model_delsontr import pross_data
#from Peeters.scr.model import pross_transport

from scr.read_results import read_excel, read_mcmb
from scr.pross_data import process_data
from scr.logging_conf import logging_conf
from scr.plot_data import plot_figures
from scr.write import write_results

from config_models import *
from config_lake import clake

def main():
    logging_conf()
    logging.info('STEP 1: READING DATA')
    logging.info('STEP 1.1: Reading transect data')
    t_data = read_excel(path, lakes)
    logging.info('STEP 1.2: Reading montecarlo data')
    mc_data = read_mcmb(path_res, filenameMC)
    logging.info('STEP 2: PROCESSING DATA')
    modeldata, modelparam = process_data(t_data, clake, Kh_model, k600_model, mc_data, dt,
            t_end, models)
    logging.info('STEP 3: WRITING RESULTS')
    write_results(modelparam, path_res)
    logging.info('STEP 4: PLOTTING DATA')
    plot_figures(t_data, mc_data, modeldata, modelparam, path_fig, sct, fshore)

if __name__ == '__main__':
    main()
