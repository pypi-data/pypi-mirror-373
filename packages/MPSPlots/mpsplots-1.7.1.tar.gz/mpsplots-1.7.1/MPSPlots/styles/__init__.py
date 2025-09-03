#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MPSPlots.directories import style_directory
import matplotlib.pyplot as plt

mps = style_directory.joinpath('mps_plot.mplstyle')

new_age = style_directory.joinpath('new_age.mplstyle')

gg_plot = style_directory.joinpath('ggplot.mplstyle')


def use_mpsplots_style():
    plt.style.use(mps)


def use_new_age_style():
    plt.style.use(new_age)


def use_ggplot_style():
    plt.style.use(gg_plot)


def use_default_style():
    plt.rcParams["mathtext.fontset"] = "dejavuserif"
    plt.rcParams["font.family"] = "serif"
