#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl

import logging
import os
import pdb

import numpy as np

mpl.style.use('ggplot')

def plot_results(path_out, data, cx_data, param_data, clake, savefig, filtfig, ExpName):
    for lake in data:
        for date in data[lake]:
            logging.info('Making figure: %s, %s', lake, date)
            date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
            title = 'Lake %s %s' % (lake, date_str)

            # Main Results Parameters
            ds = param_data.loc[(lake, date)].ds

            # Lake date data
            ld_data = data[lake][date]
            mind = data[lake][date].index.min()
            C0 = data[lake][date]['CH4'][mind].mean()
            ld_data['CH4c'] = data[lake][date]['CH4']/C0
            cx_data[lake][date]['CH4c_op'] = cx_data[lake][date]['CH4_op']/C0
            cx_data[lake][date]['CH4c'] = cx_data[lake][date]['CH4']/C0

            # If there is data to filter
            filt = clake[lake][date][4]
            if filt:
                fdata = ld_data.reset_index()
                ld_data = ld_data.reset_index()
                ld_data = ld_data.drop(filt)
                ld_data = ld_data.set_index('Distance')
                fdata = fdata.iloc[filt]
                fdata = fdata.set_index('Distance')
            else:
                fdata = ld_data

            fig = plt.figure(figsize=(8,6))
            gs = gridspec.GridSpec(2, 2)
            fig.suptitle(title)
            plot_transect(fig, gs, lake, date, fdata, cx_data, ld_data, param_data,
                          filt, filtfig)
            ax2 = fig.add_subplot(gs[1, 0])
            ax3 = fig.add_subplot(gs[1, 1])
            plot_fractionation(ax2, lake, date, fdata, param_data, ld_data,
                               ds, filt, filtfig)
            plot_keeling(ax3, lake, date, fdata, param_data, ld_data, ds, filt,
                         filtfig)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            if savefig:
                pathfig = os.path.join(path_out,'Lakes', lake, 'Results', 'Transect')
                if not os.path.exists(pathfig):
                    os.makedirs(pathfig)
                if filtfig:
                    figname = 'DelSontro_' + lake + '_' + date + '_' + ExpName + 'Filt.png'
                else:
                    figname = 'DelSontro_' + lake + '_' + date + '_' + ExpName + '.png'
                filename = os.path.join(pathfig, figname)
                plt.savefig(filename, format='png', dpi=300)
                pathfig = os.path.join(path_out, 'Results','Transect','Figures')
                filename = os.path.join(pathfig, figname)
                if not os.path.exists(pathfig):
                    os.makedirs(pathfig)
                plt.savefig(filename, format='png', dpi=300)
                logging.info('Saved in: %s', pathfig)
            else:
                plt.show()

def plot_transect(fig, gs, lake, date, fdata, cx_data, ld_data, param_data,
                  filt, filtfig):

    kop = param_data.loc[(lake, date)].kop
    Kh = param_data.loc[(lake, date)].Kh
    lda = param_data.loc[(lake, date)].lda

    title = u'\u03BB = %.2f (1/m), k$_{op}$ = %.2f (1/d), K$_h$ = %.2f (m$^2$/d)' % (lda, kop, Kh)
    gs00 = gridspec.GridSpecFromSubplotSpec(1,4, subplot_spec=gs[0,:])
    ax = fig.add_subplot(gs00[0,:3])
    ax.set_title(title)
    ax1 = fig.add_subplot(gs00[0,3])
    ax1.axis('off')
    ld_data['CH4c'].plot(ax=ax, style='ko', legend=False, mfc='w')
    cx_data[lake][date].plot(ax=ax, y='CH4c_op', label='Model', legend=False,
                             color='k')
    cx_data[lake][date].plot(ax=ax, y='CH4c', label='Model', legend=False,
                             color='b')
    ld_data['dCH4'].plot(ax=ax, secondary_y=True, marker='o', color= 'r',
                       linestyle='None', mfc='w')
    ax.right_ax.set_ylabel(u'\u03B4$^{13}$CH$_4$ (\u2030)')
    #ax.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
    ax.set_ylabel(u'Relative [CH$_4$]')
    ax.set_xlabel('Distance from shore (m)')
    labels = ['CH$_4$', 'Model_op', 'Model', u'\u03B4$^{13}$CH$_4$']
    if filt and filtfig:
        fdata.plot(ax=ax, y='CH4c', marker='*',
                                 linestyle='None', color='grey',
                                 legend=False)
        fdata['dCH4'].plot(ax=ax, secondary_y=True, marker='*',
                                 linestyle='None', color='red',
                                 legend=False)
        labels = ['CH$_4$', 'Model_op', 'Model', 'Filtered', u'\u03B4$^{13}$CH$_4$']

    handles = []
    for ax in [ax, ax.right_ax]:
        for h,l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
    ax1.legend(handles, labels, ncol=1, loc='center right')

def plot_fractionation(ax, lake, date, fdata, param_data, ld_data, ds,
                       filt, filtfig, a=1.02):

    # Fractionation
    b1 = param_data.loc[(lake, date)].b1
    b0 = param_data.loc[(lake, date)].b0
    title = u'\u03B2$_0$=%.2f, \u03B2$_1$=%.2E' % (b0, b1)
    ax.set_title(title)
    try:
        fyf = np.log(((a - 1)*1000) - (ld_data.dCH4 - ds))
        flnC = np.log(ld_data.CH4)
    except Exception:
        logging.warning('Fractionation: Negative value in data occured')
    try:
        yf = np.log(((a - 1)*1000) - (fdata.dCH4 - ds))
        lnC = np.log(fdata.CH4)
    except:
        yf = fdata.dCH4*np.NAN
        lnC = fdata.dCH4*np.NAN
        logging.warning('Fractionation: Negative value in filtered data occured')

    f = np.polyval([b1, b0], flnC)
    ax.plot(flnC, fyf, 'ko',markerfacecolor='w')
    ax.plot(flnC, f)
    ax.set_xlabel('ln(CH$_4$)')
    ax.set_ylabel(u'ln((\u03B1-1)*1000 - (\u03B4$^{13}$CH$_4$ - \u03B4s))')
    if filt and filtfig:
        ax.plot(lnC, yf,'*', color='grey')


def plot_keeling(ax, lake, date, fdata, param_data, ld_data, ds, filt, filtfig):

    title = u'\u03B4s=%.2f (\u2030)' % ds
    ax.set_title(title)
    pol0 = param_data.loc[(lake, date)].pol0
    fk = np.polyval([pol0, ds], 1/ld_data.CH4)
    ax.plot(1/ld_data.CH4, ld_data.dCH4, 'ko', markerfacecolor='w')
    ax.plot(1/ld_data.CH4, fk)
    ax.set_xlabel(u'1/CH$_4$ (l/\u03BCmol)')
    ax.set_ylabel(u'\u03B4$^{13}$CH$_4$ (\u2030)')
    if filt and filtfig:
        ax.plot(1/fdata.CH4, fdata.dCH4,
                '*', color = 'grey')
