"""
File Purpose: solving tfbi
"""

from ...tools import ImportFailed
try:
    import tfbi_theory as tt
except ImportError as err:
    tt = ImportFailed("tfbi_theory", err=err, locals=locals(), abbrv='tt')

from ...defaults import DEFAULTS
from ...errors import InputError
from ...tools import (
    format_docstring, alias, simple_property,
    UNSET,
    ProgressUpdater,
)

_paramdocs_tfbi_solving = {
    'solving_pattern': '''import tfbi_theory as tt
        import PlasmaCalcs as pc
        cc = ... # any PlasmaCalculator object from PlasmaCalcs.
        ds0 = cc.tfbi_ds()
        kp = tt.kPickerLowres(ds0)
        dsk = kp.get_ds()   # copy of ds0, but with ds['k'] = k from kPicker.
        drel = tt.TfbiDisprelC.from_ds(dsk)
        dsR = drel.solve()  # copy of dsk, but with ds['omega'] = solution to TFBI theory!''',
    'solving_pattern_notes': '''if cc has more than ~4 ions, you will want to drop some or group them somehow.
                e.g. for MhdMultifluidCalculator, before calling tfbi_ds():
                    cc.use_mix_heavy_ions(0.3, m_mean_mode='density')
            You can also pick ions directly during cc.tfbi_ds().
                e.g. for Bifrost chromosphere analysis, where n[He_II] < 1e-6 * ne, I use:
                    cc.tfbi_ds(ions=[i for i in cc.fluids if i.q==1 and i!='He_II'])
            After finishing solving, you might want to save the result,
                e.g. dsR.pc.save('filename') saves result to 'filename.pcxarr';
                can load it later via pc.xarray_load('filename.pcxarr').''',
}


### --------------------- TfbiSolver --------------------- ###

@format_docstring(**_paramdocs_tfbi_solving,
                  max_num_ions=DEFAULTS.ADDONS.TFBI_MAX_NUM_IONS)
