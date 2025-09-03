"""
File Purpose: calculating plasma drifts, e.g. hall, pederson.
"""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .plasma_parameters import PlasmaParametersLoader
from ..errors import FormulaMissingError
from ..plotting import PlotSettings
from ..tools import (
    simple_property,
    xarray_sum, xarray_sel,
)


class PlasmaDriftsLoader(PlasmaParametersLoader):
    '''plasma drifts.'''
    # # # GET DRIFTS # # #
    @known_var(deps=['skappa', 'E_un0_cross_B', 'mod_B'])
    def get_u_hall(self, *, _E=None, _B=None):
        '''Hall drift velocity. u_hall = (kappa**2 / (1 + kappa**2)) * (E_un0 x B) / |B|**2,
        where kappa is the magnetization parameter, kappa = gyrof / nusn.
        [EFF] for efficiency, can provide E and/or B, if already known.
        '''
        skappa = self('skappa')  # signed kappa; skappa<0 when q<0.
        E_cross_B = self('E_un0_cross_B', _E=_E, _B=_B)
        mod_B = self('mod_B', _B=_B)
        return ((skappa**2 / (1 + skappa**2)) / mod_B**2) * E_cross_B 

    @known_var(deps=['skappa', 'E_un0', 'mod_B'], aliases=['u_ped'])
    def get_u_pederson(self, *, _E=None, _B=None):
        '''Pederson drift velocity. u_pederson = (skappa / (1 + skappa**2)) * E_un0 / |B|,
        where skappa is the (signed) magnetization parameter, skappa = q * |B| / (m * nusn).
        [EFF] for efficiency, can provide E and/or B, if already known.
        '''
        skappa = self('skappa')  # signed kappa; skappa<0 when q<0.
        E = self('E_un0') if _E is None else _E
        mod_B = self('mod_B', _B=_B)
        return ((skappa / (1 + skappa**2)) / mod_B) * E 

    @known_var(deps=['skappa', 'E_un0_dot_B', 'B', 'mod_B'])
    def get_u_EdotB(self, *, _E=None, _B=None):
        '''EdotB drift velocity. u_EdotB = (skappa**3 / (1 + skappa**2)) * (E_un0 dot B) B / |B|^3
        (Commonly neglected, but comes from the same physical equation as hall & pederson drifts;
        from solving equilibrium momentum equation for u, when neglecting all derivatives.)
        [EFF] for efficiency, can provide E and/or B, if already known.
        '''
        skappa = self('skappa')
        E_dot_B = self('E_un0_dot_B', _E=_E, _B=_B)
        B = self('B') if _B is None else _B
        mod_B = self('mod_B', _B=_B)
        return ((skappa**3 / (1 + skappa**2)) * B / mod_B**3) * E_dot_B

    @known_var(deps=['u_hall', 'u_pederson', 'u_EdotB'], aliases=['u_eqcol', 'eqcol_u'])
    def get_u_drift(self):
        '''equilibrium velocity; solution to the momentum equation with collisions,
        assuming zero acceleration and zero spatial gradients.
        u_drift = u_hall + u_pederson + u_EdotB.
        '''
        # [EFF] calculate E & B first, to avoid recalculating them 3 times.
        #   will need all components of E & B, even if len(self.component)==1,
        #   because internally will calculate E cross B AND E dot B.
        with self.using(component=None):  # all components
            E = self('E_un0')
            B = self('B')
        result = self('u_hall', _E=E, _B=B) + self('u_pederson', _E=E, _B=B) + self('u_EdotB', _E=E, _B=B)
        if self.component != self.components:
            # if self.component is not None, then we need to select the right component(s).
            result = xarray_sel(result, component=self.component)
        return result
        # inefficient way: recalculates E & B, each time:
        # return self('u_hall') + self('u_pederson') + self('u_EdotB')

    @known_var(deps=['E_un0_perpmod_B', 'mod_B'])
    def get_EBspeed(self):
        '''speed determined from E_un0 and B: |E_un0 perp to B| / |B|.'''
        # [TODO] make a different variable for full |E_un0| (including parallel component)?
        # (the E dot B term of u_drift scales with skappa^3/(1+skappa^2) though,
        # which is not bounded between 0 and 1 like hall and pederson skappa-related coefficients...)
        return self('E_un0_perpmod_B') / self('mod_B')

    @known_var(deps=['J_perpmod_B', 'ne', 'abs_qe'])
    def get_JBspeed(self):
        '''speed determined from J perp to B, and ne: |J_perp to B| / (ne * |qe|).'''
        # [TODO] make a different variable for full |J| (including parallel component)?
        return self('J_perpmod_B') / (self('ne') * self('abs_qe'))

    # # # GET KAPPA & NUSN FROM VELOCITIES (assuming velocities are from drifts) # # #
    # note - example plotting code for these quantities can be found in eppic_moments.py

    @known_pattern(r'skappa_from_(means_|)(.*_)?momExB', ignores_dims=['component'],
                   deps=[{1: lambda groups: 'u' if groups[1] is None else groups[1][:-len('_')]},
                        'u_neutral', 'u_cross_B', 'mod_B', 'E_cross_B',])
    def get_skappa_from_momExB(self, var, *, _match=None):
        '''signed kappa (magnetization parameter) that statisfies momentum equation in the E x B direction.
        'skappa_from_{means_}{u_}momExB'
            E.g. 'skappa_from_means_momExB', 'skappa_from_momExB', 'skappa_from_means_moment1_momExB'
            {means_} = 'means_' or ''.
                if 'means_', take means of vars: 'u', 'u_neutral', 'mod_B', 'E_cross_B', 'u_cross_B'
            {u_} = '' or any other var then '_'.
                if provided, use this var instead of 'u' for velocity.  (Doesn't affect "u_neutral" though.)
                E.g. eppic calculator might use 'moment1' here, as in 'skappa_from_moment1_momExB'.

        Algebraic solution:
            momentum equation, rearranged using skappa = q * |B| / (m * nusn):
                0 = q (E + u x B) - m * nusn * (u - u_neutral)
                0 = skappa (E + u x B) - |B| (u - u_neutral)
            dotting with E x B:
                0 = skappa [(u x B) dot (E x B)] - |B| [(u - u_neutral) dot (E x B)]
                --> skappa = |B| [(u - u_neutral) dot (E x B)] / [(u x B) dot (E x B)]
        '''
        # Note, the denominator can be "simplified" further (but is not in this method) via:
        # (u x B) dot (E x B) = (u dot B) (E dot B) - (u dot E) |B|^2
        means, uvar = _match.groups()
        mean = 'mean_' if means else ''   # default ''
        ustr = uvar[:-len('_')] if uvar else 'u'
        with self.using(component=None):  # make sure to get all components of vectors.
            u = self(f'{mean}{ustr}')
            u_n = self(f'{mean}u_neutral')
            mod_B = self(f'{mean}mod_B')
            E_cross_B = self(f'{mean}E_cross_B')
            u_cross_B = self(f'{mean}{ustr}_cross_B')
            skappa = mod_B * self.dot(u - u_n, E_cross_B) / self.dot(u_cross_B, E_cross_B)
        return skappa

    @known_pattern(r'skappa_from_(means_|)(.*_)?momE', ignores_dims=['component'],
                   deps=[{1: lambda groups: 'u' if groups[1] is None else groups[1][:-len('_')]},
                        'u_neutral', 'E', 'mod_B', 'E_cross_B',])
    def get_skappa_from_momE(self, var, *, _match=None):
        '''signed kappa (magnetization parameter) that statisfies momentum equation in the E direction.
        'skappa_from_{means_}{u_}momE'
            E.g. 'skappa_from_means_momE', 'skappa_from_momE', 'skappa_from_means_moment1_momE'
            {means_} = 'means_' or ''.
                if 'means_', take means of vars: 'u', 'u_neutral', 'mod_E', 'mod_B', 'E', 'E_cross_B'
            {u_} = '' or any other var then '_'.
                if provided, use this var instead of 'u' for velocity.  (Doesn't affect "u_neutral" though.)
                E.g. eppic calculator might use 'moment1' here, as in 'skappa_from_moment1_momE'.

        Algebraic solution:
            momentum equation, rearranged using skappa = q * |B| / (m * nusn):
                0 = q (E + u x B) - m * nusn * (u - u_neutral)
                0 = skappa (E + u x B) - |B| (u - u_neutral)
            dotting with E:
                0 = skappa (|E|^2 + (u x B) dot E) - |B| (u - u_neutral) dot E    # note uxB.E == BxE.u == -ExB.u
                --> skappa = |B| (u - u_neutral) dot E / (|E|^2 - u dot (E x B))

        Note: results untrustworthy when kappa >> 1, since that involves dividing by a value close to 0.
        '''
        means, uvar = _match.groups()
        mean = 'mean_' if means else ''
        ustr = uvar[:-len('_')] if uvar else 'u'
        with self.using(component=None):  # make sure to get all components of vectors.
            u = self(f'{mean}{ustr}')
            u_n = self(f'{mean}u_neutral')
            E = self(f'{mean}E')
            mod_B = self(f'{mean}mod_B')
            E_cross_B = self(f'{mean}E_cross_B')
            mod_E_squared = self('mean_mod_E')**2 if means else self.dot(E,E)  # [EFF] use known E if not taking means.
            skappa = mod_B * self.dot(u - u_n, E) / (mod_E_squared - self.dot(u, E_cross_B))
        return skappa

    # [TODO] skappa from momB which gets skappa that satisfies momentum equation in the B direction.
    # (it is undetermined when E dot B == 0 == u dot B, so it's not useful if B perp to 2D simulation plane.)

    @known_pattern(r'skappa_from_(means_|)(.*_)?hall', ignores_dims=['component'],
                   deps=[{1: lambda groups: 'u' if groups[1] is None else groups[1][:-len('_')]},
                        'mod_B', 'E_cross_B', 'q'])
    def get_skappa_from_hall(self, var, *, _match=None):
        '''signed kappa (magnetization parameter) that statisfies u_hall = u, in the E x B direction.
        'skappa_from_{means_}{u_}hall'
            E.g. 'skappa_from_means_hall', 'skappa_from_hall', 'skappa_from_means_moment1_hall'
            {means_} = 'means_' or ''.
                if 'means_', take means of vars: 'u', 'u_neutral', 'mod_B', 'E_cross_B'
            {u_} = '' or any other var then '_'.
                if provided, use this var instead of 'u' for velocity.  (Doesn't affect "u_neutral" though.)
                E.g. eppic calculator might use 'moment1' here, as in 'skappa_from_moment1_hall'.

        Algebraic solution:
            formula for u_hall (from solving momentum equation for u in the E x B direction):
                u_hall = (kappa**2 / (1 + kappa**2)) * (E x B) / |B|**2
            solving for kappa**2, assuming u instead of u_hall, yields:
                (u dot (E x B)) == (kappa**2 / (1 + kappa**2)) * (|E x B|**2 / |B|**2)
                A + A * kappa**2 - kappa**2 == 0, where A = (u dot (E x B)) / (|E x B|**2 / |B|**2)
                kappa**2 = A / (1 - A)
                --> skappa = +- sqrt(A / (1 - A)),
            There are two solutions; return solution with the same sign as self('q') (i.e. fluid's charge)
        '''
        means, uvar = _match.groups()
        mean = 'mean_' if means else ''
        ustr = uvar[:-len('_')] if uvar else 'u'
        u_n = self(f'{mean}u_neutral')
        if np.any(u_n != 0):  # [TODO] account for nonzero u_neutral in this method.
            raise NotImplementedError(f'{var!r} when u_neutral != 0.')
        with self.using(component=None):  # make sure to get all components of vectors.
            u = self(f'{mean}{ustr}')
            mod_B = self(f'{mean}mod_B')
            E_cross_B = self(f'{mean}E_cross_B')
            A = self.dot(u, E_cross_B) / (self.dot(E_cross_B, E_cross_B) / mod_B**2)
            sign = np.sign(self('q'))
            skappa = sign * (A / (1 - A))**0.5
        return skappa

    @known_pattern(r'skappa_from_(means_|)(.*_)?pederson', ignores_dims=['component'],
                   deps=[{1: lambda groups: 'u' if groups[1] is None else groups[1][:-len('_')]},
                        'u_neutral', 'mod_B', 'E', 'q'])
    def get_skappa_from_pederson(self, var, *, _match=None):
        '''signed kappa (magnetization parameter) that statisfies u_pederson = u, in the E direction.
        'skappa_from_{means_}{u_}pederson'
            E.g. 'skappa_from_means_pederson', 'skappa_from_pederson', 'skappa_from_means_moment1_pederson'
            {means_} = 'means_' or ''.
                if 'means_', take means of vars: 'u', 'u_neutral', 'mod_B', 'E', 'mod_E',
            {u_} = '' or any other var then '_'.
                if provided, use this var instead of 'u' for velocity.  (Doesn't affect "u_neutral" though.)
                E.g. eppic calculator might use 'moment1' here, as in 'skappa_from_moment1_pederson'.

        Algebraic solution:
            formula for u_pederson (from solving momentum equation for u in the E direction):
                u_pederson = (skappa / (1 + skappa**2)) * E / |B|
            solving for skappa, assuming u instead of u_pederson, yields:
                (u dot E) == (skappa / (1 + skappa**2)) * (|E|**2 / |B|)
                A + A * skappa**2 - skappa == 0, where A = (u dot E) / (|E|**2 / |B|)
                skappa = (1 +- sqrt((-1)^2 - 4 * A * A)) / (2 * A),
            There are two solutions; the correct choice can be determined by using the momentum equation;
                the correct choice for the +- sign turns out to be: -sign(q) where q = self('q') == fluid's charge.

        Note: results untrustworthy when kappa >> 1, since that involves dividing by a value close to 0.
        '''
        means, uvar = _match.groups()
        mean = 'mean_' if means else ''
        ustr = uvar[:-len('_')] if uvar else 'u'
        u_n = self(f'{mean}u_neutral')
        if np.any(u_n != 0):  # [TODO] account for nonzero u_neutral in this method.
            raise NotImplementedError(f'{var!r} when u_neutral != 0.')
        with self.using(component=None):  # make sure to get all components of vectors.
            u = self(f'{mean}{ustr}')
            mod_B = self(f'{mean}mod_B')
            E = self(f'{mean}E')
            mod_E_squared = self('mean_mod_E')**2 if means else self.dot(E,E)  # [EFF] use known E if not taking means.
            A = self.dot(u, E) / (mod_E_squared / mod_B)
            qsign = np.sign(self('q'))
            skappa = (1 - qsign * (1 - 4 * A**2)**0.5) / (2 * A)
        return skappa

    @known_pattern(r'nusn_from_(means_|)(.*_)?(momExB|momE|hall|pederson)', ignores_dims=['component'],
                   deps=['sgyrof', {(0,1,2): 'skappa_from_{group0}{group1}{group2}'}])
    def get_nusn_from_drift(self, var, *, _match=None):
        '''nusn, calculated by assuming u satisfies momentum equation to zeroth order.
        There are various options for how to solve for nusn, as explained below (see {drift}).
        All solutions use nusn = sgyrof / skappa, where skappa is determined via
            skappa = self('skappa'+var[len('nusn'):]).
        E.g. 'nusn_from_means_momExB' --> use skappa = self('skappa_from_means_momExB').

        The description below helps explain the various options.

        'nusn_from_{means_}{u_}{drift}'
            E.g. 'nusn_from_means_momExB', 'nusn_from_hall', 'nusn_from_means_moment1_momB'
            {means_} = 'means_' or ''.
                if 'means_', take means of vars: 'sgyrof', any vars relevant to the chosen {drift} option.
            {u_} = '' or any other var then '_'.
                if provided, use this var instead of 'u' for velocity.  (Doesn't affect "u_neutral" though.)
            {drift} = 'momExB', 'momE', 'hall', or 'pederson'
                indicates how to solve for nusn. Use the similarly-named var when getting skappa.
                'momExB' --> get skappa from the momentum equation in the E x B direction.
                'momE' --> get skappa from the momentum equation in the E direction.
                'hall' --> get skappa from u_hall = u, in the E x B direction.
                'pederson' --> get skappa from u_pederson = u, in the E direction.
        '''
        means, uvar, drift = _match.groups()
        if uvar is None: uvar = ''
        kvar = f'skappa_from_{means}{uvar}{drift}'
        skappa = self(kvar)
        return self('sgyrof') / skappa

    def plot_check_nusn_from_drift(self, *, u='u', drift='momExB', cycle1=dict(ls=['-', '--', '-.', ':']),
                                   means=True, log=True, **kw_timelines):
        '''plots PlasmaCalcs.timelines() for comparing nusn to nusn inferred from drifts.
        This is meant to be used as a quick check. Use this code as an example if you need more low-level control.

        u: str or iterable of strs
            var to use for velocity. Might want something else, e.g. EppicCalculator might use u='moment1'
            iterable of strs --> get multiple.
        drift: str or iterable of strs
            tells the way to infer skappa, and thus nusn. Options: 'momExB', 'momE', 'hall', 'pederson'.
            iterable of strs --> get multiple.
        cycle1: dict of lists
            parameters to use for matplotlib plotting if getting multiple u or drift.
        means: bool
            whether to take means of lower-level vars while getting skappa.
            (e.g. use 'skappa_from_means_momExB' instead of 'skappa_from_momExB', if True.)
        log: bool
            whether to take log10 of the ratios (nusn_from_drift / nusn) before plotting.

        returns plt.gcf().
        '''
        mean = 'means_' if means else ''
        log10 = 'log10_' if log else ''
        if isinstance(u, str):
            u = [u]
        if isinstance(drift, str):
            drift = [drift]
        Nlines = len(u) * len(drift)
        Lcycle = None if len(cycle1)==0 else min(len(val) for val in cycle1.values())
        if (Lcycle is not None) and (Nlines > Lcycle):
            print(f'warning, too many timelines ({Nlines}) compared to style cycle length ({Lcycle}).')
        kw_timelines['ybounds'] = kw_timelines.pop('ybounds', PlotSettings.get_default('ybounds'))
        i = 0
        for uvar in u:
            for driftvar in drift:
                # calculation
                arr = self(f'{log10}(mean_(nusn_from_{mean}{uvar}_{driftvar}/nusn))')
                # plotting
                style = {k: v[i] for k,v in cycle1.items()}
                tls = arr.pc.timelines(label=f'({uvar}_{driftvar})', **style, **kw_timelines)
                # bookkeeping
                kw_timelines['ybounds'] = plt.ylim()  # ensure later timelines' ylims are big enough to show all timelines.
                i += 1
        # plot formatting
        plt.ylabel(f'{log10}(nusn_from_drift / nusn)')
        plt.title('check nusn from drift' if getattr(self, 'title', None) is None else self.title)

        return plt.gcf()

    # # # ELECTRIC FIELD FROM DRIFTS # # #
    @known_var(deps=['E0S1', 'E0S2', 'mod_B'])
    def get_eta0_J(self, *, _E0S1=None, _E0S2=None):
        '''E0_perp_B = eta0_J * J_perp_B + ..., where eta0_J = E0S1 * |B| / (E0S1^2 + E0S2^2). note: 
        see help(self.get_E0_un0_perpB) for more details.

        [EFF] for efficiency, can provide _E0S1 and/or _E0S2 if known.
        '''
        E0S1 = self('E0S1') if _E0S1 is None else _E0S1
        E0S2 = self('E0S2') if _E0S2 is None else _E0S2
        return E0S1 * self('mod_B') / (E0S1**2 + E0S2**2)

    @known_var(deps=['E0S1', 'E0S2', 'mod_B'])
    def get_eta0_hall(self, *, _E0S1=None, _E0S2=None):
        '''E0_perp_B = eta0_hall J x Bhat + ..., where eta0_hall = - E0S2 * |B| / (E0S1^2 + E0S2^2)
        see help(self.get_E0_un0_perpB) for more details.

        [EFF] for efficiency, can provide _E0S1 and/or _E0S2 if known.
        '''
        E0S1 = self('E0S1') if _E0S1 is None else _E0S1
        E0S2 = self('E0S2') if _E0S2 is None else _E0S2
        return -E0S2 * self('mod_B') / (E0S1**2 + E0S2**2)

    @known_var(deps=['q', 'n', 'skappa'], ignores_dims=['fluid'])
    def get_E0S1(self, *, _skappa=None, _n=None):
        '''E0S1 = sum_s (qs ns skappa_s / (1 + skappa_s^2)),
        summed across all charged fluids (from self.fluids).
        see help(self.get_E0_un0_perpB) for more details.

        [EFF] for efficiency, can provide _skappa and/or _n if known.
        '''
        with self.using(fluid=self.fluids.charged()):
            skappa = self('skappa') if _skappa is None else _skappa
            n = self('n') if _n is None else _n
            q = self('q')
        summand = q * n * skappa / (1 + skappa**2)
        return xarray_sum(summand, dim='fluid')

    @known_var(deps=['q', 'n', 'skappa'], ignores_dims=['fluid'])
    def get_E0S2(self, *, _skappa=None, _n=None):
        '''E0S2 = sum_s (qs ns skappa_s^2/ (1 + skappa_s^2)),
        summed across all charged fluids (from self.fluids).
        see help(self.get_E0_un0_perpB) for more details.

        [EFF] for efficiency, can provide _skappa and/or _n if known.
        '''
        with self.using(fluid=self.fluids.charged()):
            skappa = self('skappa') if _skappa is None else _skappa
            n = self('n') if _n is None else _n
            q = self('q')
        skappa2 = skappa**2
        summand = q * n * skappa2 / (1 + skappa2)
        return xarray_sum(summand, dim='fluid')

    @known_var(deps=['q', 'n', 'skappa'], ignores_dims=['fluid'])
    def get_E0S1_and_S2(self):
        '''dataset containing 'E0S1' and 'E0S2'. Equivalent to self(['E0S1', 'E0S2']),
        but more efficient (only computes skappa and n one time).
        E0S1 = sum_s (qs ns skappa_s / (1 + skappa_s^2))
        E0S2 = sum_s (qs ns skappa_s^2/ (1 + skappa_s^2))
        '''
        with self.using(fluid=self.fluids.charged()):
            skappa = self('skappa')
            n = self('n')
        return self(['E0S1', 'E0S2'], _skappa=skappa, _n=n)

    @known_var(deps=['eta0_J', 'J'])
    def get_E0_etaJ_perpB(self, *, _E0S1=None, _E0S2=None):
        '''E0_perp_B = E0_etaJ_perpB + ..., where E0_etaJ_perpB = eta0_J * J_perp_B.
        see help(self.get_E0_un0_perpB_fromJ) for more details.
        '''
        eta0_J = self('eta0_J', _E0S1=_E0S1, _E0S2=_E0S2)
        J = self('J_perp_B')
        return eta0_J * J

    @known_var(deps=['eta0_hall', 'J_cross_hat_B'])
    def get_E0_hall(self, *, _E0S1=None, _E0S2=None):
        '''E0_perp_B = E0_hall + ..., where E0_hall = eta0_hall * J x Bhat.
        see help(self.get_E0_un0_perpB) for more details.
        '''
        eta0_hall = self('eta0_hall', _E0S1=_E0S1, _E0S2=_E0S2)
        J_cross_Bhat = self('J_cross_hat_B')
        return eta0_hall * J_cross_Bhat

    @known_var(deps=['E0_etaJ_perpB', 'E0_hall'])
    def get_E0_un0_perpB(self):
        '''E0_un0_perpB = E0_etaJ_perpB + E0_hall
        == eta0_J * J_perp_B + eta0_hall * J x Bhat
        == (E0S1 |B| J_perp_B + E0S2 B cross J) / (E0S1^2 + E0S2^2), where
            E0S1 = sum_s (qs ns skappa_s / (1 + skappa_s^2)),
            E0S2 = sum_s (qs ns skappa_s^2/ (1 + skappa_s^2)),

        This is the electric field in the un=0 frame of reference, assuming:
            - zeroth order equilibrium velocities from multifluid equations,
            - including only collisions with neutrals,
            - considering only E (& J) perp to B; ignoring E0 (& J) parallel to B.
        '''
        E0S1_and_S2 = self('E0S1_and_S2')
        E0S1 = E0S1_and_S2['E0S1']
        E0S2 = E0S1_and_S2['E0S2']
        E0_etaJ = self('E0_etaJ_perpB', _E0S1=E0S1, _E0S2=E0S2)
        E0_hall = self('E0_hall', _E0S1=E0S1, _E0S2=E0S2)
        return E0_etaJ + E0_hall

    @known_var(aliases=['E0_un0_perpmagB'], deps=['mod_B', 'J_perpmod_B', 'E0S1', 'E0S2'])
    def get_E0_un0_perpmodB(self):
        '''E0_un0_perpmodB = |E0_un0_perpB|.
        Should be equivalent to self('mod_E0_un0_perpB'), aside from rounding errors.
        [EFF] the method here uses an algebraic simplification of the E0_un0_perpB formula:
            E0_un0_perpB == (E0S1 |B| J_perp_B + E0S2 B cross J) / (E0S1^2 + E0S2^2)
            --> (do some algebra, and utilizing J_perp_B dot B = 0) -->
            E0_un0_perpmodB = (|B| |J_perp_B|) / sqrt(E0S1^2 + E0S2^2)
        '''
        E0S1_and_S2 = self('E0S1_and_S2')
        E0S1 = E0S1_and_S2['E0S1']
        E0S2 = E0S1_and_S2['E0S2']
        mod_B = self('mod_B')
        mod_J = self('J_perpmod_B')
        return (mod_B * mod_J) / (E0S1**2 + E0S2**2)**0.5

    @known_var(aliases=['E0_un0_perpmagB_min'], deps=['mod_B', 'J_perpmod_B', 'nq'], ignores_dims=['fluid'])
    def get_E0_un0_perpmodB_min(self):
        '''E0_un0_perpmodB_min = minimum possible value of |E0_un0_perpB|, at each point.
            E0_un0_perpmodB_min = (1/sqrt(2)) * |B| |J_perp_B| / (ne |qe|)

        Regardless of kappa (& nusn) values for electrons and ions, will always have:
            E0_un0_perpmodB >= E0_un0_perpmodB_min.

        Logic which proves this fact (below, using "K" as shorthand for "skappa"):
            E0_un0_perpmodB has sqrt(E0S1^2 + E0S2^2) in the denominator;
            --> when sqrt(E0S1^2 + E0S2^2) is largest, E0_un0_perpmodB will be smallest.
            sqrt(E0S1^2 + E0S2^2) is largest when |E0S1| and |E0S2| are both largest.
            (1)  |E0S1| <= sum_s (|qs| ns |Ks| / (1 + Ks^2))
            (2)  |E0S2| <= sum_s (qs ns Ks^2 / (1 + Ks^2))
            For ANY real K, the relevant quantities are bounded by:
                (i)   0 < |K| / (1 + K^2) <= 1/2
                (ii)  0 < K^2 / (1 + K^2) < 1
                which can be readily shown using introductory calculus:
                    |K|/(1+K^2) has local extrema (derivative=0) only at K=1, where |K|/(1+K^2)=1/2;
                        it tends to 0 when K->0; and it tends to 0 when K->inf.
                    K^2/(1+K^2) has local extrema (derivative=0) only at K=0, where it equals 0;
                        it tends to 0 when K->0; and it tends to 1 when K->inf.
            Applying (i) to expression (1) above yields:
                |E0S1| <= sum_s |qs| ns * 1/2
                Utilizing quasineutrality (sum_s qs ns = 0) and qe < 0 and qi > 0, provides:
                    sum_s |qs| ns = ne |qe| + sum_i ni qi = 2 ne |qe|
                --> |E0S1| <= ne |qe|
            Meanwhile for expression (2), note that because qe < 0 and qi > 0,
                ne qe (Ke^2 / (1 + Ke^2)) has opposite the sign as sum_i ni qi Ki^2 / (1 + Ki^2),
                so the largest possible |E0S1| occurs when one of those two terms is as small as possible.
                Applying (ii) to each term, and quasineutrality to the second term, yields:
                    |ne qe (Ke^2 / (1 + Ke^2))| < ne |qe|
                    |sum_i ni qi Ki^2 / (1 + Ki^2)| < sum_i ni qi = ne |qe|
                --> |E0S2| < ne |qe|
            Combining yields:
                sqrt(E0S1^2 + E0S2^2) < sqrt(2) ne |qe|
            Thus, we always have:
                (|B| |J_perp_B|) / sqrt(E0S1^2 + E0S2^2) >= (|B| |J_perp_B|) / (sqrt(2) * ne |qe|)
                i.e.  E0_un0_perpmodB >= E0_un0_perpmodB_min.
        '''
        mod_B = self('mod_B')
        mod_J = self('J_perpmod_B')
        nqe = self('abs_nq', fluid=self.fluids.get_electron())
        if hasattr(nqe, 'drop_vars'):
            nqe = nqe.drop_vars('fluid', errors='ignore')
        return (mod_B * mod_J) / (np.sqrt(2) * nqe)

    @known_var(aliases=['E0_un0_perpmagB_simple'], deps=['mod_B', 'J_perpmod_B', 'nq'], ignores_dims=['fluid'])
    def get_E0_un0_perpmodB_simple(self):
        '''E0_un0_perpmodB_simple = simple estimate of |E0_un0_perpB|, at each point.
            E0_un0_perpmodB_simple = (|B| |J_perp_B|) / (ne |qe|)

        This is a simple estimate of |E0_un0_perpB|, accurate when kappae>>1 and kappai<<1.
        '''
        mod_B = self('mod_B')
        mod_J = self('J_perpmod_B')
        nqe = self('abs_nq', fluid=self.fluids.get_electron())
        if hasattr(nqe, 'drop_vars'):
            nqe = nqe.drop_vars('fluid', errors='ignore')
        return (mod_B * mod_J) / nqe

    # # # E_un0 mode # # #
    cls_behavior_attrs.register('E_un0_mode', default=None)
    _VALID_E_UN0_MODES = (None, 'un=u', 'un=0', 'E0_perpB', 'E0_perpmodB', 'E0_perpmodB_min')
    E_un0_mode = simple_property('_E_un0_mode', default=None, validate_from='_VALID_E_UN0_MODES',
        doc='''mode for calculating E_un0, the electric field in the neutral frame, where u_n=0.
        None, 'un=u', 'un=0', 'E0_perpB', 'E0_perpmodB', or 'E0_perpmodB_min'.
        None --> E_un0 = E + u_n x B. (i.e., E & u_n in "lab frame" then transform to u_n=0 frame.)
        'un=u' --> E_un0 = E + u x B. (i.e., assume un==u; transform to the u=0 frame.)
                    [EFF] if self.has_var('E_u0'), use E_un0 = self('E_u0') directly, without getting u;
                        assumes self('E_u0') provides "E without the u x B contribution".
                        If E_u0 not available, this mode requires 'u' to not vary with fluid.
        'un=0' --> E_un0 = E. (i.e., assume un==0 already; no need to shift frames.)
        'E0_perpB' --> E_un0 = E0_un0_perpB. (i.e., E perp to B in u_n=0 frame,
                    assuming zeroth order equilibrium velocities from multifluid equations,
                    including only collisions with neutrals,
                    and considering only E (& J) perp to B; ignoring E0 (& J) parallel to B.)
        'E0_perpmodB' --> |E_un0 perp to B| = E0_un0_perpmodB (== |E0_un0_perpB|). E_un0 = E0_un0_perpB.
                    [EFF] equivalent to using E0_perpB, except that, when getting |E_un0 perp to B|,
                    will use the more efficient formula for E0_un0_perpmodB.
        'E0_perpmodB_min' --> |E_un0 perp to B| = E0_un0_perpmodB_min. E_un0 = crash; cannot get E_un0 directly.
                    (i.e., minimum possible value of |E_un0 perp to B|, regardless of collision frequencies;
                    E0_un0_perpmodB_min = (1/sqrt(2)) * |B| |J_perp_B| / (ne |qe|).
                    See help(self.get_E0_un0_perpmodB_min) for details.)''')

    # some (but not all) of the E_un0_type options based on E_un0_mode.
    #   the types not included here are those with a more complicated dependency
    #   e.g. when mode == 'un=u' we need to check self.has_var('E_u0').
    _E_UN0_MODE_TO_TYPE = {
        None: 'E+unxB',
        'un=0': 'E',
        'E0_perpB': 'E0_perpB',
        'E0_perpmodB': 'E0_perpB',
        'E0_perpmodB_min': 'nan',  # can't get E_un0 directly; will crash.
    }

    @known_var
    def get_E_un0_type(self):
        '''string telling method that will be used to get E_un0. Based on self.E_un0_mode.
        possible results:
            'nan' <--> will crash. (e.g. this occurs if E_un0_mode = 'E0_perpmodB_min')
            'E+unxB' <--> self('E') + self('u_neutral_cross_B')
            'E_u0' <--> self('E_u0')
            'E+uxB' <--> self('E') + self('u_cross_B')
            'E' <--> self('E')
            'E0_perpB' <--> self('E0_un0_perpB')
        '''
        mode = self.E_un0_mode
        if mode in self._E_UN0_MODE_TO_TYPE:  # handles mode = None, 'un=0', 'E0_perpB', 'E0_perpmodB', 'E0_perpmodB_min'.
            result = self._E_UN0_MODE_TO_TYPE[mode]  # possible results = 'E+unxB', 'E', 'E0_perpB', 'nan'
        elif mode == 'un=u':
            if self.has_var('E_u0'):
                result = 'E_u0'
            else:
                result = 'E+uxB'
        else:
            result = 'nan'  # invalid E_un0 mode; should be prevented by E_un0 setter.
        if result == 'nan':
            self._handle_typevar_nan(errmsg=f"E_un0_type, when E_un0_mode=({mode!r}).")
        return xr.DataArray(result)

    _E_UN0_TYPE_TO_DEPS = {'E+unxB': ['E', 'u_neutral_cross_B'],
                           'E_u0': ['E_u0'],
                           'E+uxB': ['E', 'u_cross_B'],
                           'E': ['E'],
                           'E0_perpB': ['E0_un0_perpB']}

    @known_var(value_deps=[('E_un0_type', '_E_UN0_TYPE_TO_DEPS')])
    def get_E_un0(self):
        '''E_un0 = electric field in the neutral frame, where u_n=0.
        Result depends on self.E_un0_mode; see help(type(self).E_un0_mode) for details.
        '''
        kind = self('E_un0_type').item()
        if kind == 'nan':
            if self.E_un0_mode == 'E0_perpmodB_min':
                errmsg = ('E_un0 cannot be directly calculated when E_un0_mode="E0_perpmodB_min";\n'
                            'use a different E_un0_mode or get E_un0_perpmod_B instead.')
                raise FormulaMissingError(errmsg)
            else:
                raise LoadingNotImplementedError('unknown error when getting self.E_un0')
        elif kind == 'E+unxB':
            # [EFF] if un==0 just return E, without adding un x B.
            un = self('u_neutral', component=None)
            result = self('E')
            if np.any(un != 0):
                result = result + self('u_neutral_cross_B', _u_neutral=un)
        elif kind == 'E_u0':
            return self('E_u0')
        elif kind == 'E+uxB':
            # [EFF] if u==0 just return E, without adding u x B.
            u = self('u', component=None)
            result = self('E')
            if np.any(u != 0):
                result = result + self('u_cross_B', _u=u)
        elif kind == 'E':
            result = self('E')
        else:
            assert kind == 'E0_perpB', f'invalid E_un0_type ({kind!r}).'
            result = self('E0_un0_perpB')
        return result

    _E_UN0_MODE_TO_PERPMOD_B_DEPS = {'E0_perpmodB': 'E0_un0_perpmodB',
                                     'E0_perpmodB_min': 'E0_un0_perpmodB_min',
                                     '__default__': ['E_un0', 'B']}

    @known_var(aliases=['E_un0_perpmag_B'],
               attr_deps=[('E_un0_mode', '_E_UN0_MODE_TO_PERPMOD_B_DEPS')])
    def get_E_un0_perpmod_B(self, **kw_perpmod):
        '''E_un0_perpmod_B == |E_un0 perp to B| == magnitude of E, perp to B, in u_neutral=0 frame.
        This is usually equivalent to using self.magnitude(self.take_perp_to(B, E_un0)),
            but if E_un0_mode = 'E0_perpmodB' will use more efficient method (self('E0_un0_perpmodB')),
            and if E_un0_mode = 'E0_perpmodB_min' will use different method (self('E0_un0_perpmodB_min')).

        kwargs are passed to self.get_perpmod, if applicable.
        '''
        mode = self.E_un0_mode
        if mode == 'E0_perpmodB':
            return self('E0_un0_perpmodB')
        elif mode == 'E0_perpmodB_min':
            return self('E0_un0_perpmodB_min')
        else:  # use the logic directly from the perpmod pattern (see self.get_perpmod, for details)
            # [TODO] encapsulate this somehow? It's repeated code from QuantityLoader.__call__.
            try:
                matched = self.match_var('E_un0_perpmod_B', check='KNOWN_PATTERNS')
            except FormulaMissingError as err0:  # (direct)   # no match in KNOWN_VARS & KNOWN_PATTERNS.
                # >> actually get value from load_direct. Crash if that fails <<
                try:
                    return self.load_direct('E_un0_perpmod_B')
                except Exception as err1:
                    raise err1 from err0   # traceback will include info from err0 and err1.
            else:
                return matched.load_value(self, **kw_perpmod)
