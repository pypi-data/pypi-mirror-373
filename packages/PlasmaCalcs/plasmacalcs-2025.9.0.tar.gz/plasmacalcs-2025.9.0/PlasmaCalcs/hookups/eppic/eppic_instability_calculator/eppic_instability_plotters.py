"""
File Purpose: KNOWN_PLOTTERS for EppicInstabilityCalculator
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from ....errors import PlottingAmbiguityError
from ....plotting import PlotterManager, plot_note
from ....tools import (
    simple_property,
    code_snapshot_info, Stopwatch,
    xr1d,
)


class EppicInstabilityPlotterManager(PlotterManager):
    '''EppicInstabilityCalculator plotting routines'''
    @known_plotter(kinds=['timelines', 'n_mul', 'runtime_info'], cost=10)
    def plot_min_n_nodes(ec, **kw_plot_settings):
        '''timelines of min_n_nodes vs n_mul (log2-log10 plot).
        Includes lines for:
            min_n_nodes_given_nsubdomains
            min_n_nodes_given_runtime_guess
        '''
        defaults_here = dict(robust=False, markersize=8)
        plt.figure(figsize=(6,3))
        arr = ec('log2_min_n_nodes_given_nsubdomains')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='(given nsubdomains)',
                         marker='o', fillstyle='none',
                         **{**defaults_here, **kw_plot_settings})
        plt.grid()
        # given runtime guess
        arr = ec('log2_min_n_nodes_given_runtime_guess')
        arr.pc.timelines(tCOORD, label='(given runtime guess)',
                         marker='x',
                         **{**defaults_here, **kw_plot_settings})
        # better labels
        plt.title(f'min_n_nodes\n{ec.title}', fontsize='small')
        pow2s = list(range(2,9))
        plt.yticks(pow2s, labels=[2**p for p in pow2s])
        plt.ylabel('min_n_nodes')
        plt.xlabel('log10_n_mul')
        return result

    @known_plotter(kinds=['timelines', 'n_mul', 'runtime_info'], cost=15)
    def plot_safe_node_hours(ec, **kw_plot_settings):
        '''timelines of safe_node_hours vs n_mul (log-log plot).
        Includes line for n_nodes = min, 4, 16, 64, 256.

        Compare with SU cost on Frontera (1 node-hour is 1 SU in 'normal' queue).
        '''
        defaults_here = dict(robust=False)
        plt.figure(figsize=(6,3))
        min_n_nodes = ec('min_n_nodes')
        arr = ec('log10_safe_node_hours', n_nodes=min_n_nodes)
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='n_nodes=(min_n_nodes)',
                         marker='X', color='black', ls='--', fillstyle='none',
                         **{**defaults_here, 'markersize': 8, **kw_plot_settings})
        plt.grid()
        # for a variety of n_nodes
        n_nodes = xr1d([4, 16, 64, 256], 'n_nodes')
        arr = ec('log10_safe_node_hours', n_nodes=n_nodes)
        arr.pc.timelines(tCOORD, marker='o', ls='-', alpha=0.5,
                         **{**defaults_here, 'markersize': 4, **kw_plot_settings})
        # better labels
        plt.title(f'log10_safe_node_hours\n{ec.title}', fontsize='small')
        plt.xlabel('log10_n_mul')
        # note about cost / cost(4). (i.e. "how much more expensive is this run than with n_nodes=4?)
        valrat = (10**(arr - arr.isel(n_nodes=0))).pc.squeeze_close(tol=0.05)
        if valrat.ndim==1:  # only varies in the n_nodes dim
            n0 = arr.coords['n_nodes'][0].item()
            strs = [f'{val.coords["n_nodes"]:3d} | {val.item():.2g}' for val in valrat]
            plot_note(f'nodes | cost÷cost({n0}):\n  '+'\n  '.join(strs),
                         xy='outside lower right', font='monospace', fontsize='small')
        return result

    @known_plotter(kinds=['timelines', 'n_mul', 'runtime_info'], cost=17)
    def plot_safe_runtime_seconds(ec, **kw_plot_settings):
        '''timelines of safe_runtime_seconds vs n_mul (log-log plot).
        Includes line for n_nodes = min, 4, 16, 64, 256.
        Also includes horizontal lines at 1 hour, 8 hours, and 48 hours.

        Compare with actual wall-clock time it takes to run the run.
        '''
        defaults_here = dict(robust=False)
        plt.figure(figsize=(6,3))
        # hlines (style: do 48 first since it will be above the others on the y-axis too)
        plt.axhline(np.log10(48 * 3600), color='gray', ls='--', label='(48 hours)')
        plt.axhline(np.log10(8 * 3600), color='gray', ls='-.', label='(8 hours)')
        plt.axhline(np.log10(1 * 3600), color='gray', ls=':', label='(1 hour)')
        # n_nodes=min
        min_n_nodes = ec('min_n_nodes')
        arr = ec('log10_safe_runtime_seconds', n_nodes=min_n_nodes)
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, label='n_nodes=(min_n_nodes)',
                         marker='X', color='black', ls='--', fillstyle='none',
                         **{**defaults_here, 'markersize': 8, **kw_plot_settings})
        plt.grid()
        # for a variety of n_nodes
        n_nodes = xr1d([4, 16, 64, 256], 'n_nodes')
        arr = ec('log10_safe_runtime_seconds', n_nodes=n_nodes)
        arr.pc.timelines(tCOORD, marker='o', ls='-', alpha=0.5,
                         **{**defaults_here, 'markersize': 4, **kw_plot_settings})
        # better labels
        plt.title(f'log10_safe_runtime_seconds\n{ec.title}', fontsize='small')
        plt.xlabel('log10_n_mul')
        plt.legend(bbox_to_anchor=(1.02, 0.95), loc='upper left', fontsize='small')
        # note about time(4) / time. (i.e. "how much less time does this run take than with n_nodes=4?)
        valrat = (10**(arr.isel(n_nodes=0) - arr)).pc.squeeze_close(tol=0.05)
        if valrat.ndim==1:
            n0 = arr.coords['n_nodes'][0].item()
            strs = [f'{val.coords["n_nodes"]:3d} | {val.item():.2g}' for val in valrat]
            plot_note(f'nodes | time({n0})÷time:\n  '+'\n  '.join(strs),
                         xy='outside lower right', font='monospace', fontsize='x-small')
        return result

    @known_plotter(kinds=['timelines', 'n_mul', 'runtime_info'], cost=11)
    def plot_safe_total_Gbytes(ec, **kw_plot_settings):
        '''timeline of safe_total_Gbytes vs n_mul (log-log plot).'''
        plt.figure(figsize=(5,2.5))
        arr = ec('log10_safe_total_Gbytes')
        if 'n_mul' not in arr.coords and 'log_n_mul' not in arr.coords:
            raise PlottingAmbiguityError('expected n_mul dependence')
        tCOORD = 'log_n_mul'
        result = arr.pc.timelines(tCOORD, marker='o', color='black')
        plt.grid()
        # better labels
        plt.title(f'log10_safe_total_Gbytes\n{ec.title}', fontsize='small')
        plt.xlabel('log10_n_mul')
        return result
