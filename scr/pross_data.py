#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
import logging

import DelSontro.scr.model_delsontr as ds
import Peeters.scr.model as pe
import scr.model as co

def process_data(t_data, clake, Kh_model, Bio_model, mc_data, dt, t_end, ExpName, models):

    modeldata = dict()
    for mod in models:
        if mod == 'DelSontro':
            logging.info('Processing data DelSontro et. al. 2018 model')
            ds_data, ds_param = ds.pross_data(t_data, clake, Kh_model, Bio_model)

        elif mod == 'Peeters':
            logging.info('Processing physical model Peeters et.al. 2019')
            pdb.set_trace()

        elif mod == 'CO_cor':
            logging.info('Processing physical model Ased corrected')
            ph_data, opt_data = co.pross_transport(t_data, ds_param, mc_data, ds_data,
                    clake, dt, tf, exp_name)

        elif mod == 'CO':
            logging.info('Processing physical model Ased not corrected')
            ph_data, opt_data = co.pross_transport(t_data, ds_param, mc_data, ds_data,
                    clake, dt, tf, exp_name)
