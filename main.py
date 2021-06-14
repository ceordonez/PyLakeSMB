#/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import multiprocessing as mp

from scr.read_results import read_excel, read_mcmb, read_dis
from scr.pross_data import process_data
from scr.logging_conf import logging_conf
from scr.plot_data import plot_figures
from scr.write import write_results
from scr.read_config import read_config


def main(pool):
    logging_conf()
    logging.info('STEP 0: READING CONFIGURATION FILES')
    conf_run, lakeparam = read_config()
    logging.info('STEP 1: READING DATA')
    logging.info('STEP 1.1: Reading transect data')
    t_data = read_excel(conf_run['path'], conf_run['lakes'])
    logging.info('STEP 1.2: Reading montecarlo data')
    mc_data = read_mcmb(conf_run['path_res'], conf_run['filenameMC'])
    logging.info('STEP 1.3: Reading dissolution data')
    dis_data = read_dis(conf_run['path_res'], conf_run['lakes'])
    logging.info('STEP 2: PROCESSING DATA')
    modeldata, modelparam = process_data(t_data, dis_data, mc_data, conf_run,
                                         lakeparam, pool)
    logging.info('STEP 3: WRITING RESULTS')
    write_results(modelparam, modeldata, conf_run)
    logging.info('STEP 4: PLOTTING DATA')
    plot_figures(t_data, mc_data, modeldata, modelparam, conf_run)


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    main(pool)