class TfbiSolver():
    '''high-level interface for solving TFBI theory across many physical parameters.

    Call TfbiSolver to solve TFBI.
    Example:
        import PlasmaCalcs as pc
        cc = pc.PlasmaCalculator(...)   # <-- your PlasmaCalculator of choice
        solver = pc.TfbiSolver(cc)
        solution = solver()             # alias: solver.solve()
    solution is an xarray.Dataset with all relevant quantities (see TfbiLoader.get_tfbi_all),
        and 'omega' telling roots with largest imaginary part.

    If you need more precise control over the solving process, use the pattern:
        {solving_pattern}

    TfbiSolver internally stores self.cc, ds0, kp, dsk, drel, and dsR,
        as defined by the pattern above.

    cc: PlasmaCalculator
        PlasmaCalculator object used to load the data.
        Should be a TfbiLoader subclass. (PlasmaCalculator satisfies this by default,
            assuming successful import SymSolver and import tfbi_theory.)
    ions: None or specifier of multiple fluids (e.g. slice, or list of strs)
        None --> use cc.fluids.ions()
        print warning if this specifies more than DEFAULTS.ADDONS.TFBI_MAX_NUM_IONS ions
            (default: {max_num_ions}), because then solving will be slow and may be inaccurate.
        ions are determined when called, not during __init__.
    kres: 'low', 'mid', or 'high'
        resolution in k-space. Tells which self.kPicker_cls to use.
        'low' --> tfbi_theory.kPickerLowres. Recommended if solving across many points.
        'mid' --> tfbi_theory.kPickerMidres. Recommended if solving across a few points.
        'high' --> tfbi_theory.kPickerHighres. Recommended if solving at only 1 point.
    mod, lmod, ang: UNSET or dict
        passed directly to kPicker if provided. Can specify k values other than the defaults.
        see help(self.kPicker_cls) for more details.
    tfbi_all: bool
        whether to compute all relevant tfbi vars, ds0 = cc('tfbi_all').
        False --> compute only the necessary vars, ds0 = cc('tfbi_inputs').
    drel_cls: None, str, or class
        tfbi_theory class to use for solving TFBI theory.
        None --> use self.drel_cls default: tt.TfbiDisprelC
        str --> use getattr(tt, drel_cls) to get the class.
    '''
    kPickerLowres_cls_name = 'kPickerLowres'  # used to make self.kPicker_cls if kres='low'
    kPickerMidres_cls_name = 'kPickerMidres'  # used to make self.kPicker_cls if kres='mid'
    kPickerHighres_cls_name = 'kPickerHighres'  # used to make self.kPicker_cls if kres='high'

    @property
    def kPicker_cls(self):
        '''kPicker class to use for choosing wavevectors to consider. Depends on self.kres:
        'low' --> tfbi_theory.kPickerLowres
        'mid' --> tfbi_theory.kPickerMidres
        'high' --> tfbi_theory.kPickerHighres
        '''
        if self.kres == 'low':
            return getattr(tt, self.kPickerLowres_cls_name)
        elif self.kres == 'mid':
            return getattr(tt, self.kPickerMidres_cls_name)
        elif self.kres == 'high':
            return getattr(tt, self.kPickerHighres_cls_name)
        else:
            raise InputError(f"Invalid kres. Expected 'low' or 'high'; got {self.kres!r}")

    drel_cls_name = 'TfbiDisprelC'  # used to make self.drel_cls.
    # (drel_cls = tt.TfbiDisprelC here would crash immediately if tt import failed.
    # By using drel_cls property, we avoid this crash until it's actually relevant.)
    drel_cls = simple_property('_drel_cls', setdefaultvia='_default_drel_cls',
        doc='''class to use for solving TFBI theory. Default: tt.TfbiDisprelC.''')
    def _default_drel_cls(self):
        '''default drel_cls. getattr(tt, self.drel_cls_name)'''
        return getattr(tt, self.drel_cls_name)

    def __init__(self, cc, ions=None, *, kres='low', mod=UNSET, lmod=UNSET, ang=UNSET, tfbi_all=True,
                 drel_cls=None):
        self.cc = cc
        self.ions = ions
        self.kres = kres
        self.mod = mod
        self.lmod = lmod
        self.ang = ang
        self.tfbi_all = tfbi_all
        if drel_cls is not None:
            if isinstance(drel_cls, str):
                self.drel_cls = getattr(tt, drel_cls)
            elif isinstance(drel_cls, type):
                self.drel_cls = drel_cls
            else:
                raise InputError(f"Invalid drel_cls. Expected None, str, or class; got {drel_cls!r}")

    @property
    def ions_explicit(self):
        '''list of ions from self.cc which would be used during self.cc.tfbi_ds()'''
        if self.ions is None:
            result = self.cc.fluids.ions()
        else:
            result = self.cc.fluids.get(self.ions)
        return result

    def _warn_if_too_many_ions(self):
        '''print warning if self.ions specifies too many ions.'''
        default_nmax = DEFAULTS.ADDONS.TFBI_MAX_NUM_IONS
        ions = self.ions_explicit
        if len(ions) > default_nmax:
            warnmsg = (f">>> Warning: TfbiSolver has {len(ions)} ions, which may be slow and inaccurate. <<<\n"
                       f"    (To avoid this warning, either use fewer ions, or "
                            f"increase DEFAULTS.ADDONS.TFBI_MAX_NUM_IONS (={default_nmax}, currently).)")
            print(warnmsg)

    __call__ = alias('solve')

    @format_docstring(**_paramdocs_tfbi_solving, sub_ntab=1)
    def solve(self, *, verbose=True, **kw_growth_root):
        '''solve TFBI theory. Assigns self.ds0, kp, dsk, drel, and dsR.
        Does not do any caching at this level; if the code crashes you will need to restart it completely.
        For more precise control including possibility for caching, use the pattern directly:
            {solving_pattern}

        verbose: bool
            whether to print progress updates (highly recommended).
        additional kwargs get passed directly to drel.solve().
            (options include: ncpu, ncoarse, careful)
        '''
        updater = ProgressUpdater(print_freq=0 if verbose else -1)  # print all statements if verbose, else nothing.
        self._warn_if_too_many_ions()
        # get ds0 -- manage progress updates here.
        ds0_updater = ProgressUpdater(print_freq=0 if verbose else -1)
        ds0_updater.print(f'getting ds0 via {type(self.cc).__name__}.tfbi_ds() ...')
        self.ds0 = self.cc.tfbi_ds(ions=self.ions, all=self.tfbi_all)
        ds0_updater.finalize(f'solver.ds0 = {type(self.cc).__name__}.tfbi_ds()', end='\n')
        # picking k is usually fast; no need for progress updates.
        kw_kPicker = dict(mod=self.mod, lmod=self.lmod, ang=self.ang)
        kw_kPicker = {k: v for k, v in kw_kPicker.items() if v is not UNSET}
        self.kp = self.kPicker_cls(self.ds0, **kw_kPicker)
        # follow the rest of the pattern. tt manages its own progress updates.
        self.dsk = self.kp.get_ds()
        self.drel = self.drel_cls.from_ds(self.dsk)
        self.dsR = self.drel.solve(verbose=verbose, **kw_growth_root)
        updater.print_clear(force=verbose)  # clear print statements on current line, if we're printing anything.
        updater.finalize(f'{type(self).__name__}.solve() (all steps from start to finish)', always=True)
        return self.dsR

    solution = alias('dsR', doc='''result of self.solve(); alias to self.dsR.''')
    solved = property(lambda self: hasattr(self, 'dsR'), doc='''tells whether self.solution exists''')

    def __repr__(self):
        contents = []
        cc_str = f'title={self.cc.title!r}' if hasattr(self.cc, 'title') else '...'
        contents.append(f'cc={type(self.cc).__name__}({cc_str})')
        if self.ions is not None:
            contents.append(f'ions={self.ions!r}')
        if isinstance(self.mod, dict) and len(self.mod) > 0:
            contents.append(f'mod={self.mod!r}')
        if isinstance(self.lmod, dict) and len(self.lmod) > 0:
            contents.append(f'lmod={self.lmod!r}')
        if isinstance(self.ang, dict) and len(self.ang) > 0:
            contents.append(f'ang={self.ang!r}')
        if self.tfbi_all != True:
            contents.append(f'tfbi_all={self.tfbi_all}')
        contents.append(f'solved={self.solved}')
        return f'{type(self).__name__}({", ".join(contents)})'
