"""
File Purpose: loader for tfbi-related quantities
"""
import os

from .tfbi_solver import TfbiSolver, _paramdocs_tfbi_solving
from ..addon_tools import register_addon_loader_if
from ...defaults import DEFAULTS
from ...errors import FluidValueError, InputMissingError, MemorySizeError
from ...quantities import QuantityLoader
from ...tools import (
    format_docstring,
    simple_property,
    xarray_min, xarray_grid,
    xarray_load, xarray_save,
    xarray_min_coord_where,
)


### --------------------- TfbiLoader --------------------- ###

@register_addon_loader_if(DEFAULTS.ADDONS.LOAD_TFBI)
@format_docstring(**_paramdocs_tfbi_solving)
class TfbiLoader(QuantityLoader):
    '''quantities related to the Thermal Farley Buneman Instability.
    
    NOTE: for simple calculations, consider using maindims_means=True!

    To solve TFBI theory, you can use the following pattern:
        {solving_pattern}
        
        Notes:
            {solving_pattern_notes}
    '''
    tfbi_solver_cls = TfbiSolver

    def tfbi_mask(self, *, kappae=1, ionfrac=1e-3, kappai=1, set=True):
        '''set & return self.mask appropriate for TFBI.
        kappae: None or number, default 1
            lower limit for kappae; mask points with kappae smaller than this value.
            (kappae = |qe| |B| / (me nuen))
            Internally, loaded as 'kappa' with fluid='e'.
            TFBI probably only matters when electrons are magnetized --> kappae >> 1.
            Applying TFBI theory to kappae masked points would still be fine,
                but will probably always say "instability doesn't grow there".
            None --> no mask on kappae
        ionfrac: None or number
            upper limit for ionfrac; mask points with ionfrac larger than this value.
            (ionfrac = ne / ntotal)
            Internally, loaded as 'SF_ionfrac' if available,
                else ne/(ne+n_neutral), with ne from self('n', fluid=self.fluids.get_electron()).
                (Note: checked in Bifrost: SF_ionfrac uses SF_n = sum of element densities.
                    SF_n does not include ne.
                    The formula SF_ionfrac = ne/(ne+nn) uses ne as a proxy for sum(ni),
                        which will be okay unless there are twice+ ionized species.)
            TFBI assumes weakly ionized.
            E_un0 also assumes weakly ionized, when self.assume_un='u'.
            Applying TFBI theory to ionfrac masked points would be a big issue,
                as it could lead to many false positives,
                where physical effects not included in the theory damp out the TFBI.
            None --> no mask on ionfrac.
        kappai: None or number, default 1
            upper limit for min kappai; mask points with all kappai larger than this value.
            (kappai = |qi| |B| / (mi nuin))
            Internally, loaded as 'kappa' with fluid=ions, then take min across fluids.
            TFBI probably only matters when at least 1 ion species is demagnetized --> kappai < 1.
            Applying TFBI theory to kappai masked points would still be fine,
                but will probably always say "instability doesn't grow there".
            None --> no mask on kappai.
        set: bool
            whether to set self.mask = result.
            if False, only returns the result, without also setting self.mask.
        '''
        if all(x is None for x in (kappae, ionfrac, kappai)):
            raise InputMissingError('At least one must be non-None: kappae, ionfrac, kappai.')
        with self.using(masking=False):
            if ionfrac is not None:
                if self.has_var('SF_ionfrac'):
                    ionfrac_vals = self('SF_ionfrac')
                else:
                    ne = self('n', fluid=self.fluids.get_electron())
                    nn = self('n_neutral')
                    ionfrac_vals = ne / (ne + nn)
            if kappae is not None:
                kappae_vals = self('kappa', fluid=self.fluids.get_electron())
            if kappai is not None:
                kappai_vals = self('kappa', fluid=self.fluids.ions())
                kappai_vals = xarray_min(kappai_vals, dim='fluid')
        mask = None
        if ionfrac is not None:
            mask_ionfrac = (ionfrac_vals > ionfrac)
            mask = mask_ionfrac if mask is None else (mask | mask_ionfrac)
        if kappae is not None:
            mask_kappae = (kappae_vals < kappae)
            mask = mask_kappae if mask is None else (mask | mask_kappae)
        if kappai is not None:
            mask_kappai = (kappai_vals > kappai)
            mask = mask_kappai if mask is None else (mask | mask_kappai)
        if set:
            self.mask = mask
            mask = self.mask  # <-- may have been altered slightly due to mask attr.
        return mask

    def tfbi_ds(self, ions=None, *, all=True, output_mask=True, **kw_get_var):
        '''returns Dataset of all the values needed & relevant to TFBI theory.
        Equivalent: self('tfbi_all', fluid=[electron, *ions], masking=True, ...)
        
        ions: None or specifier of multiple fluids (e.g. slice, or list of strs)
            list of ions to use. None --> self.fluids.ions()
        all: bool
            whether to include 'tfbi_all', or only 'tfbi_inputs'.
            With only 'tfbi_inputs', the theory is still solvable, but harder to inspect later.
        output_mask: bool
            whether to store_mask in results, if self.masking (and self.mask is not None)
        additional kwargs passed to self(...)
        '''
        if ions is None:
            ions = self.fluids.ions()
        fluid = [self.fluids.get_electron(), *ions]
        tfbi_var = 'tfbi_all' if all else 'tfbi_inputs'
        return self(tfbi_var, fluid=fluid, output_mask=output_mask, **kw_get_var)

    @format_docstring(tfbi_solver_docs=TfbiSolver.__doc__, sub_ntab=1)
    def tfbi_solver(self, ions=None, **kw_solver):
        '''return TfbiSolver object for solving TFBI theory based on values in self.
        all inputs here get passed to TfbiSolver. Equivalent: TfbiSolver(self, ...).

        docs for TfbiSolver copied below for convenience:
        -------------------------------------------------
        {tfbi_solver_docs}
        '''
        return self.tfbi_solver_cls(self, ions=ions, **kw_solver)

    # # # LOADING TFBI INPUTS & RELATED VARS # # #
    TFBI_VARS = ['mod_B', 'E_un0_perpmod_B', 'kB', 'T_n', 'm_n',  # "global" scalars
                    'm', 'nusn', 'skappa', 'eqperp_ldebye']  # scalars which depend on fluid.

    # extra vars, relevant to TFBI theory, but not necessary.
    TFBI_EXTRAS = ['SF_n', 'eps0', 'abs_qe', # "global" scalars
                    'n', 'n_n', 'eqperp_lmfp',
                    # 'tfbi_fscale_rel',  # this one turned out to be irrelevant --> exclude by default
                    ]   # scalars which depend on fluid.

    @known_var(deps=TFBI_VARS)
    def get_tfbi_inputs(self, **kw_get_vars):
        '''returns xarray.Dataset of values to input to the tfbi theory.
        "global" scalars (no dependence on component nor fluid)
            'mod_B': |magnetic field|
            'E_un0_perpmag_B': |E_un0 perp to B|. E_un0 = electric field in u_neutral=0 frame.
            'kB': boltzmann constant. kB * T = temperature in energy units.
            'T_n': temperature of neutrals.
            'm_n': mass of neutrals.
        scalars which depend on fluid. Note: checks self.fluid, not self.fluids.
            'm': mass of all non-neutral fluids
            'nusn': collision frequency between fluid and neutrals.
            'skappa': signed magnetization parameter; q |B| / (m nusn)
            'eqperp_ldebye': each fluid's debye length at its "equilibrium" temperature,
                        after considering zeroth order heating due to E_un0_perpmag_B.

        Results depend on self.fluid. May want to call as self('tfbi_inputs', fluid=CHARGED).
        '''
        if any(f.is_neutral() for f in self.iter_fluid()):
            errmsg = ('get_tfbi_inputs expects self.fluid to be charged fluids only,\n'
                      f'but it includes neutrals: {[f for f in self.iter_fluid() if f.is_neutral()]}')
            raise FluidValueError(errmsg)
        # [TODO][EFF] improve efficiency by avoiding redundant calculations,
        #    e.g. B is calculated separately for mod_B, E_un0_perpmag_B, and skappa,
        #    while E_un0 is calculated separately for E_un0_perpmag_B and eqperp_ldebye.
        tfbi_vars = self.TFBI_VARS
        return self(tfbi_vars, **kw_get_vars)

    @known_var(deps=TFBI_EXTRAS)
    def get_tfbi_extras(self, **kw_get_vars):
        '''returns xarray.Dataset of values relevant to TFBI theory but not necessary for inputs.
        Currently this just includes:
            'eqperp_lmfp': each fluid's collisional mean free path at its "equilibrium" temperature,
                        after considering zeroth order heating due to E_un0_perpmag_B.
            'SF_n': sum of number densities of all species (including neutrals)
            'n': number densities of each specie in self.fluid.
            'n_n': number density of neutral fluid.
            'n*kappa': number density times kappa.
                    TFBI dispersion relation terms scale with n*kappa for each fluid,
                    so this quantity roughly estimates the relative importance of each fluid.

        Results depend on self.fluid. May want to call as self('tfbi_extras', fluid=CHARGED).
        '''
        if any(f.is_neutral() for f in self.iter_fluid()):
            errmsg = ('get_tfbi_extras expects self.fluid to be charged fluids only,\n'
                      f'but it includes neutrals: {[f for f in self.iter_fluid() if f.is_neutral()]}')
            raise FluidValueError(errmsg)
        tfbi_extras = self.TFBI_EXTRAS
        kw_get_vars.setdefault('missing_vars', 'ignore')  # it's okay if some extras are un-gettable.
        return self(tfbi_extras, **kw_get_vars)

    @known_var(deps=['tfbi_inputs', 'tfbi_extras'])
    def get_tfbi_all(self, **kw_get_vars):
        '''returns xarray.Dataset of values relevant to TFBI theory.
        This includes tfbi_inputs (required for theory) and tfbi_extras (optional)

        Results depend on self.fluid. May want to call as self('tfbi_all', fluid=CHARGED).
        '''
        return self(['tfbi_inputs', 'tfbi_extras'], **kw_get_vars)

    @known_var(deps=['n*kappa'])
    def get_tfbi_fscale(self):
        '''tfbi_fscale = n * kappa
        tfbi dispersion relation sums terms proportional to n * kappa, for each fluid.
        '''
        return self('n*kappa')

    @known_var(deps=['tfbi_fscale'])
    def get_tfbi_fscale_rel(self):
        '''tfbi_fscale_rel = tfbi_fscale(this fluid) / tfbi_fscale(electrons).'''
        return self('tfbi_fscale') / self('tfbi_fscale', fluid=self.fluids.get_electron())

    # # # LOADING TFBI SOLUTION # # #
    @known_var(deps=['tfbi_inputs'])
    def get_tfbi_omega(self, *, kw_tfbi_solve=dict(), **kw_tfbi_solver):
        '''Thermal Farley Buneman Instability roots with largest imaginary part at each point in self.
        Equivalent: self.tfbi_solver(**kw_tfbi_solver).solve(**kw_solve)['omega'].

        Can provide kwargs, e.g. self('tfbi_omega', ions=['H_II', 'C_II'], kw_tfbi_solve=dict(ncpu=1)).

        For more control, use self.tfbi_solver() directly.
        For even more control, use the pattern described in help(self.tfbi_solver_cls).

        Recommended: consider using 'tfbi_omega_ds' instead of 'tfbi_omega'.
            'tfbi_omega_ds' gives the full Dataset of all values relevant to the solution.
            'tfbi_omega' just gives the DataArray of omega, which is harder to inspect later.
        '''
        kw_tfbi_solver.setdefault('tfbi_all', False)  # dropping ds0 later anyways so don't load it.
        solver = self.tfbi_solver(**kw_tfbi_solver)
        kw_tfbi_solve = kw_tfbi_solve.copy()
        kw_tfbi_solve.setdefault('return_ds', False)  # just return omega, not the full ds.
        # (if user specified return_ds=True, then they will get the full ds, but that's okay.)
        return solver(**kw_tfbi_solve)

    @known_var(deps=['tfbi_all'])
    def get_tfbi_omega_ds(self, *, kw_tfbi_solve=dict(), **kw_tfbi_solver):
        '''Thermal Farley Buneman Instability solution at each point in self.
        Equivalent: self.tfbi_solver(**kw_tfbi_solver).solve(**kw_solve).

        Can provide kwargs, e.g. self('tfbi_omega_ds', ions=['H_II', 'C_II'], kw_tfbi_solve=dict(ncpu=1)).

        For more control, use self.tfbi_solver() directly.
        For even more control, use the pattern described in help(self.tfbi_solver_cls).
        '''
        kw_tfbi_solver.setdefault('tfbi_all', True)
        solver = self.tfbi_solver(**kw_tfbi_solver)
        return solver(**kw_tfbi_solve)


    # # # --- SETTING VALUES; KNOWN SETTERS --- # # #
    # used when using set_var.

    @known_setter(aliases=['mag_B'])
    def set_mod_B(self, value, **kw):
        '''set mod_B to this value. Also sets mag_B, mod2_B, and mag2_B.'''
        # [TODO] pattern handling for setters, for mod; see issue #5 on git for more info.
        #   (implementing pattern handling should make this function obsolete / mostly obsolete.)
        self.set_var_internal('mod_B', value, ['snap'], **kw, ukey='b_field')
        self.set_var_internal('mag_B', value, ['snap'], **kw, ukey='b_field')
        value2 = value**2
        self.set_var_internal('mod2_B', value2, ['snap'], **kw, ukey='b_field2')
        self.set_var_internal('mag2_B', value2, ['snap'], **kw, ukey='b_field2')

    @known_setter(aliases=['E_un0_perpmag_B'])
    def set_E_un0_perpmod_B(self, value, **kw):
        '''set E_un0_perpmod_B to this value. Also sets E_un0_perpmag_B.'''
        self.set_var_internal('E_un0_perpmag_B', value, ['snap'], **kw, ukey='e_field')
        self.set_var_internal('E_un0_perpmod_B', value, ['snap'], **kw, ukey='e_field')


    # # # --- COMPUTING E_THRESH --- # # #

    _default_grid_size = (
            DEFAULTS.ADDONS.TFBI_EBSPEED_LOGMIN,
            DEFAULTS.ADDONS.TFBI_EBSPEED_LOGMAX,
            DEFAULTS.ADDONS.TFBI_EBSPEED_LOGSTEP
    )
    cls_behavior_attrs.register('tfbi_EBspeed_grid_size', default=_default_grid_size)
    tfbi_EBspeed_grid_size = simple_property('_tfbi_EBspeed_grid_size', default=_default_grid_size,
        doc=f'''(logmin, logmax, logstep) for self('tfbi_EBspeed_grid'); log is base 10.
        Default: DEFAULTS.ADDONS.TFBI_EBSPEED_LOGMIN, LOGMAX, LOGSTEP; (default: {_default_grid_size}).''')
    del _default_grid_size

    @known_var
    def get_tfbi_EBspeed_grid(self):
        '''return a 1D grid of EBspeed values with constant logstep.
        determines logmin, logmax, logstep (base 10) from self.tfbi_EBspeed_grid_size.
        result's name & EBspeed grid dim is always 'EBspeed'.
        '''
        logmin, logmax, logstep = self.tfbi_EBspeed_grid_size
        return xarray_grid(10**logmin, 10**logmax, logstep=logstep, name='EBspeed')

    def _tfbi_vs_EBspeed_file(self):
        '''returns expected abspath to file for storing tfbi solution across EBspeed grid.
        Depends on current value of self.tfbi_EBspeed_grid_size.
        Does not check whether file exists already
            (might use this to find existing file, or to determine filepath for saving result.)
        Result is like:
            {self.unique_notes_dirname}/_pc_tfbi/EBspeed_{logmin:.4g}_{logmax:.4g}_{logstep:.4g}.pcxarr
        '''
        logmin, logmax, logstep = self.tfbi_EBspeed_grid_size
        basename = f'EBspeed_{logmin:.4g}_{logmax:.4g}_{logstep:.4g}.pcxarr'
        return os.path.join(self.unique_notes_dirname, '_pc_tfbi', basename)

    @format_docstring(_mbytes_max=DEFAULTS.ADDONS.TFBI_EBSPEED_INPUTS_MBYTES_MAX)
    def solve_tfbi_vs_EBspeed(self, *, Mbytes_max=True, cache='caches', **kw_solve):
        '''solve tfbi across EBspeed grid from self('tfbi_EBspeed_grid').
        CAUTION: the implementation here might self.set('E_un0_perpmod_B', self('mod_B') * EBspeed)
        [TODO] avoid changing self.setvars... (or, at least, restore previous self.setvars afterwards.)
        Suggestion: use self.setvars.clear() after calling this function.

        Mbytes_max: bool or number
            maxmimum allowed data size [in MB] of self('tfbi_inputs'), before setting EBspeed grid.
            (helps prevent accidental requests to solve too many points at once.)
            (ignored if `cache` implies to load from existing cached file.)
            True --> use default: DEFAULTS.ADDONS.TFBI_EBSPEED_INPUTS_MBYTES_MAX (default: {_mbytes_max}).
            False or None --> no maximum
        cache: 'caches', 'cache', 'cached', or False
            controls how & whether to handle cache the result.
            cached results go to self._tfbi_vs_EBspeed_file(); default:
                {{self.unique_notes_dirname}}/_pc_tfbi/EBspeed_{{logmin:.4g}}_{{logmax:.4g}}_{{logstep:.4g}}.pcxarr
            where logmin, logmax, logstep are from self.tfbi_EBspeed_grid_size
            'caches' --> read from saved file if it exists. Else, solve and save to file.
            'cache' --> solve and save to file. Saved file must not exist yet (else, crash).
            'cached' --> read from saved file. Saved file must exist (else, crash).
            False --> solve and return result, but do not save to file nor check if file exists.
        additional kwargs are passed to self.tfbi_solver().solve(**kw)
        '''
        # check for existing file
        if cache:
            filename = self._tfbi_vs_EBspeed_file()
            if cache == 'caches':
                if os.path.exists(filename):
                    return xarray_load(filename)
                # else, cache it later
            elif cache == 'cached':
                if os.path.exists(filename):
                    return xarray_load(filename)
                else:
                    raise FileNotFoundError(f'cache="cached" but _tfbi_vs_EBspeed_file() does not exist: {filename!r}.')
            elif cache == 'cache':
                if os.path.exists(filename):
                    raise FileExistsError(f'cache="cache" but _tfbi_vs_EBspeed_file() already exists: {filename!r}.')
                # else, cache it later
        # check size of tfbi_inputs
        if Mbytes_max is not False and Mbytes_max is not None:
            if Mbytes_max is True:
                Mbytes_max = DEFAULTS.ADDONS.TFBI_EBSPEED_INPUTS_MBYTES_MAX
            try:
                tfbi_inputs = self('tfbi_inputs', array_MBmax=Mbytes_max)
            except MemorySizeError:
                inputs_Mbytes = f'an individual tfbi_input array, alone, is already larger than {Mbytes_max}'
                too_big = True
            else:
                inputs_Mbytes = f'{tfbi_inputs.pc.nMbytes:.4g}'
                too_big = tfbi_inputs.pc.nMbytes > Mbytes_max
            if too_big:
                errmsg = (f'self("tfbi_inputs").pc.nMbytes ({inputs_Mbytes} MB) > Mbytes_max ({Mbytes_max}).'
                          '\nConsider setting larger Mbytes_max (or DEFAULTS.ADDONS.TFBI_EBSPEED_INPUTS_MBYTES_MAX),'
                          f' or reducing the number of points being considered here.')
                raise MemorySizeError(errmsg)
        # set E based on EBspeed grid
        EBspeed = self('tfbi_EBspeed_grid')
        self.set('E_un0_perpmag_B', EBspeed * self('mod_B'))
        # solve TFBI
        solver = self.tfbi_solver()
        result = solver.solve(**kw_solve)
        # cache
        if cache:
            xarray_save(result, filename)
        return result

    @known_var
    def get_tfbi_vs_EBspeed(self):
        '''return tfbi solution across EBspeed grid. Load saved result if it exists, else save result to file.
        CAUTION: the implementation here might self.set('E_un0_perpmod_B', self('mod_B') * EBspeed)
        [TODO] avoid changing self.setvars... (or, at least, restore previous self.setvars afterwards.)

        CAUTION: the implementation here assumes self.tfbi_EBspeed_grid_size is enough to uniquely specify the result;
            e.g. if there is a different result at each snapshot of self, that will not be understood here.

        Equivalent: self.solve_tfbi_vs_EBspeed(cache='caches')
        '''
        verbose = getattr(self, 'verbose', True)
        return self.solve_tfbi_vs_EBspeed(cache='caches', verbose=verbose)

    @known_var
    def get_cached_tfbi_vs_EBspeed(self):
        '''return a previously-computed tfbi solution across EBspeed grid.
        Expects solution to live in _tfbi_vs_EBspeed_file(); default:
            {self.unique_notes_dirname}/_pc_tfbi/EBspeed_{logmin:.4g}_{logmax:.4g}_{logstep:.4g}.pcxarr

        CAUTION: the implementation here assumes self.tfbi_EBspeed_grid_size is enough to uniquely specify the result;
            e.g. if there is a different result at each snapshot of self, that will not be understood here.
        '''
        filename = self._tfbi_vs_EBspeed_file()
        if not os.path.exists(filename):
            errmsg = (f'tfbi_vs_EBspeed solution not found: {filename!r}'
                      f'\nConsider running self.solve_tfbi_vs_EBspeed() to compute it, '
                      'after downsampling somehow (e.g. via self.maindims_means=True, self.snap=0).'
                      '\nCAUTION: self.solve_tfbi_vs_EBspeed() might self.set("E_un0_perpmod_B"); '
                      f'consider using self.copy() first, or making a new {type(self).__name__} object after.')
            raise FileNotFoundError(errmsg)
        return xarray_load(filename)

    cls_behavior_attrs.register('tfbi_growth_thresh', default=DEFAULTS.ADDONS.TFBI_GROWTH_THRESH)
    tfbi_growth_thresh = simple_property('_tfbi_growth_thresh', default=DEFAULTS.ADDONS.TFBI_GROWTH_THRESH,
        doc=f'''threshold for confirming "yes there is tfbi growth predicted here", during self('tfbi_E_thresh').
        growth must be larger than (not equal to) this value, to confirm growth.
        0.0 is the theoretical threshold. A small positive value (e.g. 0.001) helps to avoid tiny errors.
        The default is DEFAULTS.ADDONS.TFBI_GROWTH_THRESH (default: {DEFAULTS.ADDONS.TFBI_GROWTH_THRESH}).''')

    @known_var(deps=['cached_tfbi_vs_EBspeed'])
    def get_tfbi_EBspeed_thresh(self):
        '''threshold EBspeed for TFBI to grow. NaN if no growth predicted across the EBspeed grid considered.
        
        Assumes user has already run self.solve_tfbi_vs_EBspeed().
        If not, consider doing:
            copied = self.copy()
            copied.set_attrs(maindims_means=True, snap=0)  # or some other way to downsample...
            copied.solve_tfbi_vs_EBspeed()

        equivalent to tfbi_vs_EBspeed.pc.min_coord_where('EBspeed', tfbi_vs_EBspeed.it.growth_kmax()>0)
        '''
        tfbi_vs_EBspeed = self('cached_tfbi_vs_EBspeed')
        growth_kmax = tfbi_vs_EBspeed.it.growth_kmax()
        return xarray_min_coord_where(tfbi_vs_EBspeed, 'EBspeed', growth_kmax > 0)

    @known_var(deps=['tfbi_EBspeed_thresh', 'mod_B'])
    def get_tfbi_E_thresh(self):
        '''threshold E_un0_perpmag_B for TFBI to grow. NaN if no growth predicted across the EBspeed grid considered.
        Equivalent: self('tfbi_EBspeed_thresh') * self('mod_B').

        Assumes user has already run self.solve_tfbi_vs_EBspeed().
        See self.help('tfbi_EBspeed_thresh') for more details.
        '''
        EBspeed = self('tfbi_EBspeed_thresh')
        return EBspeed * self('mod_B')
