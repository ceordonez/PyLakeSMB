#/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import multiprocessing as mp

from scr.logging_conf import logging_conf
from scr.read_config import read_config
from scr.read_inputs import read_data
from scr.pross_data import process_data
from scr.write import write_results

def main(pool):
    """Run PyLakeSMB
    """

    logging_conf()
    logging.info('STEP 0: READING CONFIGURATION FILES')
    conf_run = read_config()

    logging.info('STEP 1: READING DATA')
    data = read_data(conf_run)

    logging.info('STEP 2: PROCESSING DATA')
    modeldata, modelparam = process_data(conf_run, data, pool)

    logging.info('STEP 3: WRITING RESULTS')
    write_results(modelparam, modeldata, conf_run)

    logging.info('*** Moldel PyLakeSMB run succesfully ***')

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    main(pool)
