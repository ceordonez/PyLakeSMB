###############################################################
#
# Author: Cesar Ordonez
# Date: 18 Feb 2020
# Config file to process transect with DelSontro 2017
#
###############################################################

path = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/Lakes'
path_fig = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/'
path_res = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/'

filenameMC = 'Montecarlo_results.xlsx'
filenameOPT = 'Opt_Results_SedCorr'
savefig = True
saveres = True
filtfig = True
Bio_model = True
Kh_model = 'P' #('P' = Peeters 2015, 'L'= Lawrence 1995)
models = ('CO',)

t_end = 30 # days
dt = 0.005 # days
figtag = 'SedCorr'
#ExpName = ('Kh', 'k', 'Fsed', 'OMP')
#ExpName = ('OMP-Opt', 'k-Opt', 'Fsed-Opt', 'Fsed-Opt-ds')
#ExpName = ('k-Opt',)
ExpName = ('OMP-S',)
#ExpName = ('CO-Peeters',)
#ExpName = ('Fsed-Opt', 'Fsed-Opt-ds')
#ExpName_ds = ('Kh-Peeters')
lakes = {'Soppen': ('20180516', '20180912', '20190812'),
         'Lioson': ('20180624', '20180829', '20190717'),}
#         'Noir': ('20180620', '20180904', '20190724')
#         }

"""
lakes = {'Baldegg': ('20180526', '20180915', '20190817'),
         'Hallwil': ('20180523', '20180917'),
         'Soppen': ('20180516', '20180912', '20190812'),}
lakes = {'Baldegg': ('20180526', '20180915', '20190817'),
         'Hallwil': ('20180523', '20180917'),
         'Soppen': ('20180516', '20180912', '20190812'),
         'Lioson': ('20180624', '20180829', '20190717'),
         'Bretaye': ('20180616', '20180902', '20190720'),
         'Chavonnes': ('20180618','20180905', '20190723'),
         'Noir': ('20180620', '20180904', '20190724')
         }
"""
