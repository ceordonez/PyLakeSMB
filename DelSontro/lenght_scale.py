#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import os
import pdb


path_map = '/home/cesar/Dropbox/Cesar/PhD/Data/Fieldwork/MultiLakeSurvey/Lakes'
lakes = ('Bretaye', 'Hallwil', 'Baldegg', 'Chavonnes','Noir',
         'Lioson', 'Soppen')


for lake in lakes:
    fileborder = os.path.join(path_map, lake, 'Map', 'Border_' + lake +'.xlsx')
    data = pd.read_excel(fileborder)
    print('Reading lake:', lake)
    xcoord = data.xcoord
    ycoord = data.ycoord
    covxy = np.cov(xcoord,ycoord)
    s2x = covxy[0,0]
    s2y = covxy[1,1]
    sxy = covxy[0,1]
    A1 = (s2x + s2y)/2
    A2 = A1**2 - s2x*s2y + sxy**2
    s2ma = A1 + np.sqrt(A2)
    s2mi = A1 - np.sqrt(A2)
    sma = np.sqrt(s2ma)
    smi = np.sqrt(s2mi)
    L = np.sqrt(2*sma*smi)
    print(L, sma, smi, sma/smi)

