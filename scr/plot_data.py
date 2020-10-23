#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
import os
import logging

import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

plt.style.use('seaborn')

def plot_figures(t_data, mc_data, modeldata, modelparam, path_fig, sct, fshore):

    if sct:
        logging.info('Plotting scatter plots')
        fig = plot_scatter(t_data, modelparam, sct, path_fig)
    elif fshore:
        # Ploting transect (Distance from shore vs concentration)
        for lake in t_data:
            for date in t_data[lake]:
                # Select data
                t_ladata = t_data[lake][date]
                date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
                logging.info('Plotting transect lake %s date %s', lake, date_str)
                Fsed = mc_data.loc[lake, date_str].SedF_avg
                OMP = mc_data.loc[lake, date_str].OMP_avg
                plot_transect(t_ladata, modeldata, modelparam, OMP, Fsed, lake, date, path_fig)

def plot_transect(data, modeldata, modelparam, OMP, Fsed, lake, date, path_fig):

    plotfig1 = False
    makefig1 = False
    fitplot1 = False
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
    title = 'Lake %s %s' % (lake, date_str)
    if len(modeldata.keys())>1:
        # Figure (fig1) for all models + data
        makefig1 = True
        fig1, ax1 = plt.subplots(1, 1,figsize = (6,3))
        fig1.suptitle(title, fontsize=14)
        nf = 1
        ax1.set_xlabel('Distance from shore (m)')
        ax1.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
        # Shrink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.21,
                        box.width, box.height * 0.8])

    ci = 0
    for model in modeldata:
        k = modelparam[model].loc[lake,date].kch4
        kh = modelparam[model].loc[lake,date].Kh
        if 'DELSONTRO' in model:
            R = 0
        else:
            R = modelparam[model].loc[lake,date].R
        if 'PEETERS' in model:
            if 'OMP' in model or 'SENS' in model:
                OMP = OMP
            else:
                OMP = 0
        if '-OPT' in model:
            if 'FSED' in model:
                Fsed = modelparam[model].loc[lake, date].Fsed_opt
                OMP = 0
            elif 'OMP' in model:
                OMP = modelparam[model].loc[lake, date].OMP_opt
            elif 'KCH4' in model:
                k = modelparam[model].loc[lake, date].kch4_opt
                OMP = 0
            elif 'KH' in model:
                k = modelparam[model].loc[lake, date].kh_opt
                OMP = 0

        sOMP = 'OMP = %.2f (nmol/m$^3$/d)' % OMP
        sFsed = 'F$_{sed}$ = %.2f (mmol/m$^2$/d)' % Fsed
        sk = 'k = %.2f (m/d)' % k
        sKh = 'Kh = %.0f (m$^2$/d)' % kh
        subtitle = sOMP + ' ' +sFsed + ' '+ sk + ' ' + sKh
        fig, ax = plt.subplots(1, 1,figsize = (6,3))
        fig.suptitle(title, fontsize=14)
        ax.set_title(subtitle, fontsize=11)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fitdata = data.copy()
        fitx = fitdata.index.values.copy()
        fitx[fitx > R] = R
        fitdata = fitdata.set_index(fitx)
        n = 2
        if data.index.values.max() > R and 'OPT' in model:
            fitdata.plot(ax=ax, y='CH4', label='Samples-fitcorr', style='o', mfc='silver')
            n = 3
        data.plot(ax=ax, y='CH4', label='Samples', style='ko', mfc='k')
        if 'SENS' in model.upper():
            exp = model[model[:-3].rfind('-')+1:-3]
            label2 = '0.5'+exp
            label3 = '2'+exp
            x1 = modeldata[model][lake][date]['r1']
            x2 = modeldata[model][lake][date]['r2']
            x3 = modeldata[model][lake][date]['r3']
            y1 = modeldata[model][lake][date]['C']
            y2 = modeldata[model][lake][date]['C_05']
            y3 = modeldata[model][lake][date]['C_2']
            ax.plot(x1, y1, label=model, linestyle='-', color=colors[0])
            ax.plot(x2, y2, label=label2, linestyle='--')
            ax.plot(x3, y3, label=label3, linestyle=':')
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.21), ncol=5)
        else:
            modeldata[model][lake][date].plot(ax=ax, y='C', label=model, linestyle='-',
                    color=colors[0])
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.21), ncol=n)
        ax.set_xlabel('Distance from shore (m)')
        ax.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.11,
                        box.width, box.height * 0.9])
        now = datetime.now().strftime('%Y%m%d-%H')
        filefig = '_'. join([lake, date_str, model ,'transect-models', now])
        figpath = os.path.join(path_fig, 'Results', 'Modelling', model, 'Figures', now)
        if not os.path.exists(figpath):
            os.makedirs(figpath)
        filename = os.path.join(figpath, filefig)
        fig.savefig(filename +'.png', format='png', dpi=300)
        plt.close(fig)
        # Add model to plot with all models
        if makefig1 and 'SENS' not in model.upper():
            if not fitplot1:
                if data.index.values.max() > R and 'OPT' in model:
                    fitdata.plot(ax=ax1, y='CH4', label='Samples-fit', style='o', mfc='grey')
                    fitplot1 = True
                    nf+=1
                data.plot(ax=ax1, y='CH4', label='Samples', style='ko', mfc='k')
            modeldata[model][lake][date].plot(ax=ax1, y='C', label=model, linestyle='-',
                    color=colors[ci])
            plotfig1 = True
            nf+=1
        ci+=1
    if plotfig1 and 'SENS' not in model.upper():
        # Add legend to plot allmodels
        if nf>3:
            nf=3
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.21), ncol=nf, fontsize=10)

    if plotfig1:
        for model in modeldata:
            filefig = '_'. join([lake, date_str, *modeldata.keys() ,'transect-models', now])
            figpath = os.path.join(path_fig, 'Results', 'Modelling', model, 'Figures', now,
                    'Comparison')
            if not os.path.exists(figpath):
                os.makedirs(figpath)
            filename = os.path.join(figpath, filefig)
            fig1.savefig(filename +'.png', format='png', dpi=300)
        plt.close(fig1)
    else:
        if makefig1:
            plt.close(fig1)

