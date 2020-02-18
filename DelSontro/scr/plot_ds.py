#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl

import logging
import os
import pdb

import numpy as np

mpl.style.use('presentation')

def plot_results(path_out, data, cx_data, param_data, clake, savefig, ExpName):
    for lake in data:
        for date in data[lake]:
            logging.info('Making figure: %s, %s', lake, date)
            date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
            title = 'Lake %s %s' % (lake, date_str)

            # Main Results Parameters
            ds = param_data.loc[(lake, date)].ds

            # Lake date data
            ld_data = data[lake][date]

            # If there is data to filter
            filt = clake[lake][date][4]
            if filt:
                findex = ld_data.index[filt]
                fdata = ld_data.drop(findex)
            else:
                findex = False
                fdata = ld_data

            fig = plt.figure(figsize=(8,6))#, tight_layout=True)
            gs = gridspec.GridSpec(2, 2)
            ax1 = fig.add_subplot(gs[0, :])
            fig.suptitle(title)
            plot_transect(ax1, lake, date, fdata, cx_data, ld_data, param_data,
                          filt, findex)
            ax2 = fig.add_subplot(gs[1, 0])
            ax3 = fig.add_subplot(gs[1, 1])
            plot_fractionation(ax2, lake, date, fdata, param_data, ld_data,
                               ds, filt, findex)
            plot_keeling(ax3, lake, date, fdata, param_data, ld_data, ds, filt,
                         findex)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            if savefig:
                pathfig = os.path.join(path_out, lake, 'Results', 'Transect')
                if not os.path.exists(pathfig):
                    os.makedirs(pathfig)
                figname = 'DelSontro_' + lake + '_' + date + '_' + ExpName + '.png'
                filename = os.path.join(pathfig, figname)
                plt.savefig(filename, format='png', dpi=300)
                logging.info('Saved in: %s', pathfig)
            else:
                plt.show()

def plot_transect(ax, lake, date, fdata, cx_data, ld_data, param_data,
                  filt, findex=False):

    kop = param_data.loc[(lake, date)].kop
    Kh = param_data.loc[(lake, date)].Kh*86400/100/100.
    lda = param_data.loc[(lake, date)].lda

    title = u'\u03BB = %.2f (1/m), k$_{op}$ = %.2f (1/d), K$_h$ = %.2f (cm$^2$/s)' % (lda, kop, Kh)
    ax.set_title(title)
    fdata['CH4'].plot(ax=ax, style='ro', legend=False, markerfacecolor='w')#,
                      #color='red')
    cx_data[lake][date].plot(ax=ax, y='CH4', label='Model', legend=False)
    fdata['dCH4'].plot(ax=ax, secondary_y=True, marker='o', color= 'k',
                       linestyle='None', markerfacecolor='w')

    ax.right_ax.set_ylabel(u'\u03B4CH$_4$ (\u2030)')
    ax.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
    ax.set_xlabel('Distance from shore (m)')
    labels = ['CH$_4$', 'Model', u'\u03B4CH$_4$']
    if filt:
        ld_data.loc[findex].plot(ax=ax, y='CH4', marker='*',
                                 linestyle='None', color='grey',
                                 legend=False)
        labels = ['CH$_4$', 'Model', 'Filtered', u'\u03B4CH$_4$']

    handles = []
    for ax in [ax, ax.right_ax]:
        for h,l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
    ax.legend(handles,labels,ncol=2)

def plot_fractionation(ax, lake, date, fdata, param_data, ld_data, ds,
                       filt, findex=False, a=1.02):

    # Fractionation
    b1 = param_data.loc[(lake, date)].b1
    b0 = param_data.loc[(lake, date)].b0
    title = u'\u03B2$_0$=%.2f, \u03B2$_1$=%.2E' % (b0, b1)
    ax.set_title(title)
    fyf = np.log(((a - 1)*1000) - (fdata.dCH4 - ds))
    flnC = np.log(fdata.CH4)
    f = np.polyval([b1, b0], flnC)
    yf = np.log(((a - 1)*1000) - (ld_data.dCH4 - ds))
    lnC = np.log(ld_data.CH4)

    ax.plot(flnC, fyf, 'ko',markerfacecolor='w')
    ax.plot(flnC, f)
    ax.set_xlabel('ln(CH$_4$)')
    ax.set_ylabel(u'ln((\u03B1-1)*1000 - (CH$_4$ - \u03B4s))')
    if filt:
        ax.plot(lnC.loc[findex], yf.loc[findex],'*', color='grey')


def plot_keeling(ax, lake, date, fdata, param_data, ld_data, ds, filt, findex = False):

    title = u'\u03B4s=%.2f (\u2030)' % ds
    ax.set_title(title)
    pol0 = param_data.loc[(lake, date)].pol0
    fk = np.polyval([pol0, ds], 1/fdata.CH4)
    ax.plot(1/fdata.CH4, fdata.dCH4, 'ko', markerfacecolor='w')
    ax.plot(1/fdata.CH4, fk)
    ax.set_xlabel(u'1/CH$_4$ (l/\u03BCmol)')
    ax.set_ylabel(u'\u03B4CH$_4$ (\u2030)')
    if filt:
        ax.plot(1/ld_data.loc[findex].CH4, ld_data.loc[findex].dCH4,
                '*', color = 'grey')
