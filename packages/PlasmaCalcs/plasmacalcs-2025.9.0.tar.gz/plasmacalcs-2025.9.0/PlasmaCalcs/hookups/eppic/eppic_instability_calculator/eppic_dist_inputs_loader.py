"""
File Purpose: loading fluid-dependent eppic.i inputs,
from values in an EppicInstabilityCalculator.
"""
import numpy as np
import xarray as xr

from ....quantities import QuantityLoader
from ....tools import simple_property
from ....defaults import DEFAULTS


class EppicDistInputsLoader(QuantityLoader):
    '''loads fluid-dependent eppic.i inputs, from values in an EppicInstabilityCalculator.'''

    # # # DIST_INPUTS -- "DISPATCH" # # #

    # {varname: name for eppic.i file.}
    # with {x} indicating "replace with component (x, y, or z)",
    #  and {N} indicating "replace with fluid index".
    # name can be dict --> expect varname to expand into vars upon loading.
    DIST_INPUTS = {
        # specie setup & "cost" for this specie.
        'init_dist': 'init_dist{N}',
        'safe_nptotcelld': 'nptotcelld{N}',
        'part_pad': 'part_pad{N}',
        'safe_pow2_subcycle': 'subcycle{N}',
        # physical parameters
        'm': 'md{N}',
        'q': 'qd{N}',
        'n': 'n0d{N}',
        'nusn': 'coll_rate{N}',
        'coll_type': 'coll_type{N}',  # (not physical, but wanted to keep it next to coll_rate.)
        # physical parameters - probably derived / equilibrium values
        'eqperp_vtherm': 'v{x}thd{N}',
        'u_drift': 'v{x}0d{N}',
        # output-related vars
        'part_out_subcycle': 'part_out_subcycle{N}',
        'flux_out_subcycle': 'flux_out_subcycle{N}',
        'nvsqr_out_subcycle': 'nvsqr_out_subcycle{N}',
        'vdist_out_subcycle': 'vdist_out_subcycle{N}',
        'vdist_lims': {
            'vdist_min': 'pv{x}min{N}',
            'vdist_max': 'pv{x}max{N}',
        },
        'pnvx': 'pnvx{N}',
        'pnvy': 'pnvy{N}',
        'pnvz': 'pnvz{N}',
    }

    @known_var(deps=DIST_INPUTS)
    def get_dist_inputs(self):
        '''Dataset of dist-related input values which go to eppic.i, here using PlasmaCalcs datavar names.
        Named & dimensioned here with PlasmaCalcs conventions,
            e.g. uses 'vdist_min' which varies across 'component' and 'fluid' dims,
            instead of labeling pvxmin0, pvymin0, pvzmin0, pvxmin1, ..., pvzminN like in eppic.i.
        Result has keys:
            (physical, direct inputs)
                'n', 'm', 'q', 'nusn',
            (physical, derived from other params)
                'u_drift', 'eqperp_vtherm',
            (numerical, direct inputs, may be input via 'dist_vals' during __init__)
                'part_pad', 'coll_type', 'pnvx', 'pnvy', 'pnvz',
                'vdist_out_subcycle', 'part_out_subcycle', 'flux_out_subcycle', 'nvsqr_out_subcycle',
            (numerical, derived from other params)
                'safe_nptotcelld', 'safe_pow2_subcycle', 'vdist_min', 'vdist_max',

        if self.dspace_mode doesn't start with 'safe_', use 'safe_{mode}' instead.
            (this affects, e.g., safe_pow2_subcycle)
        '''
        with self.using(_cached_safe_pow2_subcycle=self('safe_pow2_subcycle')):  # [EFF] caching improves efficiency.
            return self(list(self.DIST_INPUTS), dspace_mode=self.safe_dspace_mode)


    # # # VELOCITY OUTPUTS # # #

    cls_behavior_attrs.register('vdist_nsigma', default=DEFAULTS.EPPIC.VDIST_NSIGMA)
    vdist_nsigma = simple_property('_vdist_nsigma', setdefault=lambda: DEFAULTS.EPPIC.VDIST_NSIGMA,
        doc=f'''number of standard deviations (actually: vtherm widths) to output in vdist.
        vdist pvxmin & max will be centered on u_drift, with width vdist_nsigma * vtherm.
        default: DEFAULTS.EPPIC.VDIST_NSIGMA (default: {DEFAULTS.EPPIC.VDIST_NSIGMA})''')

    @known_var(deps=['u_drift', 'eqperp_vtherm'])
    def get_vdist_lims(self):
        '''Dataset of vdist_min and vdist_max for each species and each vector component (x,y,z).
        Centered on u_drift, with width self.vdist_nsigma * self('eqperp_vtherm').
        '''
        center = self('u_drift')
        width = self('eqperp_vtherm')
        vmin = center - self.vdist_nsigma * width
        vmax = center + self.vdist_nsigma * width
        return xr.Dataset({'vdist_min': vmin, 'vdist_max': vmax})


    # # # SUBCYCLING AND NUMBER OF PARTICLES # # #

    cls_behavior_attrs.register('subcycle_safety', default=DEFAULTS.EPPIC.SUBCYCLE_SAFETY)
    subcycle_safety = simple_property('_subcycle_safety', setdefault=lambda: DEFAULTS.EPPIC.SUBCYCLE_SAFETY,
        doc='''safety factor for self('safe_pow2_subcycle'). Larger is safer. None <--> 1.
        when making eppic input deck, will use subcycle = largest 2^N <= (best possible subcycling / safety)''')
    # def get_safe_pow2_subcycle... already defined in TimescalesLoader.

    cls_behavior_attrs.register('npd_mul_cpu_cost', default=DEFAULTS.EPPIC.NPD_MUL_CPU_COST)
    npd_mul_cpu_cost = simple_property('_npd_mul_cpu_cost', setdefault=lambda: DEFAULTS.EPPIC.NPD_MUL_CPU_COST,
        doc=f'''"target cpu cost" of each subcycled species, when getting self('safe_npd_mul')
        the idea is to use npd(subcycled) = npd(unsubcycled) * npd_mul_cpu_cost * subcycling
        e.g. if dist 1 has subcycling = 32, and npd_mul_cpu_cost = 0.1,
            and dist 0 has subcycling = 1, npd=1000, then dist 1 should target npd = 3200.
        (might be lower or higher due to rounding; see npd_mul_max and npd_mul_increment.)
        default: DEFAULTS.EPPIC.NPD_MUL_CPU_COST (default: {DEFAULTS.EPPIC.NPD_MUL_CPU_COST})''')

    cls_behavior_attrs.register('npd_mul_max', default=DEFAULTS.EPPIC.NPD_MUL_MAX)
    npd_mul_max = simple_property('_npd_mul_max', setdefault=lambda: DEFAULTS.EPPIC.NPD_MUL_MAX,
        doc=f'''maximum value for self('safe_npd_mul'). None --> no maximum.
        e.g. if self.npd_mul_cpu_cost = 0.1, self.npd_mul_max = 5,
            if dist 1 has subcycling = 256, use npd_mul of 5 instead of 25.6.
        default: DEFAULTS.EPPIC.NPD_MUL_MAX (default: {DEFAULTS.EPPIC.NPD_MUL_MAX})''')

    @known_var(deps=['safe_pow2_subcycle'])
    def get_safe_npd_mul(self):
        '''npd multiplier for each fluid. Aim for "target cpu cost" for subcycled fluids.
        Target cpu cost is determined by self.npd_mul_cpu_cost * (cost of unsubcycled fluid).
        The idea is to use npd(subcycled) = npd(unsubcycled) * npd_mul_cpu_cost * subcycling.
            --> safe_npd_mul = npd_mul_cpu_cost * safe_pow2_subcycle.
        However, if this would be larger than self.npd_mul_max, use npd_mul_max instead.
        Also, if this would be less than 1, use 1 instead.
        '''
        npd_mul_cpu_cost = self.npd_mul_cpu_cost
        npd_mul_max = self.npd_mul_max
        result = npd_mul_cpu_cost * self('safe_pow2_subcycle')
        if self.npd_mul_max is not None:
            result = np.minimum(result, npd_mul_max)
        result = np.maximum(result, 1)
        return result


    # # # N PIC PER CELL # # #

    @known_var
    def get_nptotcelld0(self):
        '''nptotcelld for the unsubcycled distribution (not necessarily dist 0).
        default: DEFAULTS.EPPIC.NPTOTCELLD0
        '''
        return self.load_direct('nptotcelld0')

    cls_behavior_attrs.register('npd_rounding', default=DEFAULTS.EPPIC.NPD_ROUNDING)
    npd_rounding = simple_property('_npd_rounding', setdefault=lambda: DEFAULTS.EPPIC.NPD_ROUNDING,
        doc=f'''rounding to use for npd values. None --> no rounding (still round to nearest int)
        e.g. use 10 if you want all npd choices to be rounded to the nearest 10.
        default: DEFAULTS.EPPIC.NPD_ROUNDING (default: {DEFAULTS.EPPIC.NPD_ROUNDING})''')

    @known_var(deps=['nptotcelld0', 'safe_npd_mul'])
    def get_safe_nptotcelld(self):
        '''nptotcelld to use for each fluid.
        Usually, safe_nptotcelld = nptotcelld(the unsubcycled dist) * self('safe_npd_mul').
            internally, uses nptotcelld(unsubcycled) = self.nptotcelld0.
        Rounds to nearest int, or nearest multiple of self.npd_rounding, if non-None.
        '''
        result = self('nptotcelld0') * self('safe_npd_mul')
        if self.npd_rounding is None:
            result = np.round(result)
        else:
            result = np.round(result / self.npd_rounding) * self.npd_rounding
        return result.astype('int')
