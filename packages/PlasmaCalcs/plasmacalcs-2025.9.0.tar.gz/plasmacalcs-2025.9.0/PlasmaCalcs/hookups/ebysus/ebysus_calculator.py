"""
File Purpose: EbysusCalculator
"""
import os

from .ebysus_bases import EbysusBasesLoader
from .ebysus_collisions import EbysusCollisionsLoader
from .ebysus_dimensions import EbysusFluidList
from .ebysus_efield import EbysusEfieldLoader
from .ebysus_temperatures import EbysusTemperaturesLoader
from ...dimensions import SnapList
from ...errors import LoadingNotImplementedError
from ...plasma_calculator import MultifluidPlasmaCalculator
from ...tools import alias, alias_child, simple_property
from ...defaults import DEFAULTS


class EbysusCalculator(EbysusBasesLoader, EbysusCollisionsLoader,
                       EbysusEfieldLoader, EbysusTemperaturesLoader,
                       MultifluidPlasmaCalculator):
    '''PlasmaCalculator for Ebysus.

    The idea is to use EbysusData (from helita.sim.ebysus) to read files.
        But hook everything up so that PlasmaCalcs does all the heavy-lifting.

    dd should be an EbysusData object.

    collisions_mode: str, default 'best'
        default mode for getting collision frequencies;
        'helita' --> get collision frequencies directly from helita.
        for more options/details, see help(type(self).collisions_mode).
    match_type: 'AUX', 'PHYSICS', 1, 0, or None
        1 or 'AUX' --> set dd.match_type = MATCH_AUX
        0 or 'PHYSICS' --> set dd.match_type = MATCH_PHYSICS
        None --> don't adjust dd.match_type.

    UNITS note: right now, units is fully managed by dd;
        self.u(conversion) will always be 1 (e.g. self.u('l') == self.u('m') == ... == 1);
        self.units == 'si' --> dd.units_output == 'si';
        self.units == 'raw' --> dd.units_output == 'simu'.
        [TODO] handle units via PlasmaCalcs instead of dd.
    '''
    quasineutral = True   # Ebysus is always quasineutral.

    def __init__(self, dd, *, collisions_mode='best', match_type='AUX', **kw_super):
        self.dd = dd
        self.collisions_mode = collisions_mode
        if match_type is not None:
            dd.match_type = {1: 1, 'AUX': 1, 0: 0, 'PHYSICS': 0}[match_type]
        self._setup_on_set_v_methods()
        snapsdict = self.get_init_snaps()
        fdict = self.get_init_fluids()
        kw = {**snapsdict, **fdict, **kw_super}
        kw['units'] = kw.get('units', dd.units_output)
        super().__init__(**kw)

    dirname = alias_child('dd', 'fdir')

    title = simple_property('_title', setdefaultvia='_default_title',
            doc='''title to help distinguish this calculator from others.
            E.g. might want to add self.title to plots. Default: os.path.basename(self.dirname).''')
    def _default_title(self):
        '''default title for self. Here, just returns os.path.basename(self.dirname)'''
        return os.path.basename(self.dirname)

    # # # UNITS SETUP # # #
    @property
    def units(self):
        '''units, but also set dd.units_output when setting.
        UNITS note: right now, units is fully managed by dd;
            self.u(conversion) will always be 1 (e.g. self.u('l') == self.u('m') == ... == 1);
            self.units == 'si' --> dd.units_output == 'si';
            self.units == 'raw' --> dd.units_output == 'simu'.
        '''
        return super().units
    @units.setter
    def units(self, value):
        if value == 'simu':
            value = 'raw'
        super(EbysusCalculator, type(self)).units.fset(self, value)
        self.dd.units_output = 'simu' if (value == 'raw') else value

    # # # DIMENSIONS SETUP -- MAINDIMS # # #
    maindims = ('x', 'y', 'z')

    def get_maindims_coords(self):
        '''return dict of {'x': xcoords, 'y': ycoords, 'z': zcoords}, in dd.units_output units.
        coords will be sliced according to self.slices.
        '''
        result = dict(x=self.dd.get_coord('x'),
                        y=self.dd.get_coord('y'),
                        z=self.dd.get_coord('z'))
        if self.flip_z_mesh:
            result['z'] = -result['z']
        return self._apply_maindims_slices_to_dict(result)

    cls_behavior_attrs.register('flip_z_mesh', default=False)
    flip_z_mesh = simple_property('_flip_z_mesh', default=False,
            doc='''whether to flip (multiply by -1) the z mesh coordinates relative to meshfile.
            When True, z<0 implies "below photosphere", for solar simulations.''')

    get_space_coords = alias('get_maindims_coords')

    def maindims_with_extent(self):
        '''return tuple of maindims with length > 1.
        ebysus output is all technically 3D but some dims might have length 1 for 2D simulation.
        It can be convenient to know which dims have extent / which do not.
        '''
        return tuple(x for x in self.maindims if getattr(self.dd, f'n{x}') > 1)

    def maindims_with_no_extent(self):
        '''return tuple of maindims with length == 1.
        ebysus output is all technically 3D but some dims might have length 1 for 2D simulation.
        It can be convenient to know which dims have extent / which do not.
        '''
        return tuple(x for x in self.maindims if getattr(self.dd, f'n{x}') == 1)

    # # # DIMENSIONS SETUP -- OTHERS # # #
    def match_dd_dims(self):
        '''matches self.snap, fluid, and jfluid to self.dd.snap, ifluid, and jfluid.'''
        dd = self.dd
        try:
            snaps = dd.snaps
        except TypeError:  # dd.snap is a single snapshot
            self.snap = str(dd.snap)
        else:  # dd.snap is multiple snapshots
            self.snap = [str(snap) for snap in snaps]
        self.fluid = dd.get_fluid_name(dd.ifluid)
        self.jfluid = dd.get_fluid_name(dd.jfluid)

    def get_init_snaps(self):
        '''return dict of snaps, snap for setting self.snaps & self.snap.'''
        dd = self.dd
        with dd.maintaining('snap'):  # restore dd.snap afterwards
            dd[:]  # sets dd.snap to dd.get_snaps()
            snaps = [str(snap) for snap in dd.snaps]
            times_raw = dd.get_coord('t', 'simu')
        snaplist = SnapList.from_lists(s=snaps, t=times_raw)
        return dict(snaps=snaplist, snap=0)

    def get_init_fluids(self):
        '''return dict of fluids, fluid, jfluids, jfluid for setting those attrs of self.'''
        dd = self.dd
        fluids = dd.fluids
        names = fluids.name
        masses = fluids.atomic_weight  # [amu]
        charges = fluids.ionization   # [elementary charge units]
        SLs = fluids.SL
        electrons = dict(name='e', m= dd.get_mass((-1,0), units='amu'), q= -1, SL=(-1,0))
        others = [dict(name=name_, m=m_, q=q_, SL=SL_) for name_, m_, q_, SL_ in zip(names, masses, charges, SLs)]
        fluidlist = EbysusFluidList.from_dicts([electrons] + others)
        return dict(fluids=fluidlist, fluid=dd.get_fluid_name(dd.ifluid),
                    jfluids=fluidlist, jfluid=dd.get_fluid_name(dd.jfluid))

    def _setup_on_set_v_methods(self):
        '''sets up methods so that when dims in self are set, appropriate dims in self.dd are set too.
        E.g., when setting self.fluid, set self.dd.fluid too, if self.fluid_is_iterable().
        '''
        self._setup_on_set_snap()
        self._setup_on_set_fluid()
        self._setup_on_set_jfluid()

    def _setup_on_set_snap(self):
        '''sets self.snap_dim.on_set_v = method which also sets dd.snap.'''
        def on_set_snap(value):
            '''when setting snap, also set dd.snap.'''
            try:
                snap_s = self.snap.file_s(self)
                # ^^ file_s == "the str used to get file for this snap & calculator"
                # ^^ or, if snap is a SnapList, it should be an array of file_s for each snap in the list.
            except AttributeError:
                if DEFAULTS.DEBUG > 3:
                    raise
                return   # don't know what to set snap to...
            if isinstance(snap_s, str):
                self.dd.snap = int(snap_s)
            else:  # snap_s is a list of file_s values
                self.dd.snap = [int(s) for s in snap_s]
        self.snap_dim.on_set_v = on_set_snap

    def _setup_on_set_fluid(self):
        '''sets self.fluid_dim.on_set_v = method which sets dd.ifluid if setting fluid to single value.'''
        def on_set_fluid(value):
            '''when setting fluid, also set dd.ifluid, if not fluid_is_iterable().'''
            if not self.fluid_is_iterable():
                self.dd.ifluid = self.fluid.SL
        self.fluid_dim.on_set_v = on_set_fluid

    def _setup_on_set_jfluid(self):
        '''sets self.jfluid_dim.on_set_v = method which sets dd.jfluid if setting jfluid to single value.'''
        def on_set_jfluid(value):
            '''when setting jfluid, also set dd.jfluid, if not jfluid_is_iterable().'''
            if not self.jfluid_is_iterable():
                self.dd.jfluid = self.jfluid.SL
        self.jfluid_dim.on_set_v = on_set_jfluid

    # # # LOADING VARS # # #
    def _var_dimmed(self, ebysus_var):
        '''return ebysus_var, possibly slightly adjusted based on currently-loading dimension(s).
        Here:
            append component AND 'c' if self._loading_component
        E.g. 'b' turns into 'bzc' when loading 'z' component.
        '''
        result = ebysus_var
        if getattr(self, '_loading_component', False):
            result = result + str(self.component) + 'c'
        return result

    def load_direct(self, var, *args, **kw):
        '''load var "directly", either from a file or from self.direct_overrides.
        first, add dimensions to var if appropriate, based on the currently-loading dimension(s).
            E.g. 'b' turns into 'bzc' when loading 'z' component.
        If there is is an override for that var, use it; otherwise load from file.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        ebysus_var = self._var_dimmed(var)
        return super().load_direct(ebysus_var, *args, **kw)

    def load_fromfile(self, ebysus_var, *args, **kw):
        '''load ebysus_var directly from self.dd.

        ebysus_var: str
            the name of the variable to read. Should include all dimensions as appropriate.
            E.g., use 'bzc', not 'b', to get magnetic field z component.

        End-user should not need to worry about this function;
            it's mainly here for connecting the ebysus base vars for PlasmaCalcs appropriately.
        '''
        try:
            return self.dd(ebysus_var, *args, **kw)
        except ValueError as err:
            raise LoadingNotImplementedError(f'{type(self).__name__}.load_fromfile({ebysus_var!r})') from err

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return list of strings to use inside self.__repr__'''
        contents = super()._repr_contents()
        contents = [f'dirname={self.dirname!r}'] + list(contents)
        return contents
