# =======================================================================
# Author: Cesar Ordonez
# Date: 21 April 2020
# Config file to process transect with different models
# =======================================================================

# =======================================================================
# Inputs path and filenames
# =======================================================================
path = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/Lakes'
path_res = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/'
filenameMC = 'Montecarlo_results.xlsx'

# =======================================================================
# Figure options
# =======================================================================
path_fig = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/'
sct = ()#['U10','kch4_fc'],) # Scatter plot
fshore = True # Plot from shore vs concentrations

# =======================================================================
# Model configuration
# =======================================================================
models = ('Peeters-OPT-OMP',)# 'Peeters')
#models = ('Peeters-SENS-KH','Peeters-SENS-KCH4','Peeters-SENS-FSED','Peeters-SENS-OMP',)#'Peeters-OMP')#-OPT-FSED',)#,'CO-CORR-OPT-OMP')
Kh_model = 'P' #('P' = Peeters 2015, 'L'= Lawrence 1995)
k600_model = '15kAVG' # ('VP = Vachon & Prairie, 'CC': Cole & Caraco)
t_end = 30 # days
dt = 0.005 # days

"""
lakes = {'Soppen': ('20180516', '20180912', '20190812'),}
#         'Lioson': ('20180624', '20180829', '20190717'),}
#         'Noir': ('20180620', '20180904', '20190724')
#         }
"""
lakes = {'Baldegg': ('20180526', '20180915', '20190817'),
         'Soppen': ('20180516', '20180912', '20190812'),
         'Lioson': ('20180624', '20180829', '20190717'),
         'Bretaye': ('20180616', '20180902', '20190720'),
         'Chavonnes': ('20180618', '20180905', '20190723'),
         'Hallwil': ('20180523', '20180917'),
         'Noir': ('20180620', '20180904', '20190724')
         }
