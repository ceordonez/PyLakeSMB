#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def normaldist(mu, th, T):
    sim = np.random.normal((mu / T), th / np.sqrt(T), T)
    return sim


def gammadist(mu, th, T):
    sim = np.random.gamma(mu**2 / th, th / mu, T)
    return sim


def mcs(mu, th, T, N, dist):
    """ Monte Carlo Simulations.

    Parameters
    ----------
    mu : E(X)
    th : std(X)
    T : 1
    N : number of simulations
    dist : distribution (norm of gamma)

    Return
    -------
    data : pandas series with N random value took it from distribution
    """

    data = []
    if mu == 0 and th == 0:
        data = np.zeros(N)
    else:
        for i in range(N):
            if dist == 'norm':
                simdata = normaldist(mu, th, T)
            elif dist == 'gamma':
                simdata = gammadist(mu, th**2, T)
            data.append(simdata[0])
        data = pd.Series(data)
    return data
