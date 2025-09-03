"""
File Purpose: base quantities for EppicCalculator
"""
import re

import numpy as np
import xarray as xr

from .eppic_input_deck import EppicNeutral, EppicNeutralList
from ...dimensions import INPUT_SNAP
from ...errors import (
    InputConflictError, FluidValueError, DimensionAttributeError,
    FormulaMissingError, LoadingNotImplementedError,
)
from ...quantities import AllBasesLoader, SimpleDerivedLoader
from ...tools import UNSET, is_iterable_dim, simple_property


class EppicBasesLoader(AllBasesLoader, SimpleDerivedLoader):
    '''base quantities based on Eppic output.'''

    # # # BASE_QUANTS directly from eppic # # #

    @known_var(load_across_dims=['fluid'])
    def get_m(self):
        '''mass, of a "single particle". For protons, ~= +1 atomic mass unit'''
        return xr.DataArray(self.fluid.m * self.u('M'), attrs=self.units_meta())

    @known_var(load_across_dims=['fluid'])
    def get_q(self):
        '''charge, of a "single particle". For protons, == +1 elementary charge'''
        return xr.DataArray(self.fluid.q * self.u('q'), attrs=self.units_meta())

    @known_var(load_across_dims=['fluid'])
    def get_nusn(self):
        '''collision frequency (of self.fluid) with neutrals.
        "frequency for one particle of species s (self.fluid) to collide with any of the neutrals."
        [TODO] how does this compare with simulated collisions in PIC?
        '''
        return xr.DataArray(self.fluid['coll_rate'] * self.u('Hz'), attrs=self.units_meta())

    @known_var(load_across_dims=['component'], aliases=['dspace'])
    def get_ds(self):
        '''grid spacing (of output files). vector(ds), e.g. [dx, dy, dz]. Depends on self.component.
        ds = (ds_sim / nout_avg) * subsampling_step. subsampling_step=1 unless subsampling_info exists.
        '''
        x = str(self.component)
        dx_raw = self.input_deck.get_dspace(x) * self._get_subsampling_step(x)
        dx = dx_raw * self.u('length')
        return xr.DataArray(dx, attrs=self.units_meta())

    @known_var(deps=['ds_sim'], ignores_dims=['component'])
    def get_ds_for_timescales(self):
        '''ds used when calculating timescales. vector(ds), e.g. [dx, dy, dz].
        Like ds_sim, the value here doesn't include the nout_avg factor.

        ds_for_timescales equals ds_sim for components corresponding to self.input_deck.maindims()
            (regarless of current value of self.component).
        '''
        return self('ds_sim', component=self.input_deck.maindims())

    # # # loading directly from eppic # # #

    @known_var(dims=['snap', 'fluid'], aliases=['den'])
    def get_deltafrac_n(self):
        '''normalized density perturbation. (directly from Eppic.) deltafrac_n = (n - n0) / n0.'''
        return self.load_maindims_var_across_dims('den', dims=['snap', 'fluid'])  # [dimensionless]

    @known_var(load_across_dims=['fluid'])
    def get_n0(self):
        '''background density. (directly from Eppic.)
        note: as with all other quantities, this will be output in [self.units] unit system;
            numerically equal to eppic.i value if using 'raw' units.
        '''
        try:
            n0 = self.fluid.n0
        except AttributeError:
            errmsg = f'{type(self.fluid).__name__} object has no attribute "n0".'
            raise DimensionAttributeError(errmsg) from None
        return xr.DataArray(n0 * self.u('n'), attrs=self.units_meta())

    @known_var(dims=['snap', 'fluid', 'component'])
    def get_flux(self):
        '''flux. (directly from Eppic)'''
        return self.load_maindims_var_across_dims('flux', u='flux', dims=['snap', 'fluid', 'component'])

    @known_var(dims=['snap', 'fluid', 'component'])
    def get_nvsqr(self):
        '''n * ({x} component of velocity)^2. (directly from Eppic)'''
        return self.load_maindims_var_across_dims('nvsqr', u='n u2', dims=['snap', 'fluid', 'component'])

    @known_var(dims=['snap'])
    def get_phi(self):
        '''electric potential. (directly from Eppic)'''
        return self.load_maindims_var_across_dims('phi', u='E length', dims=['snap'])

    @known_var(load_across_dims=['component'])
    def get_E_ext(self):
        '''external electric field. (directly from Eppic).'''
        x = str(self.component)
        Ex = self.input_deck.get(f'E{x}0_external', 0) * self.u('E')
        return xr.DataArray(Ex, attrs=self.units_meta())

    @known_var(dims=['snap', 'fluid'])
    def get_vdist(self):
        '''velocity distribution. (directly from Eppic)'''
        if self.current_n_fluid() != 1:
            raise FluidValueError("get_vdist doesn't work with multiple fluids. Maybe you forgot to choose your fluid?")
        return self.load_across_dims(self._vdist_loader, dims=['snap', 'fluid'])

    def _vdist_loader(self):
        '''load vdist. Helper function for self.get_vdist.'''
        result = self.load_direct("vdist")
        if self._load_direct_used_override is not None:  # got var from an override, not the file.
            return result
        # else, got result directly from a file.
        result_length = len(result)
        target_length = self.fluid["pnvx"]
        if result_length > target_length: # FOR OLD VERSION OF EPPIC WITH PHDF OUTPUT_VDIST BUG
            result = np.sum(np.split(result, result_length//target_length), axis=0)
        result = self.assign_velocity_coords(result)
        return self.record_units(result)

    @known_var(load_across_dims=['component'])
    def get_B(self):
        '''magnetic field. (directly from Eppic)'''
        x = str(self.component)
        Bx = self.input_deck.get(f'B{x}', 0) * self.u('b')
        return xr.DataArray(Bx, attrs=self.units_meta())


    # # # INPUT_SNAP CASE # # #
    # (load_direct() redirects to here when self.snap is INPUT_SNAP)
    def load_input(self, fromfile_var, *args__None, **kw__None):
        '''load input value -- one of the base quantities (fromfile_var) directly from eppic.i file.
        Results are always in 'raw' units.
        E.g., self('den', fluid=0) internally uses self.load_input('den0') for INPUT_SNAP,
            and self.load_fromfile('den0') for all other snaps.

        Possible fromfile_vars are:
            'phi': electric potential, excluding any imposed E_ext.
                Always 0. (== "perturbation" to E_ext, implied by eppic.i file)
            'den{N}': density of dist N.
                Always 0. (== "perturbation" to n, implied by eppic.i file)
            'flux{x}{N}': flux of dist N in x direction.
                fN.get_n0() * fN.get_v0(x), where fN = self.fluids.get(N).
            'nvsqr{x}{N}': n * (v_x^2) of dist N in x direction.
                fN.get_nvsqr0(x), where fN = self.fluids.get(N).
                == fN.get_n0() * (fN.get_v0(x)**2 + fN.get_vth0(x)**2)
        '''
        pattern = r'(phi|den(\d+)|flux([xyz])(\d+)|nvsqr([xyz])(\d+))'
        match = re.fullmatch(pattern, fromfile_var)
        if match is None:
            errmsg = (f'fromfile_var={fromfile_var!r} not recognized. '
                      'Expected var like: phi, den{N}, flux{x}{N}, or nvsqr{x}{N}.')
            raise LoadingNotImplementedError(errmsg)
        var = match.groups()[0]
        if var == 'phi':
            result = 0.0
        elif var.startswith('den'):
            result = 0.0
        elif var.startswith('flux'):
            x, N = re.fullmatch(r'flux([xyz])(\d+)', var).groups()
            fN = self.fluids.get(int(N))
            result = fN.get_n0() * fN.get_v0(x)
        elif var.startswith('nvsqr'):
            x, N = re.fullmatch(r'nvsqr([xyz])(\d+)', var).groups()
            fN = self.fluids.get(int(N))
            result = fN.get_nvsqr0(x)
        else:
            assert False, 'coding error if reached this line'
        return xr.DataArray(result)  # in [raw] units.

    @known_pattern(r'frominputs_(.+)', deps=[0])
    def get_frominputs_value(self, var, *, _match=None):
        '''compute var based on inputs, i.e. when self.snap = INPUT_SNAP.
        result drops 'snap' coord, if it exists.

        self('frominputs_var') is equivalent to:
        with self.using(snap=INPUT_SNAP):
            return self('var').drop_vars('snap', errors='ignore')
        '''
        here, = _match.groups()
        with self.using(snap=INPUT_SNAP):
            result = self(here)
        return result.drop_vars('snap', errors='ignore')


    # # # QUASINEUTRAL CASE # # #
    # (this belongs in eppic hookup, not quasineutral.py, because it depends on eppic.)

    def _qn_direct_den0(self):
        '''gets den0 in quasineutral case.'''
        self.assert_QN()
        return self('deltafrac_ne')
        # note - 'get_deltafrac' rule is in StatsLoader; 'get_ne' rule is in QuasineutralLoader.

    def direct_overrides_dynamic(self):
        '''returns dict of {var: override} for all overrides of self which depend on behavior_attrs of self.'''
        result = super().direct_overrides_dynamic()
        if self.quasineutral:
            result.update({'den0': type(self)._qn_direct_den0})
        return result
    

    # # # HELPER QUANTS derived from eppic values # # #

    @known_var(deps=['n', 'nvsqr'])
    def get_vsqr(self):
        '''v^2 in each grid cell. components given by: v_x^2 = nvsqr_x / n.'''
        return self('nvsqr') / self('n')

    @known_pattern(r'Ta(joule)?(_global)?',
                   deps=['m', 'vsqr', {1: lambda groups: 'nmean_u' if groups[1] else 'u'}])
    def get_Ta_or_Tajoule(self, var, *, _match=None):
        '''temperature ("anisotropic").
        'Ta'      --> (m * (vsqr - u^2) / kB) [Kelvin]
        'Tajoule' --> (m * (vsqr - u^2))      [energy units]
        'Ta_global' or 'Tajoule_global'
            --> use nmean_u instead of u. nmean_u is the density-weighted mean velocity,
                i.e. it is the mean velocity across all particles in the box
                (which is not necessarily equivalent to mean across all cells in the box).
                Note that if reading u directly from simulation, nmean_u should be equal to moment1.
        components given by:
            Ta_x      = m * (vsqr_x - u_x^2) / kB
            Tajoule_x = m * (vsqr_x - u_x^2)

        There are 3 different quantities to consider, related to averaging:
            - Ta_from_moment2_x: single value, temperature if the entire box is one distribution;
                    this is probably what observations would see if they can't resolve the box.
                    Equal to x component of m * <(v - <v>)^2>, where <*> indicates mean across all particles.
                    This equals m * (<v^2> - 2<v*<v>> + <v>^2) = m * (<v^2> - <v>^2).
                    Note: <v^2> == nmean_vsqr, because nmean is equivalent to "mean across particles".
            - Ta_global_x: one value per grid cell. Not defined as a "temperature",
                    instead, defined as the quantity whose nmean is equivalent to Ta_from_moment2.
                    Ta_global_x = m * (vsqr - <v>^2) == m * (vsqr - nmean_u^2).
            - Ta_x: one value per grid cell. Temperature for that grid cell;
                    this is probably what observations would see if they could resolve the grid cells.
                    Ta_x = m * (vsqr - u^2), where u is the average of particle velocities in that cell, only.
                    Because Ta_x doesn't use global nmean_u, nmean_Ta_x is NOT equivalent to Ta_from_moment2_x.
        '''
        here, global_ = _match.groups()
        # note: nmean_u should equal moment1, but might be different if used self.set_var to set u or n;
        # that is why 'nmean_u' is used here instead of 'moment1'.
        u = self('nmean_u') if global_ else self('u')
        result = self('m') * (self('vsqr') - u**2)
        if here != 'joule':  # Ta, not Tajoule
            result = result / self.u('kB')
        return result

    @known_var(deps=['grad_phi'])
    def get_E_phi(self):
        '''electric field, from phi. E_phi = -grad(phi). Doesn't include E_ext component.'''
        return -self('grad_phi')


    # # # BASE_QUANTS derived from eppic values # # #

    @known_var(deps=['n0', 'deltafrac_n'])
    def get_n(self):
        '''number density. n = n0 * (1 + deltafrac_n)'''
        # [TODO][EFF] implement ne separately, if quasineutral.
        #   presently, implementation will work but get_n gets deltafrac_ne from ne,
        #       (since deltafrac_ne is treated as the "directly-loaded" var)
        #       then gets ne from deltafrac_ne.
        #   Fixing this is probably a very low priority,
        #       mostly because doing it cleanly involves altering some of the dimension tools,
        #       but here's a note about it in case we have time.
        if self._fluid_is_neutral():
            return self._get_n_neutral()
        n0 = self('n0')
        dfn = self('deltafrac_n')
        return n0 * (1 + dfn)

    @known_var(deps=['flux', 'n'])
    def get_u(self):
        '''velocity. u = flux / n'''
        if self._fluid_is_neutral():
            return self('u_neutral')  # always 0 in every component, for EPPIC.
        return self('flux') / self('n')

    cls_behavior_attrs.register('T_indim_only', default=False)
    T_indim_only = simple_property('_T_indim_only', default=False,
        doc='''whether to consider only components in maindims when getting T from Ta.
        Irrelevant in 3D; 3D always has self('T') == sqrt((1/3)*(Ta_x^2 + Ta_y^2 + Ta_z^2)).
        In 2D x-y sim, True --> self('T') == self('T_indim') == sqrt((1/2)*(Ta_x^2 + Ta_y^2)).
            2D & False --> self('T') = same formula as in 3D sim.''')

    @known_var(attr_deps=[('T_indim_only', {True: 'T_indim', False: 'rmscomps_Ta'})])
    def get_T(self):
        '''temperature, from nv^2. Rms average of all (3) anisotropic temperature components.
        T == sqrt((Ta_x^2 + Ta_y^2 + Ta_z^2)/3)

        if self.T_indim_only, instead return self('T_indim'), which ignores Tz if data is 2D.
        '''
        if self.T_indim_only:
            return self('T_indim')
        if self._fluid_is_neutral():
            return self._get_T_neutral()
        return self('rmscomps_Ta', component=None)

    @known_var(deps=['rmscomps_Ta'])
    def get_T_indim(self):
        '''temperature, from nv^2. Rms average of Ta components in self.maindims.
        Equivalent to self('T') in 3D, but in 2D xy data, T_indim ignores Tz.
        '''
        if self._fluid_is_neutral():
            return self._get_T_neutral()
        return self('rmscomps_Ta', component=self.maindims)

    @known_var(deps=['E_ext', 'E_phi'])
    def get_E(self):
        '''electric field. E = E_external + E_phi = E_external - grad(phi)'''
        E_ext = self('E_ext')
        E_phi = self('E_phi')
        return E_ext + E_phi


    # # # HANDLING NEUTRALS # # #

    def _fluid_is_neutral(self):
        '''returns True if self.fluid is neutral (either one neutral or multiple).
        True if self.fluid is an EppicNeutral, or iterable with only EppicNeutrals.
        '''
        f = self.fluid
        if isinstance(f, (EppicNeutral, EppicNeutralList)):
            return True
        # included EppicNeutralList check above, for efficiency.
        # (code below would also work for EppicNeutralList, but it's slower)
        # now, need to check if fluid is iterable and all are neutrals
        #  (e.g. if fluid is a list (but not FluidList) of only neutrals)
        if self.fluid_is_iterable() and all(isinstance(f_, EppicNeutral) for f_ in f):
            return True
        return False

    @known_var(aliases=['u_n'])
    def get_u_neutral(self):
        '''returns 0, since u_neutral is always 0 in every component, for eppic.'''
        return self('vector_0')

    @known_var(load_across_dims=['fluid'], aliases=['m_n_f'])
    def get_m_neutral_f(self):
        '''mass, of a "single neutral particle," varying across fluid. For Hydrogen, ~= +1 atomic mass unit'''
        if "massd_neutral" in self.fluid.params:
            return xr.DataArray(self.fluid['massd_neutral'] * self.u('M'), attrs=self.units_meta())
        else:
            return self.get_neutral('m')
    
    @known_var(aliases=['m_n'])
    def get_m_neutral(self):
        '''mass, of a "single neutral particle". For Hydrogen, ~= +1 atomic mass unit'''
        for fluid in self.fluid_list():
            if "massd_neutral" in fluid.params:
                return self.get_m_neutral_f()
        return self.get_neutral('m')

    @known_var(aliases=['n_n'])
    def get_n_neutral(self):
        '''number density of neutrals.'''
        # [TODO][REF] reduce redundancy with _get_n_neutral below?
        return self.get_neutral('n')

    @known_var(aliases=['T_n'])
    def get_T_neutral(self):
        '''temperature of neutrals.'''
        # [TODO][REF] reduce redundancy with _get_T_neutral below?
        return self.get_neutral('T')

    # not a known_var; just a helper function. called by self.get_n if appropriate.
    def _get_n_neutral(self):
        '''get the number density of self.fluid when it is an EppicNeutral or EppicNeutralList.
        (Or, crash with a helpful FormulaMissingError error message.)
        '''
        if not self._fluid_is_neutral():
            errmsg = (f'To use _get_n_neutral, self.fluid must neutral; but got fluid={self.fluid}')
            raise TypeError(errmsg)
        if getattr(self, '_inside_logic_of_get_n_neutral', False):
            with self.using(_inside_logic_of_get_n_neutral=True):
                # ^ prevent recursion on this part, in case self('n') calls self._get_n_neutral()
                try:
                    return self('n')
                    # if successful, user has set n using set_var. Probably via set_var('nj', value, ...)
                except DimensionAttributeError:  # crashed in get_n0; fluid has no 'n0' attribute.
                    pass  # handled below.
        errmsg = (f"Cannot get 'n' for neutral self.fluid={self.fluid}, when no value was set.\n"
                  f"Maybe you forgot to set_var('nj', value, ...) or set_var('n', value, ...)?")
        raise FormulaMissingError(errmsg) from None

    # not a known_var; just a helper function. called by self.get_T if appropriate.
    def _get_T_neutral(self):
        '''get the temperature of self.fluid when it is an EppicNeutral or EppicNeutralList.'''
        if not self._fluid_is_neutral():
            errmsg = (f'To use _get_T_neutral, self.fluid must neutral; but got fluid={self.fluid}')
            raise TypeError(errmsg)
        #with self.using(ncpu=1):  # never need multiprocessing for Tn_loader.
        return self.load_across_dims(self._T_neutral_loader, dims=['fluid'])

    def _T_neutral_loader(self):
        '''load T for neutrals. Helper function for self._get_T_neutral.
        gets T from vth and m. vth = sqrt(kB * T / m) --> T = m * vth^2 / (kB)
        '''
        vth = self.fluid.vth * self.u('u')
        if vth is None:
            errmsg = f'Cannot get Tn when {type(self.fluid).__name__}.vth not provided (got vth=None)'
            raise FluidValueError(errmsg)
        m = self.fluid.m * self.u('mass')
        T = m * vth**2 / self.u('kB')
        return xr.DataArray(T, attrs=self.units_meta())


    # # # --- SETTING VALUES; KNOWN SETTERS --- # # #
    # used when using set_var.

    @known_setter
    def set_n(self, value, **kw):
        '''set n to this value, by setting 'den' to the appropriate value.
        (To set neutral (jfluid) density, use set_nj instead.)
        '''
        n0 = self('n0')
        den = (value - n0) / n0
        return self.set('den', den, **kw)

    @known_setter
    def set_den(self, value, **kw):
        '''set den to this value. See also: set_n'''
        return self.set_var_internal('den', value, ['snap', 'fluid'], **kw, ukey='1')  # [dimensionless] --> ukey='1'

    @known_setter
    def set_u(self, value, **kw):
        '''set u to this value, by setting 'flux' to the appropriate value. flux = n * u.
        Depends on the current value of n; if also setting n be sure to set n first.
        '''
        n = self('n')
        flux = n * value
        return self.set('flux', flux, **kw)

    @known_setter
    def set_flux(self, value, **kw):
        '''set flux to this value. See also: set_u'''
        return self.set_var_internal('flux', value, ['snap', 'fluid', 'component'], **kw, ukey='flux')

    @known_setter
    def set_T(self, value, **kw):
        '''set T to this value, by setting all components of 'nvsqr' to the appropriate value.
        kB T ==  m * [vsqr - u^2]. --> nvsqr = n * ((kB * T / m) + u^2)
        Depends on the current value of n; if also setting n be sure to set n first.
        (To set neutral (jfluid) temperature, use set_Tj instead.)
        '''
        n = self('n')
        m = self('m')
        vtherm2 = self.u('kB') * value / m
        result = []
        for _component in self.iter_components():
            nvsqr = n * (vtherm2 + self('u')**2)
            result.extend(self.set('nvsqr', nvsqr, **kw))
        return result

    @known_setter
    def set_nvsqr(self, value, **kw):
        '''set nvsqr to this value. See also: set_T'''
        return self.set_var_internal('nvsqr', value, ['snap', 'fluid', 'component'], **kw, ukey='n u2')

    @known_setter
    def set_phi(self, value, **kw):
        '''set phi to this value.'''
        return self.set_var_internal('phi', value, ['snap'], **kw, ukey='E length')

    # NOT A KNOWN SETTER - combined method for setting multiple things.
    def set_bases(self, *, n=UNSET, u=UNSET, T=UNSET, ux=UNSET, uy=UNSET, uz=UNSET, forall=[],
                  v=UNSET, vx=UNSET, vy=UNSET, vz=UNSET, **kw):
        '''set n, u, and T to these values (for the relevant current behavior in self..).
        (e.g. if self.fluid=0, setting values for fluid=0, only.)
        
        n, u, T, ux, uy, uz: UNSET, None, or number
            UNSET --> don't set this value
            None --> delete this value from self.setvars
            number --> set this value.
            Note: if u is provided, self.component must be a single value.
        v, vx, vy, vz:
            aliases for u, ux, uy, uz, respectively.
        forall: list of strings
            behavior attrs to which set value should apply to all of.
            E.g., forall=['snap'] --> set value applies at all snaps instead of just current snap.

        additional kwargs, if provided, go to self.using(**kw) during the operation.

        returns (list of set quantities, list of unset quantities)
        '''
        # aliases / bookkeeping
        for v_, u_ in zip([v, vx, vy, vz], [u, ux, uy, uz]):
            if v_ is not UNSET and u_ is not UNSET:
                raise InputConflictError(f'set v or u or neither, but not both.')
        if v is not UNSET: u = v
        if vx is not UNSET: ux = vx
        if vy is not UNSET: uy = vy
        if vz is not UNSET: uz = vz
        # actually setting values
        added = []
        deled = []
        with self.using(**kw):
            # set n first; setting u and T internally depends on n.
            if n is UNSET:
                pass
            elif n is None:
                deled.extend(self.unset('den'))
            else:
                added.extend(self.set('n', n, forall=forall))
            # set u
            if u is UNSET:
                pass
            elif u is None:
                deled.extend(self.unset('flux'))
            else:
                added.extend(self.set('u', u, forall=forall))
            # set u, component-wise
            for x, ux_ in zip('xyz', [ux, uy, uz]):
                with self.using(component=x):
                    if ux_ is UNSET:
                        pass
                    elif ux_ is None:
                        deled.extend(self.unset(f'flux'))
                    else:
                        added.extend(self.set(f'u', ux_, forall=forall))
            # set T
            if T is UNSET:
                pass
            elif T is None:
                deled.extend(self.unset('nvsqr'))
            else:
                added.extend(self.set('T', T, forall=forall))
        return (added, deled)

    # # # SETTERS FOR JFLUID # # #
    @known_setter
    def set_nj(self, value, **kw):
        '''set n to this value for the current self.jfluid.
        Getting 'n' returns value when self.fluid is the self.jfluid from when 'n' was set.
        The implementation here assumes jfluids are inherently different from fluids,
            which is true for Eppic, where jfluid is neutral (by default).
        '''
        if is_iterable_dim(self.jfluids) and is_iterable_dim(self.fluids):
            if any(jfluid in self.fluids for jfluid in self.jfluids):
                raise FluidValueError(f'jfluids and fluids overlap; cannot use set_nj(...).')
        # temporarily set fluid to jfluid. include fluids=self.jfluids because fluids and jfluids differ.
        with self.using(fluids=self.jfluids, fluid=self.jfluid):
            battrs = ['snap', 'fluid']  # 'fluid' because getting 'n' with getj will set fluid=jfluid too.
            return self.set_var_internal('n', value, battrs, **kw, ukey='n')

    @known_setter
    def set_Tj(self, value, **kw):
        '''set T to this value for the current self.jfluid.
        Getting 'n' returns value when self.fluid is the self.jfluid from when 'n' was set.
        The implementation here assumes jfluids are inherently different from fluids,
            which is true for Eppic, where jfluid is neutral (by default).
        '''
        if is_iterable_dim(self.jfluids) and is_iterable_dim(self.fluids):
            if any(jfluid in self.fluids for jfluid in self.jfluids):
                raise FluidValueError(f'jfluids and fluids overlap; cannot use set_Tj(...).')
        # temporarily set fluid to jfluid. include fluids=self.jfluids because fluids and jfluids differ.
        with self.using(fluids=self.jfluids, fluid=self.jfluid):
            battrs = ['snap', 'fluid']
            return self.set_var_internal('T', value, battrs, **kw, ukey='1')  # [K] is "dimensionless"; u_K==1.
