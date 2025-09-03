"""
File Purpose: InstabilityQuantityLoader
"""
import xarray as xr

from .instability_data_tools import Pwl2FlatendFitter
from ..addon_tools import register_addon_loader
from ...dimensions import ELECTRON
from ...errors import InputError
from ...quantities import QuantityLoader
from ...tools import simple_property


### --------------------- InstabilityQuantityLoader --------------------- ###

@register_addon_loader
class InstabilityQuantityLoader(QuantityLoader):
    '''quantities related to instability analysis of data.

    for analysis of theory, consider InstabilityCalculator instead.
    '''

    # # # FINDING / CHOOSING t_turb # # #

    cls_behavior_attrs.register('t_turb', default=None)
    t_turb = simple_property('_t_turb', default=None,
        doc='''None, or time of turbulent onset. some _turb quantities tell values only at t>=t_turb.
        Can be set to a DataArray, to test multiple possibilities at once.
        Units should be self.units. Changing self.units afterwards will NOT auto-update t_turb.''')

    @known_var
    def get_t_turb(self):
        '''time of turbulent onset. Equal to self.t_turb if set; Crash if not set.
        (here always converts result to DataArray if not DataArray already.)
        '''
        result = self.t_turb
        if result is None:
            errmsg = ('cannot get t_turb until it is set, via self.t_turb=value.\n'
                      'Also consider standard self.set_t_turb_... options, e.g. set_t_turb_00()')
            raise InputError(errmsg)
        if not isinstance(result, xr.DataArray):
            result = self.record_units(xr.DataArray(result))
        return result

    @known_pattern(r'pwl2_(.+)', deps=[0])
    def get_pwl2_var(self, var, *, _match=None):
        '''get pwl2_flatend fit to var across self.snap, evaluated at self.snap.
        (fail if self.snap is not a list of multiple snaps.)
        pwl2_flatend is a piecewise linear function with 2 pieces; final piece has slope=0.

        Equivalent: fitter=self(var).pc.pwl2_flatend_fitter('t'); fitter.fit(); fitter.eval()
        '''
        here, = _match.groups()
        arr = self(here)
        fitter = Pwl2FlatendFitter(arr, 't')
        fitter.fit()
        return fitter.eval()

    @known_pattern(r't_turb_from_pwl2_(.+)', deps=[0])
    def get_t_turb_from_pwl2_var(self, var, *, _match=None):
        '''t_turb from pwl2_flatend fit to var. Might want to do self.t_turb = result.
        result depends on self.blur_sigma.

        Equivalent: fitter=self('var').pc.pwl2_flatend_fitter('t'); fitter.fit(); fitter.get_xsat()

        Suggestion: t_turb_from_pwl2_ln_std_blur_deltafrac_n
        '''
        here, = _match.groups()
        arr = self(here)
        fitter = Pwl2FlatendFitter(arr, 't')
        fitter.fit()
        return fitter.get_xsat()

    @known_var(deps=['caches_ln_std_blur_deltafrac_n'])
    def get_tturbvar00(self):
        '''var used for t_turb '00' standard: caches_ln_std_blur_deltafrac_n,
            with fluid=electron, snap=None, blur_sigma=10.
        '''
        with self.using(t_turb=None, fluid=ELECTRON, snap=None, blur_sigma=10):
            return self('caches_ln_std_blur_deltafrac_n')

    def set_t_turb_00(self):
        '''set self.t_turb & return t_turb from '00' standard: t_turb_from_pwl2_ln_std_blur_deltafrac_n,
            with fluid=electron, snap=None, blur_sigma=10.
        Drops 'fluid', 'snap', and 't' coords from result.
        (internally, uses 'caches_ln_std_blur_deltafrac_n' with t_turb=None, to save time if recomputed later.)

        (00 standard should never change, it will always mean this!)
        '''
        val = self('t_turb_from_pwl2_tturbvar00')
        val = val.drop_vars(('fluid', 'snap', 't'), errors='ignore')
        self.t_turb = val
        return val

    def set_t_turb_10(self):
        '''set self.t_turb & return t_turb from '10' standard: t_turb_from_pwl2_ln_std_blur_deltafrac_n,
        for fluid=None, fitting across all snaps, and blur_sigma=10.
        Renames 'fluid' to 'tturb_fluid' in result. Drops 'snap' and 't' coords from result.
        (internally, uses 'caches_ln_std_blur_deltafrac_n' with t_turb=None, to save time if recomputed later.)

        (10 standard should never change, it will always mean this!)
        '''
        with self.using(t_turb=None, fluid=None, snap=None, blur_sigma=10):
            val = self('t_turb_from_pwl2_caches_ln_std_blur_deltafrac_n')
        val = val.rename({'fluid': 'tturb_fluid'}).drop_vars(('snap', 't'), errors='ignore')
        self.t_turb = val
        return val


    # # # COMPUTING VALUES BEFORE / AFTER t_turb # # #

    @known_pattern(r'tturb_(.+)', deps=['t_turb', 0])
    def get_tturb_var(self, var, *, _match=None):
        '''values of var at or after t_turb. Mask all values before t_turb.
        [TODO][EFF] wasted time computing values which will later be masked...
        '''
        here, = _match.groups()
        arr = self(here)
        t_turb = self('t_turb')
        return arr.where(arr['t'] >= t_turb)

    ## commented-out for now, because it feels bad to push t_final into playing a role in the results.
    ## maybe can think of a better thing to base the t_sureturb safety factor on.
    # cls_behavior_attrs.register('sureturb_quantile', default=0.3)
    # sureturb_quantile = simple_property('_sureturb_quantile', default=0.3,
    #     doc='''fraction of (t_final - t_turb) to add to t_turb to get t_sureturb.
    #     t_turb tells when turbulence probably starts.
    #     t_sureturb tells time, after which, values are definitely in the turbulent regime.
    #         --> to compute turbulent properties consider only t > t_sureturb.
    #     Example: t_turb=10, t_final=30, sureturb_quantile=0.3 --> t_sureturb=10+0.3*(30-10) = 16.''')

    @known_var(deps=['t_turb'])
    def get_t_sureturb(self):
        '''time, after which, values are definitely in the turbulent regime.
        Currently, just returns self('t_turb').
        Eventually might implement some safety factor since t_turb might not be exact.
        '''
        return self('t_turb')

    @known_pattern(r'sureturb_(.+)', deps=['t_sureturb', 0])
    def get_sureturb_var(self, var, *, _match=None):
        '''values of var at or after t_sureturb. Mask all values before t_sureturb.
        [TODO][EFF] wasted time computing values which will later be masked...
        '''
        here, = _match.groups()
        arr = self(here)
        t_sureturb = self('t_sureturb')
        return arr.where(arr['t'] >= t_sureturb)

    cls_behavior_attrs.register('surelin_quantile', default=0.2)
    surelin_quantile = simple_property('_surelin_quantile', default=0.2,
        doc='''fraction of t_turb which tells t_surelin.
        t_turb tells when turbulence probably starts.
        t_surelin tells time before which, values are definitely in the linear regime.
            --> to compute linear properties consider only t < t_surelin.
        Example: t_turb=10, surelin_quantile=0.2 --> t_surelin=0.2*10 = 2.

        See also: surelin_min_quantile.''')

    cls_behavior_attrs.register('surelin_min_quantile', default=0.05)
    surelin_min_quantile = simple_property('_surelin_min_quantile', default=0.05,
        doc='''fraction of t_turb which tells start time of "definitely linear regime".
        Use this to avoid including startup noise when computing linear properties.

        Example: t_turb=10, surelin_min_quantile=0.05 --> t_surelin=0.05*10 = 0.5.''')

    @known_var(deps=['t_turb'])
    def get_t_surelin(self):
        '''time before which, values are definitely in the linear regime.
        self('t_turb') * self.surelin_quantile.
        '''
        return self('t_turb') * self.surelin_quantile

    @known_var(deps=['t_turb'])
    def get_t_surelin_min(self):
        '''start time of "definitely linear regime".
        self('t_turb') * self.surelin_min_quantile.
        '''
        return self('t_turb') * self.surelin_min_quantile

    @known_pattern(r'surelin_(.+)', deps=['t_surelin', 0])
    def get_surelin_var(self, var, *, _match=None):
        '''values of var between (inclusive) t_surelin_min and t_surelin. Mask all other values.
        [TODO][EFF] wasted time computing values which will later be masked...
        '''
        here, = _match.groups()
        arr = self(here)
        t_surelin = self('t_surelin')
        t_surelin_min = self('t_surelin_min')
        return arr.where((arr['t'] >= t_surelin_min) & (arr['t'] <= t_surelin))

    @known_pattern(r'turblindiff_(.+)',
                   deps=[{0: 'meant_sureturb_{group0}'}, {0: 'meant_surelin_{group0}'}])
    def get_turblindiff_var(self, var, *, _match=None):
        '''meant_sureturb_var - meant_surelin_var.
        i.e., (time-averaged value in turbulent regime) minus (time-averaged value in linear regime).

        see also: werrturblindiff_var
        '''
        here, = _match.groups()
        sureturb = self(f'meant_sureturb_{here}')
        surelin = self(f'meant_surelin_{here}')
        return sureturb - surelin

    @known_pattern(r'turblindiffwerr_(.+)',
                     deps=[{0: '(werrmeant_sureturb_{group0})_werrsub_(werrmeant_surelin_{group0})'}])
    def get_turblindiffwerr_var(self, var, *, _match=None):
        '''werrmeant_sureturb_var - werrmeant_surelin_var.
        i.e., (time-averaged value in turbulent regime) minus (time-averaged value in linear regime),
        but result is a Dataset with 'mean' and 'std' data_vars,
        with 'std' coming from  "standard" error propagation formula assuming independent errors:
            std(A - B) = sqrt(std(A)**2 + std(B)**2).

        see also: turblindiff_var
        '''
        here, = _match.groups()
        return self(f'(werrmeant_sureturb_{here})_werrsub_(werrmeant_surelin_{here})')

    @known_pattern(r'turblindivwerr_(.+)',
                    deps=[{0: '(werrmeant_sureturb_{group0})_werrdiv_(werrmeant_surelin_{group0})'}])
    def get_turblindivwerr_var(self, var, *, _match=None):
        '''werrmeant_sureturb_var / werrmeant_surelin_var.
        i.e., (time-averaged value in turbulent regime) divided by (time-averaged value in linear regime),
        but result is a Dataset with 'mean' and 'std' data_vars,
        with 'std' coming from  "standard" error propagation formula assuming independent errors.
        '''
        here, = _match.groups()
        return self(f'(werrmeant_sureturb_{here})_werrdiv_(werrmeant_surelin_{here})')


    # # # ZEROTH ORDER NEUTRAL HEATING RATES # # #
    @known_var
    def get_dTndt_turb0_s_ds(self):
        '''dataset of contributions to neutral heating rate, based on 'mean' turbulent values,
        for each fluid (in self.fluid), due to collisions.

        Assumes u_n==0, and does not check.

        result has keys:
            'dTndt_u2': 2 m_n / (m_n + m_s) * nuns * [(m_s / (3 kB)) |u_s|^2]
            'dTndt_T': 2 m_n / (m_n + m_s) * nuns * [(T_s - T_n)]

        Except, use werrmeant_sureturb_u instead of u_s,
            and werrmeant_sureturb_T instead of T_s

        For more accurate computation, consider self('werrmeant_sureturb_dTndt_s')
        '''
        raise NotImplementedError('[TODO] -- maybe. Might not be needed though.')
