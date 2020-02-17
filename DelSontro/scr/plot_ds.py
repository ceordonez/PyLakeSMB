#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def plot_transect(data, cx_data, param_data):
    for lake in data:
        for date in data[lake]:
            xd = data[lake][date].Distance
            cd = data[lake][date].CH4
            dcd = data[lake][date].dCH4
            cx = cx_data[lake][date].CH4
            x = cx_data[lake][date].Distance
            ds = param_data[lake][date].ds
            pol0 = param_data[lake][date].pol0
            b1 = param_data[lake][date].b1
            b0 = param_data[lake][date].b0

            yf = np.log(0.02*1000-(dcd-ds))
            lnC = np.log(cd)
            f = np.polyval([b1, b0], lnC)
            fk = np.polyval([pol0, ds], 1/cd)

            fig = plt.figure(tight_layout=True)
            gs = gridspec.GridSpec(2, 2)
            ax = fig.add_subplot(gs[0, :])
            ax.plot(xd, cd, 'o')
            ax.plot(x, cx)
            ax.set_ylabel('CH4 (umol/l)')
            ax.set_xlabel('Distance from shore (m)')
            ax = fig.add_subplot(gs[1, 0])
            ax.plot(lnC, yf, 'o')
            ax.plot(lnC, f)
            ax.set_xlabel('ln(CH4)')
            ax = fig.add_subplot(gs[1, 1])
            ax.plot(1/cd, dcd, 'o')
            ax.plot(1/cd, fk)
            ax.set_xlabel('1/CH4 (l/umol)')
            ax.set_ylabel('dCH4 (\%)')
            plt.show()
