"""
File Purpose: EppicCalculator
"""

import numpy as np
import xarray as xr

from .eppic_addon_quantity_loader import EppicAddonQuantityLoader
from .eppic_bases import EppicBasesLoader
from .eppic_choose_params import EppicChooseParams, EppicTimescales
from .eppic_input_deck import EppicInputDeck
from .eppic_direct_loader import EppicDirectLoader
from .eppic_io_tools import read_eppic_snaps_info
from .eppic_moments import EppicMomentsLoader
from .eppic_plotters import EppicPlotterManager
from .eppic_runtime_info import EppicRuntimeInfoLoader
from .eppic_sim_info import EppicSimInfoLoader
from .eppic_subsampler import EppicSubsamplable
from ...dimensions import SnapList, INPUT_SNAP
from ...errors import DimensionError, FluidValueError, InputConflictError, InputError
from ...plasma_calculator import MultifluidPlasmaCalculator
from ...tools import (
    alias, alias_child,
    UNSET,
)
from ...defaults import DEFAULTS

class EppicCalculator(EppicBasesLoader,
                      EppicMomentsLoader, EppicRuntimeInfoLoader, EppicSimInfoLoader,
                      EppicSubsamplable, EppicDirectLoader,
                      EppicPlotterManager,
                      EppicAddonQuantityLoader,
                      MultifluidPlasmaCalculator):
    '''PlasmaCalculator for Eppic outputs.
    To initialize from an eppic.i file, use EppicCalculator.from_here().
    
    Use EppicCalculator.help() for more help.

    input_deck: EppicInputDeck
        the EppicInputDeck which is being used by this calculator.
    snaps_from: 'parallel' or 'timers'
        how to determine existing snaps.
        'parallel' --> from files in directory 'parallel' (located adjacent to 'eppic.i')
        'timers' --> from data in 'domain000/timers.dat' ('domain000' adjacent to 'eppic.i')
    u: None or UnitsManager
        if provided, set self.u = u, and ignore u_l, u_t, u_n, and ne_si.
    u_l, u_t, u_n, ne_si: None or value
        must provide one of these values in order to fully determine the units.
        u_l: length [si] = u_l * length [raw]
        u_t: time [si] = u_t * time [raw]
        u_n: number density [si] = u_n * number density [raw]
        ne_si: electron number density [si]. (ne [raw] will be loaded from input_deck)
    kw_units: dict
        any additional values used to determine the units.
        can also provide u_l, u_t, u_n, or ne_si, here, instead of as direct kwarg.
        See help(UnitsManagerPIC.from_pic) for more details.
    quasineutral: None or bool
        if provided, set self.quasineutral.
        otherwise, infer it from self.input_deck.is_quasineutral().
        in quasineutral mode, distribution 0 is assumed to be electrons,
            and different routines are used to calculate its density & other parameters.
    _more_init_checks: bool, default False
        if True, perform additional checks during initialization.
        False by default for slight efficiency improvement,
            and to avoid possibility of init checks failing but object still being usable.

    other kwargs are passed to super().__init__.
    '''
    # # # DEFAULTS # # #
    _quasineutral = False

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, input_deck, *, snaps_from='parallel',
                 u=None, u_l=None, u_t=None, u_n=None, ne_si=None, kw_units=dict(),
                 quasineutral=None,
                 _more_init_checks=False,
                 **kw_super):
        self.input_deck = input_deck
        kwu = kw_units.copy()
        self.init_units_manager(u=u, u_l=kwu.pop('u_l', u_l), u_t=kwu.pop('u_t', u_t),
                                u_n=kwu.pop('u_n', u_n), ne_si=kwu.pop('ne_si', ne_si), **kwu)
        self.init_maindims()
        self.init_fluids()
        kw_super.setdefault('jfluid', 0)  # if jfluid not provided, use jfluid=0.
        self.init_snaps(snaps_from=snaps_from)
        if quasineutral is None: quasineutral = self.input_deck.is_quasineutral()
        super().__init__(input_deck, quasineutral=quasineutral, **kw_super)
        if _more_init_checks:
            self._check_files_readable()

    @classmethod
    def from_here(cls, filename='eppic.i', *, dist_names=None, **kw):
        '''create EppicCalculator from input deck file found here (at filename).
        dist_names: None or dict
            {N: name for distribution N} for any number of distributions in filename.
            E.g.: {0: 'e', 1: 'H+', 2: 'C+'}
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return cls(EppicInputDeck.from_file(filename, dist_names=dist_names), **kw)

    # # # INFO # # #
    dirname = alias_child('input_deck', 'dirname')
    filename = alias_child('input_deck', 'filename')

    # # # UNITS # # #
    def init_units_manager(self, *, u=None, u_l=None, u_t=None, u_n=None, ne_si=None, **kw_get_units_manager):
        '''set units manager self.u, based on input_deck.
        must provide one of these values in order to fully determine the units.
            u: UnitsManager object. if provided, set self.u = u.
            u_l: length [si] = u_l * length [raw]
            u_t: time [si] = u_t * time [raw]
            u_n: number density [si] = u_n * number density [raw]
            ne_si: electron number density [si]. (ne [raw] will be loaded from input_deck)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if u is None:
            u = self.input_deck.get_units_manager(u_l=u_l, u_t=u_t, u_n=u_n, ne_si=ne_si, **kw_get_units_manager)
        self.u = u

    # # # DIMENSIONS SETUP -- MAINDIMS # # #
    def init_maindims(self):
        '''set self.maindims based on input_deck.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.maindims = self.input_deck.maindims()

    def get_maindims_coords(self, units=None):
        '''return dict of {'x': xcoords, 'y': ycoords}. Possibly also 'z': zcoords.
        units: None or str
            result will be in this unit system. if None, use self.coords_units (default: self.units).
        coords will be subsampled appropriately if subsampling_info exists.
        coords will also be sliced according to self.slices.
        '''
        result = self.input_deck.get_space_coords()
        u_l = self.u('l', self.coords_units_explicit if units is None else units)
        result = {key: u_l * value for key, value in result.items()}
        result = self._apply_subsampling_to_maindims_coords(result)
        return self._apply_maindims_slices_to_dict(result)

    get_space_coords = alias('get_maindims_coords')

    # # # DIMENSIONS SETUP -- OTHERS # # #
    def init_snaps(self, *, snaps_from='parallel'):
        '''set self.snaps based on input_deck AND reading files.
        snaps_from: 'parallel' or 'timers'
            how to determine existing snaps.
            'parallel' --> from files in directory 'parallel' (located adjacent to 'eppic.i')
            'timers' --> from data in 'domain000/timers.dat' ('domain000' adjacent to 'eppic.i')
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self._snaps_from = snaps_from
        dt = self.input_deck["dt"]
        dir_ = self.input_deck.dirname
        names, times = read_eppic_snaps_info(dir_, read_mode=self.input_deck["hdf_output_arrays"], dt=dt, snaps_from=snaps_from)
        self.snaps = SnapList.from_lists(s=names, t=times)

    @property
    def snaps_from(self):
        '''how existing self.snaps were determined. Probably 'parallel' or 'timers'.
        'parallel' --> from files in directory 'parallel' (located adjacent to 'eppic.i')
        'timers' --> from data in 'domain000/timers.dat' ('domain000' adjacent to 'eppic.i')

        setting self.snaps_from=value is equivalent to calling self.init_snaps(snaps_from=value).
        '''
        return self._snaps_from
    @snaps_from.setter
    def snaps_from(self, value):
        self.init_snaps(snaps_from=value)

    def init_fluids(self):
        '''set self.fluids and self.jfluids based on input_deck.'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.fluids = self.input_deck.dists
        self.jfluids = self.input_deck.neutrals

    # [TODO][MV] should this method go somewhere else?
    def assign_velocity_coords(self, array, fluid=UNSET):
        '''assign velocity dims and coords, based on fluid.get_velocity_coords().
        E.g., for "vdist" data. Array shape and coords inferred from input deck.
        (If subsampling_info exists, that will also be applied appropriately.)
        returns an xarray with proper details for PlasmaCalcs. Output units according to self.units.

        This is not like the assign_{dim}_coord functions, which assign 0D coord to an existing xarray;
        this method creates a *new* xarray based on array, and velocity dims & coords are >0 dimensional.

        array: 3D array
            probably the "vdist" data, e.g. directly from reading output data from one snapshot.
        fluid: UNSET, int, str, Fluid, or other way to specify a single fluid.
            UNSET --> use self.fluid.
            else --> temporarily set self.fluid = fluid, during this operation.
        '''
        if np.ndim(array) != 3:
            raise DimensionError(f'array must be 3D, but got ndim={np.ndim(array)}')
        if fluid is UNSET:
            fluid = self.fluid
        with self.using(fluid=fluid):
            if self.current_n_fluid() != 1:
                raise FluidValueError(f'assign_velocity_coords expects 1 fluid, got {self.current_n_fluid()}')
            fluid = self.fluid_list()[0]  # convert to "definitely a single fluid, not a list of length 1"
            vcoords = fluid.get_velocity_coords(units=self.u('speed'))
            vcoords = self._apply_subsampling_to_vdist_coords(vcoords, fluid)
        result = xr.DataArray(array, coords=vcoords, dims=('vx', 'vy', 'vz'))
        return result

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return list of strings to use inside self.__repr__'''
        contents = super()._repr_contents()
        contents = [f'input_deck={self.input_deck!r}'] + list(contents)
        return contents

    # # # MANIPULATING / DIRECTLY USING INPUT DECK # # #
    def set_vars_from_inputs(self, snap=INPUT_SNAP, *, _version='new', **kw):
        '''set self.snap to INPUT_SNAP. self will automatically load eppic.i values when snap=INPUT_SNAP.

        (This function was useful before load_input() was implemented (on 2025-04-25),
            but now that load_input() exists, there's probably not a compelling reason to keep this around...
            However, we will keep it around for a while, in case someone was using it.
            It *should* also be *mostly* backwards compatible, as setting self.snap = INPUT_SNAP
                will now produce equivalent result as the old version would have produced,
                except the new version doesn't touch self.setvars in order to do it.

        snap: INPUT_SNAP or any snap specifier
            sets self.snap = snap, and sets values at this snap. (doesn't restore old self.snap after.)
            INPUT_SNAP --> special value; refers to "snap from input deck, not a real snap".
            You can later access the set values by using self.snap = PlasmaCalcs.INPUT_SNAP
            if _version=='new', snap MUST be INPUT_SNAP, else will crash with InputConflictError
        _version: 'new' or 'old'
            if 'new', just set self.snap = INPUT_SNAP.
            if 'old', set self.snap=snap, then use self.set_bases() to adjust self.setvars appropriately.

        kw are passed as self.using(**kw) while using this method.
        '''
        if _version == 'new':
            if snap != INPUT_SNAP:
                raise InputConflictError(f'if _version="new", snap must be INPUT_SNAP, but got {snap!r}')
            self.snap = INPUT_SNAP
        elif _version == 'old':
            self.snap = snap
            with self.using(**kw, units='raw'):  # input deck uses 'raw' units. setvars handles units later.
                # fluid-specific
                for fluid in self.iter_fluids():
                    n = fluid.get_n0()
                    vx, vy, vz = fluid.get_v0()
                    try:
                        vtherm = fluid.get_vth0(x=...)
                    except AssertionError:
                        raise NotImplementedError('set_vars_from_inputs for non-isotropic vtherm')
                    self.set_bases(n=n, vx=vx, vy=vy, vz=vz)
                    self.set('vtherm', vtherm)
                # global
                self.set('phi', 0)  # use phi=0 for initial timestep (getting E will give E_ext.)
        else:
            raise InputError(f'unknown _version={_version!r}. Must be "new" or "old".')

    def choose_params(self, **kw_init):
        '''returns EppicChooseParams based on self.

        Common usage:
            # write a new eppic.i file based on the eppic.i file in self.dirname,
            # and using the current values of params from self.
            self.choose_params().write(dst='eppic_updated.i')

        uses self.dirname and self.get_vals_for_inputs().

        kwargs go to EppicChooseParams.__init__
        '''
        return EppicChooseParams(self, **kw_init)

    def timescales(self, **kw_init):
        '''returns EppicTimescales based on self.
        CAUTION: result will have units of self.units;
            remember to switch to 'raw' when comparing to input_deck.
        '''
        return EppicTimescales(self, **kw_init)

