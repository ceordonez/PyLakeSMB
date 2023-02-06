
import sys
import os
import logging
import yaml

def read_config():

    with open('config_model.yml', 'r') as file:
        conf_model = yaml.safe_load(file)
    check_config(conf_model)

    return conf_model

def check_config(conf_run):

    TFILE = 'Data_transect.csv'
    PFILE = 'Data_parameters.csv'
    FFILE = 'Data_inputs.csv'
    DFILE = 'Data_bubbledissolution.csv'
    ALLFILES = (TFILE, PFILE, FFILE, DFILE)
    KHMODELS = ('P', 'L')
    K600MODELS = ('VP', 'CC', 'MA-NB', 'MA-PB', 'MA-MB', 'kAVG', '05kAVG', '15kAVG')
    MODELOPTIONS = ('FSED', 'PNET', 'KH', 'KCH4')

    check_files(conf_run, ALLFILES)

    model_conf = conf_run['ConfModel']

    if not isinstance(model_conf['t_end'], (int, float)):
        logging.error('t_end variable has to be a float or int')
        sys.exit()
    if not isinstance(model_conf['dt'], (int, float)):
        logging.error('dt variable has to be a float or int')
        sys.exit()
    if not isinstance(model_conf['dr'], (int, float)):
        logging.error('dr variable has to be a float or int')
        sys.exit()
    if model_conf['dt'] >= model_conf['t_end']:
        logging.error('dt needs to be lower than t_end')
        sys.exit()

    if model_conf['Kh_model'] not in KHMODELS:
        logging.error('%s not valid as horizontal dispersion model, please choose between: %s',
                conf_run['ConfModel']['Kh_model'], KHMODELS)
        sys.exit()

    if model_conf['k600_model'] not in K600MODELS:
        logging.error('%s not in k600 parameterizations options, please choose between: %s',
                conf_run['ConfModel']['k600_model'], K600MODELS)
        sys.exit()

    if model_conf['mode_model']['var'] not in MODELOPTIONS:
        logging.error('Mode_model not well defined plese select the following alternatives: %s'
                , MODELOPTIONS)
        sys.exit()

    if model_conf['mode_model']['mode'] not in ('OPT', 'EVAL'):
        logging.error('The options for mode are: (OMP, EVAL)')
        sys.exit()

    if conf_run['Montecarlo']['perform']:

        if model_conf['mode_model']['mode'] != 'OPT':
            logging.error('Montecarlo simulations only run with OPT as a mode option')
            sys.exit()

        if not isinstance(conf_run['Montecarlo']['N'], int):
            logging.error('N variable needs to be a int')
            sys.exit()


def check_files(conf_run, allfiles):

    err= False
    if not set(conf_run['Lakes'].keys()).issubset(os.listdir(conf_run['path'])):
        for lake in conf_run['Lakes']:
            if lake not in os.listdir(conf_run['path']):
                logging.error('No data for lake: %s', lake)
                sys.exit()

    for lake in conf_run['Lakes']:
        folder = os.path.join(conf_run['path'], lake)
        for filename in allfiles:
            if filename in os.listdir(folder):
                logging.info('File %s found for lake: %s', filename, lake)
            else:
                logging.error('File %s for lake %s was not found in: %s', filename, lake, folder)
                err = True
    if err:
        sys.exit('PLEASE SEE ERROR ABOVE')
