"""
File Purpose: EppicSimInfoLoader
loading details about the simulation, not necessarily physics-based.
"""

import numpy as np
import xarray as xr

from .eppic_io_tools import n_mpi_processors
from ...errors import FluidKeyError, FileContentsMissingError
from ...quantities import QuantityLoader
from ...tools import (
    product,
    xarray_sum,
    slurm_options_here, slurm_option_here,
)

class EppicSimInfoLoader(QuantityLoader):
    '''simulation info for EppicCalculator.
    These are details about the simulation, not necessarily physics-based.
    E.g., number of particles per simulation cell, number of MPI processors used, simulation dx.

    (note that dx between cells in the output is actually dx_sim * nout_avg,
        since nout_avg is used to average over a few cells in space before providing the output.)
    '''

    # # # SLURM OPTIONS # # #

    @known_var
    def get_slurm_options(self):
        '''dataset of all slurm options from slurmfiles in self.dirname.
        crash if multiple slurmfiles in self.dirname with conflicting options.
        '''
        result = slurm_options_here(self.dirname)
        return xr.Dataset(result)

    @known_var(deps=['n_nodes', 'tasks_per_node'], aliases=['n_mpi_processors', 'n_mpi'])
    def get_n_processors(self):
        '''number of MPI processors used to run this run.
        From logfile if possible, else from slurm files.
        n_processors = n_nodes * tasks_per_node.
        '''
        try:
            result = n_mpi_processors(self.dirname)
        except (FileNotFoundError, AttributeError):
            result = self('n_nodes') * self('tasks_per_node')
        else:
            result = xr.DataArray(result)
        return result

    @known_var
    def get_n_nodes(self):
        '''number of nodes used to run this run. From slurm file.
        n_processors = n_nodes * tasks_per_node.
        '''
        # [TODO] support slurmfiles which specify n_processors instead of n_nodes.
        return xr.DataArray(slurm_option_here('--nodes', self.dirname))

    @known_var
    def get_tasks_per_node(self):
        '''number of processors per node. From slurm file.
        n_processors = n_nodes * tasks_per_node.
        '''
        slurm_options = slurm_options_here(self.dirname)
        if '--tasks-per-node' in slurm_options:
            result = xr.DataArray(slurm_options['--tasks-per-node'])
        elif '--total-tasks' in slurm_options and '--nodes' in slurm_options:
            result = slurm_options['--total-tasks'] // slurm_options['--nodes']
        else:
            errmsg = ('--tasks-per-node not found in slurm options,\n'
                      'and --total-tasks and --nodes not both present, either.')
            raise FileContentsMissingError(errmsg)
        return xr.DataArray(result)

    @known_var
    def get_time_requested(self):
        '''time limit for this run. From slurm file. Result is a string, like hh:mm:ss.
        For numeric results, see self('hours_requested'), minutes_requested, or seconds_requested.
        '''
        return xr.DataArray(slurm_option_here('--time', self.dirname))

    @known_pattern(r'(hours|minutes|mins|seconds)_requested', deps=['time_requested'])
    def get_time_requested_numeric(self, var, *, _match=None):
        '''time limit for this run, in hours, minutes, or seconds. From slurm file.
        Result is the total amount, e.g. '01:15:00' --> mins_requested=75.
        '''
        here, = _match.groups()
        time_str = self('time_requested', item=True)
        hours, minutes, seconds = [int(v) for v in time_str.split(':')]
        if here == 'hours':
            result = hours + minutes/60 + seconds/3600
        elif here in ('minutes', 'mins'):
            result = hours*60 + minutes + seconds/60
        elif here == 'seconds':
            result = hours*3600 + minutes*60 + seconds
        else:
            assert False, 'coding error if reached this line'
        return xr.DataArray(result)


    # # # EPPIC.I SIM INFO # # #

    @known_var
    def get_ndim_space(self):
        '''number of spatial dimensions in simulation. 2 or 3.'''
        return xr.DataArray(self.input_deck['ndim_space'])

    @known_var
    def get_nsubdomains(self):
        '''number of subdomains. nsubdomains from the input deck.
        Note: eppic runs require n_processors % nsubdomains == 0.
        '''
        return xr.DataArray(self.input_deck['nsubdomains'])

    @known_var(deps=['n_processors'])
    def get_npow2_processors(self):
        '''largest power of 2 which evenly divides n_processors.
        E.g. if n_processors = 56 * 8 == 7 * 4 * 8 == 7 * 2^5, result would be 2^5.
        '''
        n_processors = self('n_processors')
        largest_pow2_below = 2**(np.log2(n_processors).astype('int'))
        # (e.g. if n_processors = 7 * 2^5, largest_pow2_below == 2^2 * 2^5,
        #   because 2^2 < 7 but 2^3 > 7.)
        return np.gcd(n_processors, largest_pow2_below)

    @known_var(deps=['nsubdomains', 'tasks_per_node'])
    def get_min_n_nodes_given_nsubdomains(self):
        '''minimum number of nodes, given nsubdomains and tasks_per_node,
        to ensure n_processors % nsubdomains == 0,
            where n_processors = n_nodes * tasks_per_node.
        Equivalent: nsubdomains / gcd(nsubdomains, tasks_per_node)
        '''
        tasks_per_node = self('tasks_per_node')
        nsubdomains = self('nsubdomains')
        return nsubdomains // np.gcd(nsubdomains, tasks_per_node)

    @known_var
    def get_ncells_sim(self):
        '''number of gridcells from simulation (differs from output when nout_avg != 1).
        Scalar. E.g. Nx*Ny*Nz if 3D, Nx*Ny if 2D.
        '''
        nout_avg = self.input_deck['nout_avg']
        ncellsx = [self.input_deck.get_nspace(x)*nout_avg for x in self.maindims]
        return xr.DataArray(product(ncellsx))

    @known_var(load_across_dims=['component'])
    def get_ds_sim(self):
        '''grid spacing (of simulation). vector(ds), e.g. [dx, dy, dz]. Depends on self.component.
        ds_sim = (dx, dy, dz) from input deck (not divided by nout_avg)
        '''
        x = str(self.component)
        dx = self.input_deck[f'd{x}'] * self.u('length')
        return xr.DataArray(dx, attrs=dict(units=self.units))

    @known_var
    def get_dt_sim(self):
        '''time spacing (of simulation). Time between iterations (not between snapshots)'''
        return xr.DataArray(self.input_deck['dt'], attrs=dict(units=self.units))

    def npd_for_fluid(self, fluid):
        '''return the npd for this fluid.
        This is equivalent to fluid['npd'] when it is provided,
            otherwise determined by the appropriate alternative (npcelld, nptotd, or nptotcelld).
        This method is implemented for the calculator rather than the fluid, 
            because fluid doesn't know the possibly-required global values (ncells and/or n_processors).

        result will always be converted to int, since npd is an integer.
        '''
        key = None
        for key in ('npd', 'npcelld', 'nptotd', 'nptotcelld'):
            if key in fluid.keys():
                break
        else:  # didn't break
            raise FluidKeyError(f'fluid {fluid} does not have npd, npcelld, nptotd, or nptotcelld.')
        if key == 'npd':
            return int(fluid['npd'])
        elif key == 'npcelld':
            return int(fluid['npcelld'] * self('ncells_sim', item=True))
        elif key == 'nptotd':
            return int(fluid['nptotd'] / self('n_processors', item=True))
        elif key == 'nptotcelld':
            return int(fluid['nptotcelld'] * self('ncells_sim/n_processors', item=True))
        else:
            assert False, "coding error if reached this line"

    @known_var(load_across_dims=['fluid'])
    def get_npd(self):
        '''number of PIC particles in each distribution.
        This is equivalent to fluid['npd'] when it is provided,
            otherwise determined by the appropriate alternative (npcelld, nptotd, or nptotcelld).
        '''
        return xr.DataArray(self.npd_for_fluid(self.fluid))

    @known_var(deps=['npd', 'ncells_sim'])
    def get_npcelld(self):
        '''number of PIC particles per simulation cell.'''
        return self('npd') / self('ncells_sim')

    @known_var(deps=['npd', 'n_processors'])
    def get_nptotd(self):
        '''number of PIC particles (total across all processors).'''
        return self('npd') * self('n_processors')

    @known_var(deps=['npd', 'n_processors', 'ncells_sim'])
    def get_nptotcelld(self):
        '''number of PIC particles per simulation cell (total across all processors).'''
        return self('npd') * self('n_processors') / self('ncells_sim')

    @known_var(load_across_dims=['fluid'])
    def get_subcycle(self):
        '''subcycling factor (for each fluid in self.fluid).
        (If subcycle not provided for a distribution, assume it implies subcycle=1).
        '''
        return xr.DataArray(self.fluid.get('subcycle', 1))

    @known_var(deps=['nptotcelld', 'subcycle'], reduces_dims=['fluid'])
    def get_nptotcell(self):
        '''number of particles per cell for all fluids combined, appropriately weighted considering subcycling.
        Equivalent: sum_fluids_(nptotcelld/subcycle)
        '''
        with self.using(fluid=None):
            return xarray_sum(self('nptotcelld') / self('subcycle'), 'fluid', missing_dims='ignore')

    @known_var
    def get_nit_since_prev(self):
        '''return number of timesteps since previous snapshot in self.
        when determining previous snapshot, ignore any where snap.file_snap(self) is MISSING_SNAP.
        return inf when no previous snap, e.g. at snap=0.
        '''
        if not all(s.exists_for(self) for s in self.iter_snap()):
            return self('_nit_since_prev_simple')
        snap2i = {}
        for i, snap in enumerate(self.snaps):
            snap2i[id(snap)] = i
        result = []
        for i, snap in enumerate(self.iter_snap()):
            iprev = snap2i[id(snap)] - 1
            if iprev < 0:
                result.append(np.inf)
            else:
                it_here = int(snap.file_s(self))
                it_prev = int(self.snaps[iprev].file_s(self))
                result.append(it_here - it_prev)
        if self.snap_is_iterable():  # result is 1D
            return xr.DataArray(result, dims='snap', coords=dict(snap=self.snap))
        else:  # result is 0D
            return xr.DataArray(result, coords=dict(snap=self.snap))

    @known_var(load_across_dims=['snap'])
    def get__nit_since_prev_simple(self):
        '''naive implementation of nit_since_prev. Makes fewer assumptions, but can be slow.
        (e.g., took 0.8 seconds for 800 snaps. Compare to 0.02 seconds via nit_since_prev.)
        nit_since_prev should dispatch to this method if any of the assumptions fail.
        '''
        snap_here = self.snap  # this will be a single snap thanks to load_across_dims=['snap']
        if not snap_here.exists_for(self):
            return xr.DataArray(self.snap_dim.NAN)
        # get previous existing snap.
        snapi = int(self.snap) if self.snap==self.snaps[int(self.snap)] else self.snaps.index(self.snap)
        prev_snap_i = snapi - 1
        while prev_snap_i >= 0:
            prev_snap = self.snaps[prev_snap_i]
            if prev_snap.exists_for(self):
                break
            else:
                prev_snap_i -= 1
        else:  # didn't break; no previous snap found.
            return xr.DataArray(np.inf)
        # <-- at this point, prev_snap is the previous existing snap, and snap_here is the current snap.
        it_here = int(snap_here.file_s(self))
        it_prev = int(prev_snap.file_s(self))
        return xr.DataArray(it_here - it_prev)


    # # # CPU COST # # #
    @known_var(deps=['n_processors', 'timer2seconds', 'timers', 'nit_since_prev'])
    def get_cpu_seconds_per_timestep(self):
        '''cpu seconds per timestep, for each timer in timers.
        n_processors * timer2seconds * timers / nit_since_prev

        see also: cpu_seconds_per_ct, cpu_seconds_per_pct
        '''
        numer_coeff = self('n_processors') * self('timer2seconds')
        return (numer_coeff / self('nit_since_prev')) * self('timers')

    @known_var(deps=['cpu_seconds_per_timestep', 'ncells_sim'])
    def get_cpu_seconds_per_ct(self):
        '''cpu seconds per cell per timestep, for each timer in timers.
        n_processors * timer2seconds * timers / (ncells_sim * nit_since_prev)

        see also: cpu_seconds_per_timestep, cpu_seconds_per_pct
        '''
        return self('cpu_seconds_per_timestep') / self('ncells_sim')

    @known_var(deps=['nptotcell', 'cpu_seconds_per_ct'])
    def get_cpu_seconds_per_pct(self):
        '''cpu seconds per particle, per cell, per timestep, for each timer in timers.
        n_processors * timer2seconds * timers / (nptotcell * ncells_sim * nit_since_prev)
        (note, nptotcell accounts for subcycling. See self.help('nptotcell') for details.)

        see also: cpu_seconds_per_timestep, cpu_seconds_per_ct
        '''
        return self('cpu_seconds_per_ct') / self('nptotcell')

    @known_var(deps=['cpu_seconds_per_ct', 'nptotcell'])
    def get_cpu_seconds_per_each(self):
        '''cpu seconds per (particle, per) cell, per timestep, as relevant to each timer in timers.

        cpu_seconds_per_pct for definitely scaling with nptotcell:
            - vadv time
            - xadv time
            - charge
        cpu_seconds_per_pct for timers probably scaling with nptotcell:
            - output
        cpu_seconds_per_ct for timers definitely NOT scaling with nptotcell:
            - collect
            - efield
        
        EXCLUDE timers combining times above:
            - Wall Clock
            - Sys Clock
        EXCLUDE timers not handled here:
            - fluid
        '''
        per_ct = self('cpu_seconds_per_ct')
        result = per_ct.drop_vars(('Wall Clock', 'Sys Clock', 'fluid'))
        pct_vars = ['vadv time', 'xadv time', 'charge', 'output']
        return result.assign(per_ct[pct_vars] / self('nptotcell'))

    @known_var(deps=['nptotcell'])
    def get_cpu_per_each2ct(self):
        '''conversion factors: cpu_per_each2ct * cpu_per_each == cpu_per_ct.
        Result is a dataset with timers as data vars.
        These convert from (per particle per cell per timestep) to (per cell per timestep):
            'vadv time', 'xadv time', 'charge', 'output'.
            (I.e., for these timers: result == nptotcell)
        These do not convert at all:
            'collect', 'efield'
            (I.e., for these timers: result == 1)
        Other timers' conversions are not included.
        '''
        result = {}
        nptotcell = self('nptotcell')
        for timer in ['vadv time', 'xadv time', 'charge', 'output']:
            result[timer] = nptotcell
        for timer in ['collect', 'efield']:
            result[timer] = 1
        return xr.Dataset(result)

    @known_var(deps=['cpu_per_each2ct', 'ncells_sim'])
    def get_cpu_per_each2timestep(self):
        '''conversion factors: cpu_per_each2timestep * cpu_per_each == cpu_per_timestep.
        Result is a dataset with timers as data vars.
        These convert from (per particle per cell per timestep) to (per timestep):
            'vadv time', 'xadv time', 'charge', 'output'.
            (I.e., for these timers: result == nptotcell * ncells_sim)
        These convert from (per cell per timestep) to (per timestep):
            'collect', 'efield'
            (I.e. for these timers: result == ncells_sim)
        Other timers' conversions are not included.
        '''
        return self('cpu_per_each2ct') * self('ncells_sim')
