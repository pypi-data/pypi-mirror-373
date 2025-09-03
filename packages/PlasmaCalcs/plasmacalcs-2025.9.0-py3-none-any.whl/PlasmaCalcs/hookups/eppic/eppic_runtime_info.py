"""
File Purpose: reading runtime info for EppicCalculator

this is the timing information from the timers.dat file.
"""
import numpy as np
import xarray as xr

from .eppic_io_tools import read_timers_dat, eppic_clock_times_here
from ...quantities import QuantityLoader
from ...tools import (
    alias,
    find_jobfiles,
    xarray_promote_dim, xarray_sum,
)

class EppicRuntimeInfoLoader(QuantityLoader):
    '''runtime info for EppicCalculator.'''

    # # # FROM LOG FILE # # #

    def jobfiles(self):
        '''return list of all jobfiles within self.dirname directory.'''
        return find_jobfiles(self.dirname)

    logfiles = alias('jobfiles')

    def clock_times(self):
        '''return dict of clock times from this run. (From reading self.jobfiles.)
        Result can have keys:
            'start': datetime telling when the run started.
            'stepstart': datetime telling when the iterations started.
            'end': datetime telling when the run ended.
            'init_seconds': (stepstart - start) [seconds]
            'steps_seconds': (end - stepstart) [seconds]
            'total_seconds': (end - start) [seconds]
        If jobfile missing any info, relevant keys will not appear in result.
        '''
        return eppic_clock_times_here(self.dirname)

    @known_var
    def get_clock_times(self):
        '''dataset of clock times from this run. (From reading self.jobfiles.)
        Result can have keys:
            'start': datetime telling when the run started.
            'stepstart': datetime telling when the iterations started.
            'end': datetime telling when the run ended.
            'init_seconds': (stepstart - start) [seconds]
            'steps_seconds': (end - stepstart) [seconds]
            'total_seconds': (end - start) [seconds]
        If jobfile missing any info, relevant keys will not appear in result.
        '''
        return xr.Dataset(self.clock_times())

    @known_var(deps=['clock_times'])
    def get_init_seconds(self):
        '''time [in seconds] spent initializing the run. (between start and when steps start.)'''
        return self('clock_times')['init_seconds']

    @known_var(deps=['clock_times'])
    def get_steps_seconds(self):
        '''time [in seconds] spent doing timesteps. (total duration minus init_seconds.)'''
        return self('clock_times')['steps_seconds']

    @known_var(deps=['clock_times'], aliases=['total_time_seconds'])
    def get_total_seconds(self):
        '''duration [in seconds] spent to run the entire run.'''
        return self('clock_times')['total_seconds']


    # # # FROM TIMERS.DAT # # #

    def timers_dat(self, *, with_snaps=False, as_array=False):
        '''return timers.dat as an xarray.Dataset. (dimension will be named 'it')
        result will have the same units as timers.dat file.

        with_snaps: bool
            if True, attach snap & t coords and promote 'snap' to main dim.
            based on self.snaps (not self.snap)
        as_array: bool
            whether to use xarray.Dataset.to_array() to return a DataArray instead of Dataset.
            if True, vars from Dataset will be concatenated along the new dimension named 'timer'.
        '''
        result = read_timers_dat(self.dirname, as_array=as_array, # [TODO][EFF] use caching if this is slow.
                                fix_snaps=(self.snaps_from=='parallel'))
        if with_snaps:
            existing_snaps = self.existing_snaps()
            result = self.assign_snap_along(result, 'it', existing_snaps)
            result = xarray_promote_dim(result, 'snap')
            if len(existing_snaps) != len(self.snaps):  # some self.snaps refer to MISSING_SNAP
                # fill MISSING_SNAP points with NaN.
                result = result.reindex(snap=self.snaps, fill_value=self.snap_dim.NAN)
                # assign t coords to MISSING_SNAP points  # [TODO][EFF] do something more efficient?
                result = self.assign_snap_along(result, 'snap', self.snaps)
            result = result.drop_vars('it')
        return result

    @known_var(dims=['snap'])
    def get_timers(self):
        '''timers_dat info as an xarray.Dataset, at snaps in self.snap. see also: 'runtimes'.'''
        result = self.timers_dat(with_snaps=True, as_array=False)
        result = result.sel(snap=np.array(self.snap))
        return result

    @known_var(dims=['snap'])
    def get_runtimes(self):
        '''timers_dat info as an xarray.DataArray, at snaps in self.snap. see also: 'timers'.'''
        result = self.timers_dat(with_snaps=True, as_array=True)
        result = result.sel(snap=np.array(self.snap))
        return result

    @known_var(deps=['timers'])
    def get_run_time(self):
        '''Wall clock runtime for each snap. Same units as timers_dat info.'''
        return self('timers')['Wall Clock']

    @known_var(deps=['timers'])
    def get_write_time(self):
        '''time spent writing output files. Same units as timers_dat info.'''
        return self('timers')['output']

    @known_var(deps=['run_time', 'write_time'])
    def get_calc_time(self):
        '''Wall clock runtime, ignoring time spent writing output files. Same units as timers_dat info.'''
        return self('run_time') - self('write_time')

    @known_pattern(r'(write|calc)_time_frac', deps=['run_time', {0: '{group0}_time'}])
    def get_time_frac(self, var, *, _match=None):
        '''fraction of runtime spent on writing or calculating.
            var='write_time_frac' --> fraction of runtime spent writing output files.
            var='calc_time_frac' --> fraction of runtime spent calculating, ignoring write_time.
        '''
        here, = _match.groups()
        return self(f'{here}_time') / self('run_time')

    @known_pattern(r'(run|calc|write)_(timestep|dt)_cost(_f|_nosub|_fnosub|_nosubf)?',
            deps=['nit_since_prev', 'npd', {0: '{group0}_time'},
                {2: lambda groups: 'subcycle' if (groups[2] is not None and 'sub' in groups[2]) else []}])
    def get_timestep_cost_or_dt_cost(self, var, *, _match=None):
        '''total cpu time per simulated particle, per timestep (or per dt).
        
        time_cost = (runtime / timestep_or_dt) * (n_processors / total number of particles)
        total number of particles = n_processors * npart.
            Note: n_processors cancels out; time_cost = (runtime / timestep_or_dt) / npart
        timestep_or_dt = one timestep or one dt; see below.
        npart = number of simulated particles, in one processor. Depends on {settings}; see below.

        '{clock}_{time}_cost{settings}'
            E.g. 'run_timestep_cost', 'write_dt_cost_f', 'calc_dt_cost_nosubf'
            {clock} = 'run', 'calc', or 'write'
                tells which clock to use.
                'run' --> 'Wall clock' | 'calc' --> 'Wall Clock - output' | 'write' --> 'output'
            {time} = 'timestep' or 'dt'
                'timestep' --> report result as cost per timestep, regardless of dt.
                'dt'       --> report result as cost per dt (converted to SI units).
            {settings} = '', '_f', '_nosub', '_fnosub', or '_nosubf'
                tells whether to return a separate value for each fluid, and whether to account for subcycling.
                    ''        --> single value. account for subcycling.     npart = self('npd/subcycle').sum('fluid')
                    '_nosub'  --> single value. ignore subcycling.          npart = self('npd').sum('fluid')
                    '_f'      --> per-fluid values. account for subcycling. npart = self('npd/subcycle')
                    '_fnosub' --> per-fluid values. ignore subcycling.      npart = self('npd')
                    '_nosubf' --> same as '_fnosub'; provided for convenience.

                accounting for subcycling means dividing by the subcycling factor,
                because less effort is spent on subcycled distributions.
        '''
        clock, time, settings = _match.groups()
        clock_per_timestep = self(f'{clock}_time') / self('nit_since_prev')
        # get npart
        if settings is None:
            settings = ''
        if 'f' in settings:
            npart = self('npd')
            if 'nosub' not in settings:
                npart = npart / self('subcycle')
        else:
            with self.using(fluid=None):
                npart = self('npd')
                if 'nosub' not in settings:
                    npart = npart / self('subcycle')
                npart = xarray_sum(npart, 'fluid')
        result = clock_per_timestep / npart
        if time == 'dt':
            result = self.record_units(result / self.input_deck['dt'])
        elif time == 'timestep':
            pass  # already divided by timestep.
        else:
            raise NotImplementedError(f'coding error, expected time="timestep" or "dt", got {time!r}')
        return result


    # # # CONVERTING BETWEEN TIMERS.DAT <--> SECONDS # # #

    @known_var(deps=['run_time', 'steps_seconds'])
    def get_timer2seconds(self):
        '''conversion factor from timers.dat units to seconds.
        E.g. timer2seconds = 0.01 <--> 1 timer unit = 0.01 seconds <--> 1 second = 100 timer units.

        timer2seconds = steps_seconds / sum(run_time)
        Might vary from machine to machine. Seems to be 0.01 on Frontera (plus small rounding errors).
        '''
        return self('steps_seconds') / self('run_time').sum()

    @known_var(deps=['timer2seconds'])
    def get_seconds2timer(self):
        '''conversion factor from seconds to timers.dat units.
        E.g. seconds2timer = 100 <--> 1 timer unit = 0.01 seconds <--> 1 second = 100 timer units.

        seconds2timer = sum(run_time) / steps_seconds
        Might vary from machine to machine. Seems to be 100 on Frontera (plus small rounding errors).
        '''
        return 1 / self('timer2seconds')


    # # # TRYING TO "GUESS" RUNTIME PER TIMESTEP # # #

    # stats from some (~100) 2D runs I (sam) have on my machine,
    #   when computing 'log10_meant_cpu_seconds_per_each'.
    #   Excluded runs with ncells_sim <= 128**2 (because small runs timing isn't as important to get right)
    #       and runs with nx >= 20 (because I don't have enough runs to learn dependence with nsubdomains < max,
    #           and max nsubdomains is when nx = 8. Closest-to-optimal safe nsubdomains is when nx = 16.)
    CPU_SECONDS_PER_EACH_INFO = {
        'timers': ['vadv time', 'xadv time', 'charge', 'collect', 'efield', 'output'],
        'timer_shorthand': ['vadv', 'xadv', 'charge', 'collect', 'efield', 'output'],
        'stats': {
            'min': [-7.60274492, -8.08801379, -8.29066597, -6.4194993 , -6.45974422, -9.13447354],
            'mean': [-7.14767658, -7.71036947, -8.16571132, -5.41090113, -5.84219558, -8.26272736],
            'median': [-7.14165344, -7.7622515 , -8.18222028, -5.4868952 , -5.83410388, -8.29974968],
            'max': [-6.64987625, -6.85562141, -7.85642911, -4.26655371, -5.16467001, -6.96257236],
            'std': [0.1618933 , 0.24986124, 0.07723055, 0.39052264, 0.27228036, 0.41827969],
        },
        # arr.polyfit(log10_n_nodes, degree=1) where arr==log10_meant_cpu_seconds_per_each.
        'polyfit_n_nodes': {
            'coeff': {   # coeffs for each degree. Direct result of polyfit.
                1: [ 0.07367062,  0.33485588,  0.07118243,  0.98491967,  0.76134439,  0.42652909],
                0: [-7.23738158, -8.11810654, -8.25238656, -6.61018799, -6.76924614, -8.78209026],
            },
            'std': {   # stddev on coeffs for each degree. Larger stddev --> less certainty on coeff result.
                1: [0.05228419, 0.07328888, 0.02404283, 0.07154953, 0.03530289, 0.12873761],
                0: [0.06593647, 0.09242584, 0.03032081, 0.09023231, 0.04452106, 0.16235315],
            },
        },
        # which timers we should actually use polyfit_n_nodes for, when guessing runtime.
        #   default is ['collect', 'efield'] because those have smaller std & (max-min) after detrending
        #   (and since the fit is in logspace, that should directly cause smaller error in predictions).
        'polyfit_n_nodes_apply': ['collect', 'efield'],
    }

    @known_pattern(r'guess_cpu_seconds_(all|vadv|xadv|charge|collect|efield|output)_per_each(_safe|)',
                   deps=['n_nodes'])
    def get_guess_cpu_seconds_per_each(self, var, *, _match=None):
        '''guess log10(cpu seconds per (particle, per) grid cell, per timestep), for the indicated timer.
        if 'safe' included in var, uses mean + stddev instead of just mean, to get a conservative estimate.
        Result excludes initialization time (before iterations begin).

        timer options:
            'all': result will be a Dataset of results from all timers, with timer names as data_vars.
                    (timer names are 'vadv time', 'xadv time', 'charge', 'collect', 'efield', 'output'.)
            'vadv', 'xadv', 'charge', 'collect', 'efield', 'output': result for corresponding timer.

        if timer is 'all', return sum of the results from other timers.

        These results are per particle per grid cell per timestep:
            'vadv time', 'xadv time', 'charge', 'output'.
        These results are per particle per timestep:
            'collect', 'efield'.

        The guess is informed by self.CPU_SECONDS_PER_EACH_INFO,
            which contains numerical values derived from some simulations run on Frontera.
        Assumes 'output' is not very expensive.
            The "output" timer was not tested across a large variety of 'nout'.
            (trying to detrend with respect to nout didn't affect stddev significantly.)
        '''
        here, safe = _match.groups()
        INFO = self.CPU_SECONDS_PER_EACH_INFO
        if here == 'all':
            result = {}
            for i, timer_shorthand in enumerate(INFO['timer_shorthand']):
                timer = INFO['timers'][i]
                result[timer] = self(f'guess_cpu_seconds_{timer_shorthand}_per_each{safe}')
            return xr.Dataset(result)
        # else, getting result for an individual timer.
        i = INFO['timer_shorthand'].index(here)
        timer = INFO['timers'][i]
        if timer in INFO['polyfit_n_nodes_apply']:
            log_n_nodes = self('log10_n_nodes')
            pfit = INFO['polyfit_n_nodes']
            coeff1 = pfit['coeff'][1][i]
            coeff0 = pfit['coeff'][0][i]
            if safe:
                coeff1 = coeff1 + pfit['std'][1][i]
                coeff0 = coeff0 + pfit['std'][0][i]
            guess = coeff1 * log_n_nodes + coeff0
        else:
            guess = INFO['stats']['mean'][i]
            if safe:
                guess = guess + INFO['stats']['std'][i]
        # above, got log10(guess). Exponentiate and return:
        return xr.DataArray(10**guess)

    @known_pattern(r'guess_cpu_seconds_(all|sum|vadv|xadv|charge|collect|efield|output)_per_(timestep|ct)(_safe|)',
                   deps=[{1: 'cpu_per_each2{group1}'}, {2: 'guess_cpu_seconds_all_per_each{group2}'}])
    def get_guess_cpu_seconds_per_timestep_or_ct(self, var, *, _match=None):
        '''guess cpu seconds required per (cell, per) timestep, for the indicated timer.
        if 'safe' included in var, uses mean + stddev instead of just mean, to get a conservative estimate.
        Use 'ct' to indicate 'per cell per timestep'.
            (result using 'timestep') == ncells_sim * (result using 'ct').
        Result excludes initialization time (before iterations begin).

        timer options:
            'all': result will be a Dataset of results from all timers, with timer names as data_vars.
                    (timer names are 'vadv time', 'xadv time', 'charge', 'collect', 'efield', 'output'.)
            'sum': result will be the sum of the results from other timers.
            'vadv', 'xadv', 'charge', 'collect', 'efield', 'output': result for corresponding timer.

        Assumes 'output' is not very expensive; it was not tested as much as the others.
        The guess is informed by self.CPU_SECONDS_PER_EACH_INFO.
        For more details see: guess_cpu_seconds_per_each.
        '''
        here, ct, safe = _match.groups()
        INFO = self.CPU_SECONDS_PER_EACH_INFO
        if here == 'all' or here == 'sum':
            result = {}
            for i, timer_shorthand in enumerate(INFO['timer_shorthand']):
                timer = INFO['timers'][i]
                result[timer] = self(f'guess_cpu_seconds_{timer_shorthand}_per_{ct}{safe}')
            if here == 'all':
                return xr.Dataset(result)
            else:  # here == 'sum'
                return sum(result.values())
        # else, getting result for an individual timer.
        i = INFO['timer_shorthand'].index(here)
        timer = INFO['timers'][i]
        guess_each = self(f'guess_cpu_seconds_{here}_per_each{safe}')
        each2timestep = self(f'cpu_per_each2{ct}')[timer]
        return guess_each * each2timestep

    @known_pattern(r'guess_cpu_seconds(|_unsafe)',
                   deps=['guess_cpu_seconds_sum_per_timestep_safe'])  # [TODO] deps based on group0
    def get_guess_cpu_seconds(self, var, *, _match=None):
        '''guess run cost, in cpu seconds. nt * guess_cpu_seconds_sum_per_timestep_safe
        Uses 'safe' guess (unless '_unsafe' included in name) but excludes initialization time.
            Might want to add a safety factor (e.g. assume 20% larger than this time).
        '''
        unsafe, = _match.groups()
        safe = '' if unsafe else '_safe'
        return self.input_deck['nt'] * self(f'guess_cpu_seconds_sum_per_timestep{safe}')

    @known_pattern(r'guess_runtime_seconds(|_unsafe)',
                   deps=['n_processors', {0: 'guess_cpu_seconds{group0}'}])
    def get_guess_runtime_seconds(self, var, *, _match=None):
        '''guess run cost, in wall clock time [seconds]. guess_cpu_seconds / n_processors.
        Uses 'safe' guess (unless '_unsafe' included in name) but excludes initialization time.
            Might want to add a safety factor (e.g. assume 20% larger than this time).

        Compare directly with self('steps_seconds').
        '''
        unsafe, = _match.groups()
        return self(f'guess_cpu_seconds{unsafe}') / self('n_processors')

    @known_pattern(r'guess_node_hours(|_unsafe)',
                   deps=['tasks_per_node', {0: 'guess_cpu_seconds{group0}'}])
    def get_guess_node_hours(self, var, *, _match=None):
        '''guess run cost, in node hours. guess_cpu_seconds * seconds2hours / tasks_per_node
        (seconds2hours = 1/3600)
        Uses 'safe' guess (unless '_unsafe' included in name) but excludes initialization time.
            Might want to add a safety factor (e.g. assume 20% larger than this time).
        '''
        unsafe, = _match.groups()
        seconds2hours = 1 / 3600
        return self(f'guess_cpu_seconds{unsafe}') * seconds2hours / self('tasks_per_node')
