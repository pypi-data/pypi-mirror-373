"""
File Purpose: plotting routines by Sam
"""
import os

import matplotlib.pyplot as plt
import xarray as xr

from ....dimensions import (
    DimensionFractionalIndexer,
    IONS, ELECTRON,
)
from ....plotting import PlotterManager, CMAPS, cmap, Colormap
from ....tools import simple_property
from ....defaults import DEFAULTS


class EppicPlotterManagerSam(PlotterManager):
    '''eppic plotting routines by Sam'''

    # # # DEFAULTS # # #

    def _sam_timeline_defaults(ec, *, title=True):
        '''sets sam's defaults for timelines plots.
        calls plt.grid(), and plt.title(ec.title).
        '''
        plt.grid()
        if title: plt.title(ec.title)


    SAM_DEFAULTS = {
        # style for various physical parameters
        'n_style': dict(cmap='plasma', share_vlims='row'),
        'E_style': dict(cmap='cet_CET_R4' if Colormap.exists('cet_CET_R4') else 'rainbow', axsize=(2, 2)),
        'T_style': dict(cmap=CMAPS.get('T', 'cet_fire' if Colormap.exists('cet_fire') else 'inferno')),
        # ec.snap = sometimes, before doing plots of "images at a few snapshots"
        'sometimes': slice(None, None, 0.33),  # for "multifluid" case.
        'sometimes_style': dict(title_kw=dict(fontsize='small'), axsize=(1.5,1.5), subplot_title_width=15,
                                ),
        'manytimes': [0, 0.02, 0.04, 0.06, 0.08, 0.10,
                      0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                      0.50, 0.60, 0.70, 0.80, 0.90, -1],
        'manytimes_wrap': 6,
        'manytimes_style': dict(title_kw=dict(fontsize='small'), axsize=(1.5,1.5), subplot_title_width=15,
                                share_vlims='row',
                                ),
        # fft calcs for fft computations; fft style for fft plots (except "full" fft plots)
        'fft_calcs': dict(fft_keep=0.1, fft_half='x'),
        'fft_style': dict(min_n_ticks=(3,4), grid=True, robust=0.5, share_vlims='row'),
        'fft_fluids_style': dict(title_kw=dict(fontsize='xx-small'))
    }

    sam_defaults = simple_property('_sam_defaults', setdefaultvia='_default_sam_defaults',
        doc='''various defaults for sam's plotting.
        Editing ec.sam_defaults directly will change values for an instance.
        Editing ec.SAM_DEFAULTS directly will change values for all future instances.''')
    def _default_sam_defaults(self):
        '''returns a copy of self.SAM_DEFAULTS.
        Uses a somewhat hacky deepcopy for dicts - copies down 1 layer of dicts.
        E.g. ec.sam_defaults['fft_calcs'] is a copy of ec.SAM_DEFAULTS['fft_calcs'],
        but ec.sam_defaults['sometimes_style']['title_kw'] is the same object
            as ec.SAM_DEFAULTS['sometimes_style']['title_kw'], so, e.g.,
                ec.sam_defaults['sometimes_style']['title_kw']['fontsize'] = 'large'
                would affect all instances, while
                ec.sam_defaults['sometimes_style']['title_kw'] = {'fontsize': 'large'}
                would affect only the current instance, ec.
        '''
        result = self.SAM_DEFAULTS.copy()
        # copy down 1 layer of dicts
        for key, value in result.items():
            if isinstance(value, dict):
                result[key] = value.copy()
        return result

    def _extra_coords_with_title(self):
        '''return self.extra_coords with {'title': repr(self.title)} added,
        if self.title exists and 'title' not in self.extra_coords yet.
        else, just return self.extra_coords.
        '''
        extra_coords = self.extra_coords
        if 'title' in extra_coords:
            return extra_coords
        try:
            title = getattr(self, 'title')
        except AttributeError:
            return extra_coords
        else:
            return {**extra_coords, 'title': repr(title)}


    # # # DISPATCH # # #

    def sam_plots_lowres(ec, *, dst='plots_lowres/{savename}', dpi=100, bbox_inches='tight',
                        snap=slice(None, None, 0.0333), min_cost=None, max_cost=40, **kw):
        '''save sam's plots in lowres mode. return abspath to folder containing plots.'''
        log_extras = [f'Called sam_plots_lowres(min_cost={min_cost!r}, max_cost={max_cost!r})']
        with ec.using(snap=snap):
            ec.save_plots(who='sam', dst=dst, bbox_inches=bbox_inches, dpi=dpi,
                          min_cost=min_cost, max_cost=max_cost, log_extras=log_extras, **kw)
        if not os.path.isabs(dst):
            dst = os.path.join(ec.notes_dirname, dst)
        return os.path.dirname(dst)

    def sam_plots_midres(ec, *, dst='plots_midres/{savename}', dpi=200, bbox_inches='tight',
                        snap=slice(None, None, 0.01), min_cost=None, max_cost=None, **kw):
        '''save sam's plots in midres mode. return abspath to folder containing plots.'''
        log_extras = [f'Called sam_plots_midres(min_cost={min_cost!r}, max_cost={max_cost!r})']
        with ec.using(snap=snap):
            ec.save_plots(who='sam', dst=dst, bbox_inches=bbox_inches, dpi=dpi,
                          min_cost=min_cost, max_cost=max_cost, log_extras=log_extras, **kw)
        if not os.path.isabs(dst):
            dst = os.path.join(ec.notes_dirname, dst)
        return os.path.dirname(dst)

    def sam_plots_highres(ec, *, dst='plots_highres/{savename}', dpi=400, bbox_inches='tight',
                        snap=None, min_cost=None, max_cost=None, **kw):
        '''save sam's plots in highres mode. return abspath to folder containing plots.'''
        log_extras = [f'Called sam_plots_highres(min_cost={min_cost!r}, max_cost={max_cost!r})']
        with ec.using(snap=snap):
            ec.save_plots(who='sam', dst=dst, bbox_inches=bbox_inches, dpi=dpi,
                          min_cost=min_cost, max_cost=max_cost, log_extras=log_extras, **kw)
        if not os.path.isabs(dst):
            dst = os.path.join(ec.notes_dirname, dst)
        return os.path.dirname(dst)


    # # # VERY FAST PLOTS FIRST (I USED "COST=0" TO INDICATE THIS) # # #

    @known_plotter(who='sam', kinds=['timelines', 'moments', 'u', 'full'], cost=0)
    def plot_moment1(ec, **kw_plot_settings):
        '''moment1 timelines for all fluids.'''
        ec._sam_timeline_defaults()
        with ec.using(fluid=None, snap=None):
            return ec('moment1').pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'moments', 'T', 'full'], cost=0)
    def plot_Ta_from_moment2(ec, **kw_plot_settings):
        '''Ta_from_moment2 timelines for all fluids.'''
        ec._sam_timeline_defaults()
        with ec.using(fluid=None, snap=None):
            return ec('Ta_from_moment2').pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'moments', 'T', 'full'], cost=0)
    def plot_T_box(ec, **kw_plot_settings):
        '''T_box timelines for all fluids.'''
        ec._sam_timeline_defaults()
        with ec.using(fluid=None, snap=None):
            ec('T_from_moment2').pc.timelines(ls='--', label='(T_from_moment2)')
            ec('T_box').pc.timelines(label='(T_box)')


    # # # STATS # # #

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'n'], cost=30)
    def plot_n_stats(ec, **kw_plot_settings):
        '''number density stats timelines for all fluids.'''
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n')):
            arr = ec('log10_stats_n')[['min', 'mean', 'median', 'max']]
        arr = arr.to_dataarray().rename('log10_stats_n')
        ec._sam_timeline_defaults()
        return arr.pc.timelines(dims=['fluid', 'variable'], **kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'E'], cost=25)
    def plot_E_stats(ec, **kw_plot_settings):
        '''E-field (vector) stats timelines.'''
        with ec.using(snap=ec.where_loadable('phi', 'current_n')):
            arr = ec('stats_E')
        arr = arr.to_dataarray().rename('stats_E')
        ec._sam_timeline_defaults()
        return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'E'], cost=27)
    def plot_E_mod_stats(ec, **kw_plot_settings):
        '''E-field (mod) stats timelines.'''
        with ec.using(snap=ec.where_loadable('phi', 'current_n')):
            arr = ec('stats_mod_E')
        arr = arr.to_dataarray().rename('stats_mod_E')
        ec._sam_timeline_defaults()
        return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'u'], cost=27)
    def plot_u_mod_stats(ec, **kw_plot_settings):
        '''stats of u (mod) timelines for all ions and electrons.
        (electrons in a subplot above ions, if mean electrons |u| >> 3 * ions |u|.)
        '''
        with ec.using(snap=ec.where_loadable('flux', 'current_n')):
            arr = ec('stats_mod_u')[['min', 'mean', 'median', 'max']]
        u_e = arr.pc.isel(fluid=ELECTRON)
        u_i = arr.pc.isel(fluid=IONS)
        if u_e['mean'].mean() > 3 * u_i['mean'].mean():  # then put electrons on their own subplot
            u_e = u_e.to_dataarray().rename('stats_mod_u')
            u_i = u_i.to_dataarray().rename('stats_mod_u')
            colors = cmap('tab10').colors
            fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True,
                                    layout='constrained', squeeze=False,
                                    figsize=(10, 6), height_ratios=[1,3])
            # electrons subplot
            plt.sca(axs[0,0])
            ec._sam_timeline_defaults()
            efluid = u_e.coords['fluid'].item()
            kw = {'color': colors[0], 'cycles': [DEFAULTS.PLOT.TIMELINES_CYCLE1],
                  **kw_plot_settings}
            u_e.pc.timelines(label=f'fluid={efluid},', **kw)
            plt.xlabel('')
            # ions subplot
            plt.sca(axs[1,0])
            ec._sam_timeline_defaults(title=False)
            kw = {'cycles': [dict(color=colors[1:]), DEFAULTS.PLOT.TIMELINES_CYCLE1],
                 **kw_plot_settings}
            u_i.pc.timelines(dims=['fluid', 'variable'], **kw)
        else:  # everyone on the same plot
            arr = arr.to_dataarray().rename('stats_mod_u')
            ec._sam_timeline_defaults()
            return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'u'], cost=21)
    def plot_u_std(ec, **kw_plot_settings):
        '''std of u (vector) timelines for all ions and electrons.
        (electrons in a subplot above ions, if mean electrons std(u) >> 3 * ions std(u).)
        '''
        with ec.using(snap=ec.where_loadable('flux', 'current_n')):
            arr = ec('std_u')
        u_e = arr.pc.isel(fluid=ELECTRON)
        u_i = arr.pc.isel(fluid=IONS)
        if u_e.mean() > 3 * u_i.mean():  # then put electrons on their own subplot
            colors = cmap('tab10').colors
            fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True,
                                    layout='constrained', squeeze=False,
                                    figsize=(10, 6), height_ratios=[2,3])
            # electrons subplot
            plt.sca(axs[0,0])
            ec._sam_timeline_defaults()
            efluid = u_e.coords['fluid'].item()
            kw = {'color': colors[0], 'cycles': [DEFAULTS.PLOT.TIMELINES_CYCLE1],
                  **kw_plot_settings}
            u_e.pc.timelines(label=f'fluid={efluid}', **kw)
            plt.xlabel('')
            # ions subplot
            plt.sca(axs[1,0])
            ec._sam_timeline_defaults(title=False)
            kw = {'cycles': [dict(color=colors[1:]), DEFAULTS.PLOT.TIMELINES_CYCLE1],
                 **kw_plot_settings}
            u_i.pc.timelines(**kw)
        else:  # everyone on the same plot
            ec._sam_timeline_defaults()
            return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'stats', 'u'], cost=21)
    def plot_u_std_mod(ec, **kw_plot_settings):
        '''std of u (mod) timelines for all ions and electrons.
        (electrons in a subplot above ions, if mean electrons std(u) >> 3 * ions std(u).)
        '''
        with ec.using(snap=ec.where_loadable('flux', 'current_n')):
            arr = ec('std_mod_u')
        u_e = arr.pc.isel(fluid=ELECTRON)
        u_i = arr.pc.isel(fluid=IONS)
        if u_e.mean() > 3 * u_i.mean():  # then put electrons on their own subplot
            colors = cmap('tab10').colors
            fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True,
                                    layout='constrained', squeeze=False,
                                    figsize=(10, 6), height_ratios=[2,3])
            # electrons subplot
            plt.sca(axs[0,0])
            ec._sam_timeline_defaults()
            efluid = u_e.coords['fluid'].item()
            u_e.pc.timelines(label=f'fluid={efluid}', color=colors[0], **kw_plot_settings)
            plt.xlabel('')
            # ions subplot
            plt.sca(axs[1,0])
            ec._sam_timeline_defaults(title=False)
            kw = {'cycles': [dict(color=colors[1:]), DEFAULTS.PLOT.TIMELINES_CYCLE1],
                 **kw_plot_settings}
            u_i.pc.timelines(**kw)
        else:  # everyone on the same plot
            ec._sam_timeline_defaults()
            return arr.pc.timelines(**kw_plot_settings)


    # # # LN_STD_DETAFRAC_N # # #

    @known_plotter(who='sam', kinds=['timelines', 'growth', 'instability', 'n'], cost=27)
    def plot_ln_std_deltafrac_n(ec, **kw_plot_settings):
        '''ln_std_deltafrac_n timelines for all fluids.'''
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n')):
            arr = ec('ln_std_deltafrac_n')
        ec._sam_timeline_defaults()
        return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'growth', 'instability', 'n'], cost=35)
    def plot_ln_std_blur_deltafrac_n(ec, **kw_plot_settings):
        '''ln_std_blur_deltafrac_n timelines for all fluids, for blur_sigma in [0, 1, 10, 20]'''
        BLURS = [0, 1, 10, 20]
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n')):
            arr = xr.Dataset({blur: ec('ln_std_blur_deltafrac_n', blur_sigma=blur) for blur in BLURS})
        ec._sam_timeline_defaults()
        arr = arr.to_dataarray('blur').rename('ln_std_blur_deltafrac_n')
        return arr.pc.timelines(dims=['fluid', 'blur'], **kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'growth', 'instability', 'tfbi', 'n'], cost=28)
    def plot_ddt_ln_std_deltafrac_n(ec, **kw_plot_settings):
        '''ddt_ln_std_deltafrac_n timelines for all fluids.'''
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n')):
            arr = ec('ddt_ln_std_deltafrac_n')
        ec._sam_timeline_defaults()
        kw_plot_settings.setdefault('robust', 5)
        return arr.pc.timelines(**kw_plot_settings)

    @known_plotter(who='sam', kinds=['timelines', 'growth', 'instability', 'tfbi', 'n'], cost=36)
    def plot_ddt_ln_std_blur_deltafrac_n(ec, **kw_plot_settings):
        '''ddt_ln_std_blur_deltafrac_n timelines for all fluids, for blur_sigma in [0, 1, 10, 20]'''
        BLURS = [0, 1, 10, 20]
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n')):
            arr = xr.Dataset({blur: ec('ddt_ln_std_blur_deltafrac_n', blur_sigma=blur) for blur in BLURS})
        ec._sam_timeline_defaults()
        arr = arr.to_dataarray('blur').rename('ddt_ln_std_blur_deltafrac_n')
        kw_plot_settings.setdefault('robust', 5)
        return arr.pc.timelines(dims=['fluid', 'blur'], **kw_plot_settings)


    # # # VALUES VS SPACE # # #

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'movie', 'n', 'long', 'at_snap'], cost=70)
    def plot_deltafrac_n(ec, **kw_plot_settings):
        '''deltafrac_n movie for all fluids, all current snaps (in self.snap).'''
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n'),
                      extra_coords=ec._extra_coords_with_title()):
            arr = ec('deltafrac_n')
        kw = {'top': 0.65,  # fudge factor for prettier subplot spacing
                **ec.sam_defaults['n_style'], **kw_plot_settings}
        return arr.pc.subplots(row='fluid', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'n', 'sometimes'], cost=15)
    def plot_deltafrac_n_sometimes(ec, **kw_plot_settings):
        '''deltafrac_n at some times (ec.sam_defaults['sometimes']) for all fluids.'''
        # could just do where_loadable('n'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(fluid=None, snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
                arr = ec('deltafrac_n')
        kw = {**ec.sam_defaults['n_style'], **ec.sam_defaults['sometimes_style'],
                'title':'snap={snap}, t={t:.3g},\n{fluid}',
                **kw_plot_settings}
        return arr.pc.subplots(row='fluid', col='snap', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'n', 'manytimes'], cost=14)
    def plot_deltafrac_ne_manytimes(ec, **kw_plot_settings):
        '''deltafrac_n for electrons at "many" times (ec.sam_defaults['manytimes']).'''
        manysnaps = ec.where_loadable('n').get(DimensionFractionalIndexer(ec.sam_defaults['manytimes']))
        with ec.using(fluid=ELECTRON, snap=manysnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('deltafrac_n')
        kw = {**ec.sam_defaults['manytimes_style'],
              **ec.sam_defaults['n_style'],
              **kw_plot_settings}
        if arr.sizes['snap'] > ec.sam_defaults['manytimes_wrap']:
            kw['wrap'] = ec.sam_defaults['manytimes_wrap']
        return arr.pc.subplots(row='snap', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'E', 'sometimes'], cost=11)
    def plot_E_mod_sometimes(ec, **kw_plot_settings):
        '''mod_E at some times (ec.sam_defaults['sometimes'])'''
        # could just do where_loadable('phi'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('log10_mod_E')
        kw = {'top': 1.5,  # fudge factor for prettier subplot spacing
                **ec.sam_defaults['sometimes_style'], **ec.sam_defaults['E_style'], **kw_plot_settings}
        return arr.pc.subplots(col='snap', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'u', 'sometimes'], cost=16)
    def plot_u_mod_sometimes(ec, **kw_plot_settings):
        '''mod_u at some times (ec.sam_defaults['sometimes'])'''
        # could just do where_loadable('flux'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('mod_u')
        kw = {**ec.sam_defaults['sometimes_style'],
                'top': 1.0,  # fudge factor for prettier subplot spacing
                'title':'snap={snap}, t={t:.3g},\n{fluid}',
                **kw_plot_settings}
        return arr.pc.subplots(row='fluid', col='snap', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'T', 'sometimes'], cost=18)
    def plot_T_sometimes(ec, **kw_plot_settings):
        '''T at some times (ec.sam_defaults['sometimes'])'''
        # could just do where_loadable('nvsqr'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('T')
        kw = {**ec.sam_defaults['sometimes_style'],
                **ec.sam_defaults['T_style'],
                'top': 1.0,  # fudge factor for prettier subplot spacing
                'title':'snap={snap}, t={t:.3g},\n{fluid}',
                **kw_plot_settings}
        return arr.pc.subplots(row='fluid', col='snap', **kw)


    # # # FFT (deltafrac_n) # # #

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'n', 'sometimes'], cost=22)
    def plot_deltafrac_n_abs_radfft_sometimes(ec, **kw_plot_settings):
        '''abs_radfft_deltafrac_n at some times (ec.sam_defaults['sometimes']) for all fluids.
        Not the full region of k-space; see also plot_deltafrac_n_abs_radfft_full.
        '''
        # could just do where_loadable('n'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(fluid=None, snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('abs_radfft_deltafrac_n', **ec.sam_defaults['fft_calcs'])
        kw = {**ec.sam_defaults['sometimes_style'],
              **ec.sam_defaults['fft_style'],
              **ec.sam_defaults['fft_fluids_style'],
              'title':'snap={snap},\nt={t:.3g},\n{fluid}',
              **kw_plot_settings}
        result = arr.pc.subplots(row='fluid', col='snap', **kw)
        result.scatter_max() # put markers at maximum on each subplot.
        return result

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'n', 'sometimes'], cost=27)
    def plot_deltafrac_n_blurk_abs_radfft_sometimes(ec, **kw_plot_settings):
        '''blurk_abs_radfft_deltafrac_n at some times (ec.sam_defaults['sometimes']) for all fluids.'''
        blur = {'blur_sigma': 1}
        # could just do where_loadable('n'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(fluid=None, snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('blurk_abs_radfft_deltafrac_n', **ec.sam_defaults['fft_calcs'], **blur)
        kw = {**ec.sam_defaults['sometimes_style'],
              **ec.sam_defaults['fft_style'],
              **ec.sam_defaults['fft_fluids_style'],
              'title':'snap={snap},\nt={t:.3g},\n{fluid}',
              **kw_plot_settings}
        result = arr.pc.subplots(row='fluid', col='snap', **kw)
        result.scatter_max() # put markers at maximum on each subplot.
        return result

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'n', 'sometimes'], cost=23)
    def plot_deltafrac_n_abs_radfft_full_sometimes(ec, **kw_plot_settings):
        '''abs_radfft_deltafrac_n at some times (ec.sam_defaults['sometimes']) for all fluids.
        Includes the full region of k-space; see also plot_deltafrac_n_abs_radfft_full.
        '''
        fft_full = dict(fft_slices={})  # <-- full region of k-space
        # could just do where_loadable('n'), but we want to overlap with the other 'sometimes' plots
        somesnaps = ec.where_loadable(['n', 'phi', 'flux', 'nvsqr'])
        somesnaps = somesnaps.get(ec.sam_defaults['sometimes'])
        with ec.using(fluid=None, snap=somesnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('abs_radfft_deltafrac_n', **fft_full)
        kw = {**ec.sam_defaults['sometimes_style'],
                'top': 1.0,  # fudge factor for prettier subplot spacing
                'title':'snap={snap}, t={t:.3g},\n{fluid}',
                **kw_plot_settings}
        return arr.pc.subplots(row='fluid', col='snap', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'n', 'movie', 'long'], cost=71)
    def plot_deltafrac_n_abs_radfft(ec, **kw_plot_settings):
        '''abs_radfft_deltafrac_n movie for all fluids, all current snaps (in self.snap).
        Not the full region of k-space.
        '''
        with ec.using(fluid=None, snap=ec.where_loadable('n', 'current_n'),
                      extra_coords=ec._extra_coords_with_title()):
            arr = ec('abs_radfft_deltafrac_n', **ec.sam_defaults['fft_calcs'])
        kw = {**ec.sam_defaults['fft_style'],
              **ec.sam_defaults['fft_fluids_style'],
              'title': '{fluid}',
              'top': 0.5, # fudge factor for prettier subplot spacing
              **kw_plot_settings}
        return arr.pc.subplots(row='fluid', **kw)

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'n', 'movie'], cost=75)
    def plot_deltafrac_n_blurk_abs_radfft(ec, **kw_plot_settings):
        '''blurk_abs_radfft_deltafrac_n movie for all fluids, all current snaps (in self.snap).
        Not the full region of k-space. Uses blur_sigma=1.
        '''
        blur = {'blur_sigma': 1}
        with ec.using(fluid=None, snap=ec.where_loadable('n', ec.snap_list()),
                      extra_coords=ec._extra_coords_with_title()):
            arr = ec('blurk_abs_radfft_deltafrac_n', **ec.sam_defaults['fft_calcs'], **blur)
        kw = {**ec.sam_defaults['fft_style'],
              **ec.sam_defaults['fft_fluids_style'],
              'title': '{fluid}',
              'top': 0.5, # fudge factor for prettier subplot spacing
              **kw_plot_settings}
        return arr.pc.subplots(row='fluid', **kw)


    # # # FFT (|E|**2) # # #

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'E', 'manytimes'], cost=21)
    def plot_E_mod2_abs_radfft_manytimes(ec, **kw_plot_settings):
        '''abs_radfft_delta_mod2_E at "many" times (ec.sam_defaults['manytimes']).'''
        manysnaps = ec.where_loadable('phi').get(DimensionFractionalIndexer(ec.sam_defaults['manytimes']))
        with ec.using(snap=manysnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('abs_radfft_delta_mod2_E', **ec.sam_defaults['fft_calcs'])
        kw = {**ec.sam_defaults['manytimes_style'],
              **ec.sam_defaults['fft_style'],
              'title':'snap={snap},\nt={t:.3g}',
              **kw_plot_settings}
        if arr.sizes['snap'] > ec.sam_defaults['manytimes_wrap']:
            kw['wrap'] = ec.sam_defaults['manytimes_wrap']
        result = arr.pc.subplots(row='snap', **kw)
        result.scatter_max() # put markers at maximum on each subplot.
        return result

    @known_plotter(who='sam', kinds=['2D', 'subplots', 'fft', 'E', 'manytimes'], cost=12)
    def plot_E_mod2_blurk_abs_radfft_manytimes(ec, **kw_plot_settings):
        '''abs_radfft_delta_mod2_E at "many" times (ec.sam_defaults['manytimes']).'''
        manysnaps = ec.where_loadable('phi').get(DimensionFractionalIndexer(ec.sam_defaults['manytimes']))
        blur = {'blur_sigma': 1}
        with ec.using(snap=manysnaps, extra_coords=ec._extra_coords_with_title()):
            arr = ec('blurk_abs_radfft_delta_mod2_E', **ec.sam_defaults['fft_calcs'], **blur)
        kw = {**ec.sam_defaults['manytimes_style'],
              **ec.sam_defaults['fft_style'],
              'title':'snap={snap},\nt={t:.3g}',
              **kw_plot_settings}
        if arr.sizes['snap'] > ec.sam_defaults['manytimes_wrap']:
            kw['wrap'] = ec.sam_defaults['manytimes_wrap']
        result = arr.pc.subplots(row='snap', **kw)
        result.scatter_max() # put markers at maximum on each subplot.
        return result
