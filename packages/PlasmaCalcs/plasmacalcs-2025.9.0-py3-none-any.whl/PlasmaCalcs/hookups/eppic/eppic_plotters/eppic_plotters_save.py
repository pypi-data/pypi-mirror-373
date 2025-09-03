"""
File Purpose: plotting routines by Save
"""

import matplotlib.pyplot as plt

from ....plotting import PlotterManager


class EppicPlotterManagerSave(PlotterManager):
    '''eppic plotting routines by Save.
    Consider using EppicCalculator.make_plots(who='save') to make all the plots.
    '''

    # remember to say who='save' for each of these!
    @known_plotter(who='save')
    def plot_moment1_specie0(ec, **kw_plot_settings):
        '''plot the first moment of the simulation for specie0'''
        result = ec('moment1', fluid=0).pc.timelines(**kw_plot_settings)
        plt.title(f'{ec.title}, species={ec.fluids.get(0)}')
        return result
