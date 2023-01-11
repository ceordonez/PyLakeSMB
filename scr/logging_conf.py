#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

def logging_conf():
    # Logging configuration
    logging.basicConfig(format='%(asctime)s %(levelname)s:> %(message)s',
                        datefmt='%d/%m/%y %H:%M', level=logging.INFO,
                        filename='PyLakeSMB.log', filemode='w')
    rootLogger = logging.getLogger()
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:> %(message)s', '%d/%m/%y %H:%M'))
    rootLogger.addHandler(consoleHandler)