def plot_scatter(data, modelparam, sct, path_fig):
    fig, ax = plt.subplots(1, 1, figsize=(4, 4))#, tight_layout=True)
    #title = 'Lake %s' % (lake)
    #fig.suptitle(title, fontsize=14)
    box = ax.get_position()
    sc_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    #mod_ix = find_nearest(la_t_data, modeldata)
    ax.set_position([box.x0 + 0.02, box.y0 + box.height * 0.01,
                 box.width, box.height * 0.85])
    ss_colors.append('b')
    lb = []
    ln = []
    lnsall = []
    lbsall = []
    maux = 0
    markers = ['o', 's', '^']
    for model in modelparam:
        lakes = modelparam[model].index.get_level_values('Lake').drop_duplicates()
        auxc = 0
        auxm = 0
        for lake in lakes:
            varx = sct[maux][0]
            vary = sct[maux][1]
            datax = modelparam[model].loc[lake][varx]
            datay = modelparam[model].loc[lake][vary]
            l1 = ax.scatter(datax, datay, marker=markers[auxm], label=lake, color=sc_colors[auxc])
    #        l2 = ax.scatter(data.CH4, ds_data.loc[ds_ix].CH4, marker='s', color=sc_colors[aux],
    #                   facecolors='w')
            if auxc >= 5*(1+auxm):
                auxc = 0
                auxm += 1
            else:
                auxc += 1
        ax.legend(loc='upper center', bbox_to_anchor=(0.5,1.30), ncol=3)
        #maxC = np.nanmax([datax.max(), datay.max()])
        #minC = np.nanmin([datax.min(), datay.min()])
        ax.set_xlabel(axislabels(varx))
        ax.set_ylabel(axislabels(vary))
        #ax.plot([minC, maxC], [minC, maxC], 'k-')
        #lns = [l1]
        #lbs = [model,model]

        now = datetime.now().strftime('%Y%m%d-%H')
        filefig = '_'. join([varx, vary, model ,'scatter-models', now])
        figpath = os.path.join(path_fig, 'Results', 'Modelling', model, 'Figures', now)
        if not os.path.exists(figpath):
            os.makedirs(figpath)
        filename = os.path.join(figpath, filefig)
        logging.info('Saving: %s' % filefig)
        fig.savefig(filename + '.png', format='png', dpi=300)
        plt.close(fig)
        """
        lnsall.append(lns)
        lbsall.append(lbs)
        ln.append(l1)
        lb.append(date_str)
        lg1 = plt.legend(lnsall[0], lbsall[0], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        lg2 = plt.legend(ln , lb, loc='upper center', bbox_to_anchor=(0.5, -0.27), ncol=3)
        plt.gca().add_artist(lg1)

        return fig, l1, lns, lbs
        """


def find_nearest(data, mdata):
    dx = data.index.values
    mx = mdata.index.values
    ix = []
    for x in dx:
        ix.append(np.abs(x - mx).argmin())
    return np.array(mx[ix])

def axislabels(var):
    var = var.upper()
    if 'KCH4' in var:
        label = u'K$_{CH_4}$ (m/d)'
    elif 'OMP' in var:
        label = u'OMP (mmol/m$^3$/d)'
    elif 'FSED' in var:
        label = u'F$_SED$ (mmol/m$^2$/d)'
    elif 'FA' in var:
        label = u'F$_a$ (mmol/m$^2$/d)'
    elif 'U10'  in var:
        label = u'U$_{10}$ (m/s)'
    elif 'CH4' in var:
        label = u'CH$_4$ (\u03BCmol/l)'
        if 'm' in var:
            label = u'CH$_{4,m}$ (\u03BCmol/l)'
    return label
