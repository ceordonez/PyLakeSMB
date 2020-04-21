#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import logging
import numpy as np
import pdb
import os

plt.style.use('seaborn')

def plot_transect(data, ph_data, ds_data, date_str, title, subtitle, lake,
                  path_fig, exp, save_fig, figtag):
    fig, ax = plt.subplots(1, 1,figsize = (6,3))
    fig.suptitle(title, fontsize=14)
    ax.set_title(subtitle, fontsize=11)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    label1 = exp
    data.plot(ax=ax, y='CH4', label='Samples', style='ko', mfc='k')
    ph_data.plot(ax=ax, y='C', label=label1, linestyle='-')
    ds_data.plot(ax=ax, y='CH4', label='DelSontro', linestyle='-')
    if 'Opt' not in exp:
        label2 = '0.5'+exp
        label3 = '2'+exp
        ph_data.plot(ax=ax, y='C_05', label=label2, linestyle='--')
        ph_data.plot(ax=ax, y='C_2', label=label3, linestyle=':')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.21), ncol=5)
    else:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.21), ncol=3)
    ax.set_xlabel('Distance from shore (m)')
    ax.set_ylabel(u'CH$_4$ (\u03BCmol/l)')
    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.11,
                    box.width, box.height * 0.9])
    if save_fig:
        filefig = lake + '_' + date_str + '_' + exp + '_transect-models.png'
        figpath = os.path.join(path_fig, 'Results', 'Modelling', exp, figtag,'Figures')
        if not os.path.exists(figpath):
            os.makedirs(figpath)
        filename = os.path.join(figpath, filefig)
        fig.savefig(filename, format='png', dpi=300)
        plt.close(fig)
    else:
        plt.show()

def plot_scatter(data, ph_data, ds_data, ds_ix, ph_ix, title, lake,
                 date_str, fig, ax, aux):
    fig.suptitle(title, fontsize=14)
    box = ax.get_position()
    sc_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    ax.set_position([box.x0, box.y0 + box.height * 0.07,
                 box.width, box.height * 0.95])
    l1 = ax.scatter(data.CH4, ph_data.loc[ph_ix].C_omp, marker='o',
               color=sc_colors[aux])
    l2 = ax.scatter(data.CH4, ds_data.loc[ds_ix].CH4, marker='s', color=sc_colors[aux],
               facecolors='w')
    ax.set_xlabel(u'CH$_4$ (\u03BCmol/l)')
    ax.set_ylabel(u'CH$_{4,model}$ (\u03BCmol/l)')
    maxC = max([data.CH4.max(), ph_data.loc[ph_ix].C.max(),
                ds_data.loc[ds_ix].CH4.max()])
    minC = min([data.CH4.min(), ph_data.loc[ph_ix].C.min(),
                ds_data.loc[ds_ix].CH4.min()])
    ax.plot([minC, maxC], [minC, maxC], 'k-')
    lns = [l1, l2]
    lbs = ['Ph_OMP','DelSontro']
    return fig, l1, lns, lbs

def plot_figures(data, ph_data, ds_data, mc_data, ds_param, opt_data,
                 path_fig, exp_name, save_fig, figtag):
    for lake in data:
        figsc, axsc = plt.subplots(1, 1, figsize=(4, 4))
        aux = 0
        lb = []
        ln = []
        lnsall = []
        lbsall = []
        for exp in exp_name:
            for date in data[lake]:
                # Select data
                la_t_data = data[lake][date]
                la_ph_data = ph_data[exp][lake][date]
                la_ds_data = ds_data[lake][date]
                k = ds_param.loc[lake,date].kch4
                kh = ds_param.loc[lake,date].Kh
                date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
                Fsed = mc_data.loc[lake, date_str].SedF_avg
                OMP = mc_data.loc[lake, date_str].OMP_avg
                if 'Fsed-Opt' in exp:
                    Fsed = opt_data.loc[lake, date][exp]
                    OMP = 0
                elif 'OMP-Opt' in exp:
                    OMP = opt_data.loc[lake, date][exp]
                elif 'k-Opt' in exp:
                    k = opt_data.loc[lake, date][exp]
                    OMP = 0

                sOMP = 'OMP = %.2f (nmol/m$^3$/d)' % OMP
                sFsed = 'F$_{sed}$ = %.2f (mmol/m$^2$/d)' % Fsed
                date_str = date[:4] + '-' + date[4:6] + '-' + date[6:]
                title = 'Lake %s %s' % (lake, date_str)
                sk = 'k = %.2f (m/d)' % k
                sKh = 'Kh = %.0f (m$^2$/d)' % kh
                subtitle = sOMP + ' ' +sFsed + ' '+ sk + ' ' + sKh
                plot_transect(la_t_data, la_ph_data, la_ds_data, date_str,
                            title, subtitle, lake, path_fig, exp, save_fig, figtag)
                """
                ds_ix = find_nearest(la_t_data, la_ds_data)
                ph_ix = find_nearest(la_t_data, la_ph_data)
                title = 'Lake %s' % (lake)
                figsc, l1, lns, lbs = plot_scatter(la_t_data, la_ph_data, la_ds_data, ds_ix, ph_ix, title,
                                lake, date_str, figsc, axsc, aux)
                lnsall.append(lns)
                lbsall.append(lbs)
                ln.append(l1)
                lb.append(date_str)
                aux+=1
                """
            """
            lg1 = plt.legend(lnsall[0], lbsall[0], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            lg2 = plt.legend(ln , lb, loc='upper center', bbox_to_anchor=(0.5, -0.27), ncol=3)
            plt.gca().add_artist(lg1)

            if save_fig:
                filefig = lake + '_' + date_str + '_' + 'scatter-models.png'
                figpath = os.path.join(path_fig, 'Results', 'Modelling','Figures')
                if not os.path.exists(figpath):
                    os.makedirs(figpath)
                filename = os.path.join(figpath, filefig)
                logging.info('Saving: %s' % filefig)
                figsc.savefig(filename, format='png', dpi=300)
                plt.close(figsc)
            else:
                plt.show()
            """
            # Plotting transect and models

def find_nearest(data, mdata):
    dx = data.index.values
    mx = mdata.index.values
    ix = []
    for x in dx:
        ix.append(np.abs(x - mx).argmin())
    return np.array(mx[ix])


