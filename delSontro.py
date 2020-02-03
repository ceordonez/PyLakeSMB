#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb

from scipy.special import iv # Modified Bessel function first kind

# Lake Archigan

Zml = 4     # (m) Surface mixed layer depth
A = 5.3     # (km2) Lake area
r = 1300    # (m) Lake radio
U10 = 1.47  # (m/s) Wind velocity at 10m
L = 1443    # (m) Length scale
Cc = 0.103  # (umol/l) Concentration center
Cr = 1      # (umol/l) Concentration border
kop = 0.1   #(1/d)


x = np.arange(0,r,10)  #(m)
Kh1 = 1.4*10**(-4)*L**(1.07)*86400 # (m2/d) (Peeters and Hofmann (2015)
Kh2 = 3.2*10**(-4)*L**(1.10)*86400 # (m2/d) (Lawrence et al 1995)

k600 = 2.51 + 1.48*U10 + 0.39*U10*np.log10(A) # (cm/h) Vachon and Praire (2013)
k600 = k600*24/100. #(m/d)

lda1 = np.sqrt((k600/Zml+kop)/Kh1)
lda2 = np.sqrt((k600/Zml+0*kop)/Kh2)
lda3 = np.sqrt((k600/Zml-kop)/Kh2)
lda4 = np.sqrt((k600/Zml+kop)/Kh2)

print('k600', k600)
print('lda', lda1)
print('lda', lda2)
print('Kh1', Kh1)
print('Kh2', Kh2)

Cx1 = Cc*iv(0,lda1*x)
Cx2 = Cc*iv(0,lda2*x)
Cx3 = Cc*iv(0,lda3*x)
Cx4 = Cc*iv(0,lda4*x)

plt.figure()
#plt.plot(r-x,Cx1/Cx1[-1], label = 'Kh1')
plt.plot(r-x,Cx2/Cx2[-1], label = 'kop=0')
plt.plot(r-x,Cx3/Cx3[-1], label = 'kop=-0.1')
plt.plot(r-x,Cx4/Cx4[-1], label = 'kop=0.1')
plt.legend()
#plt.plot(x,Cxe)

C0n = 0.5
C0f = 0.0
plt.figure()
Cxe = C0n*np.exp(-lda2*x) + C0f*np.exp(-lda2*(r-x))
plt.plot(x, Cxe/Cxe[0])
plt.show()

