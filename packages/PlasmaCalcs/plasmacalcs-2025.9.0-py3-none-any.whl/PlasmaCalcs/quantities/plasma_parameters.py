"""
File Purpose: calculating plasma parameters, e.g. plasma beta, plasma frequency
"""
import numpy as np

from .quantity_loader import QuantityLoader
from ..dimensions import ELECTRON, IONS
from ..tools import xarray_sum

class PlasmaParametersLoader(QuantityLoader):
    '''plasma parameters, e.g. plasma beta, plasma frequency'''
    # # # PLASMA BETA # # #
    @known_var(deps=['P', 'mod_B'])
    def get_beta(self):
        '''plasma beta. beta = (pressure / magnetic pressure) = (P / (B^2 / (2 mu0)))'''
        return self('P') / (self('mod_B')**2 / (2 * self.u('mu0')))

    # # # GYROFREQUENCY # # #
    @known_var(deps=['q', 'mod_B', 'm'])
    def get_sgyrof(self):
        '''signed gyrofrequency. sgyrof == q |B| / m == charge * |B| / mass. Negative when charge < 0.'''
        return self('mod_B') * (self('q') / self('m'))
        # ^note: grouped (q/m) for efficiency (both are probably constant across maindims)
        #    and because both might be small numbers --> helps avoid getting close to float32 limits.

    @known_var(deps=['abs_sgyrof'], aliases=['cyclof', 'omega_c'])
    def get_gyrof(self):
        '''(unsigned) gyrofrequency. gyrof == |sgyrof| == |q| |B| / m == |charge| * |B| / mass.'''
        return self('abs_sgyrof')

    # # # MAGNETIZATION PARAMETER (KAPPA) # # #
    @known_var(deps=['nusn', 'sgyrof'])
    def get_skappa(self):
        '''signed kappa (magnetization parameter). skappa = sgyrof / nusn. Negative when charge < 0.
        skappa = gyrofrequency / collision frequency of self.fluid with neutrals.
        gyrofrequency == q * |B| / (mass * nusn). 
        ''' 
        return self('sgyrof') / self('nusn')

    @known_var(deps=['abs_skappa'])
    def get_kappa(self):
        '''(unsigned) kappa (magnetization parameter). kappa = |skappa| == |gyrof| / nusn.
        kappa = |gyrofrequency| / collision frequency of self.fluid with neutrals.
        '''
        return self('abs_skappa')

    # # # PLAMSA FREQUENCY # # #
    @known_var(deps=['n', 'abs_q', 'm'])
    def get_wplasma(self):
        '''"plasma frequency". wplasma = sqrt(n q^2 / (m epsilon0))
        This is analogous to the "true" plasma frequency of Langmuir oscillations,
            which is calculated using the same formula but applied to electrons.
        wplasma is equivalent to wplasmae if self.fluid is electrons.
        '''
        return self('n')**0.5 * self('abs_q') / (self('m') * self.u('eps0'))**0.5

    @known_var(deps=['wplasma'], aliases=['wpe', 'omega_pe'], ignores_dims=['fluid'])
    def get_wplasmae(self):
        '''electron plasma frequency; Langmuir oscillations. wpe = sqrt(ne qe^2 / (me epsilon0))'''
        return self('wplasma', fluid=ELECTRON)

    # # # DEBYE LENGTH # # #
    @known_var(deps=['ldebye2'])
    def get_ldebye(self):
        '''Debye length (of self.fluid). ldebye = sqrt(epsilon0 kB T / (n q^2))'''
        return self('ldebye2')**0.5

    @known_var(deps=['Tjoule', 'n', 'abs_q'])
    def get_ldebye2(self):
        '''squared Debye length (of self.fluid). ldebye2 = epsilon0 kB T / (n q^2)'''
        return self.u('eps0') * self('Tjoule') / (self('n') * self('abs_q')**2)
        
    @known_var(deps=['ldebye2'], reduces_dims=['fluid'])
    def get_ldebye_subset(self):
        '''"total" Debye length; ldebye_subset = sqrt(epsilon0 kB / sum_fluids(n q^2 / (kB T)))
        sum is taken over the fluids in self.fluid.
        Equivalent: sqrt( 1 / sum_fluids(1/ldebye^2) )
        '''
        return xarray_sum(1/self('ldebye2'), dim='fluid')**-0.5

    @known_var(deps=['ldebye_subset'], ignores_dims=['fluid'])
    def get_ldebye_total(self):
        '''total Debye length for all fluids; ldebye_total = sqrt(epsilon0 kB / sum_fluids(n q^2 / (kB T)))
        sum is taken over all the fluids in self.fluids.
        Equivalent: sqrt( 1 / sum_fluids(1/ldebye^2) )
        '''
        return self('ldebye_subset', fluid=None)  # fluid=None --> use all fluids.

    # # # MEAN FREE PATH # # #
    @known_var(deps=['vtherm', 'nusn'], aliases=['lmfp'])
    def get_mean_free_path(self):
        '''collisional mean free path. lmfp = vtherm / nusn = thermal velocity / collision frequency.'''
        return self('vtherm') / self('nusn')

    # # # THERMAL VELOCITY # # #
    @known_var(deps=['Tjoule', 'm'], aliases=['vth', 'vthermal'])
    def get_vtherm(self):
        '''thermal velocity. vtherm = sqrt(kB T / m)'''
        return (self('Tjoule') / self('m'))**0.5

    @known_setter
    def set_vtherm(self, value, **kw):
        '''set thermal velocity, by setting T.
        vtherm = sqrt(kB T / m) --> set T to (m vtherm^2 / kB).
        '''
        T = self('m').values * value**2 / self.u('kB')
        self.set('T', T, **kw)

    @known_var(deps=['T_n', 'm_n'], aliases=['vth_n', 'vthermal_n',
                                'vth_neutral', 'vtherm_neutral', 'vthermal_neutral'])
    def get_vtherm_n(self):
        '''thermal velocity for neutrals. vtherm_n = sqrt(kB T_n / m_n)'''
        return (self('kB*T_n') / self('m_n'))**0.5

    # # # SOUND SPEED # # #
    @known_var(deps=['csound2'], aliases=['cs'])
    def get_csound(self):
        '''sound speed. csound = sqrt(gamma * P / r)'''
        return self('csound2')**0.5

    @known_var(deps=['gamma', 'P', 'r'], aliases=['cs2'])
    def get_csound2(self):
        '''sound speed squared. csound2 = gamma P / r.'''
        return self('gamma') * self('P') / self('r')

    # # # ALFVEN SPEED # # #
    @known_var(deps=['va2'], aliases=['va'])
    def get_valfven(self):
        '''Alfven speed. valfven = |B| / sqrt(mu0 * r)'''
        return self('va2')**0.5

    @known_var(deps=['mod2_B', 'r'], aliases=['va2'])
    def get_valfven2(self):
        '''Alfven speed squared. valfven2 = |B|^2 / (mu0 * r)'''
        return self('mod2_B') / (self.u('mu0') * self('r'))

    # # # ni/ne # # #
    @known_var(deps=['n'], ignores_dims=['fluid'])
    def get_niefrac(self):
        '''ion-to-electron density ratio. niefrac = ni / ne.
        Result always corresponds to fluid=IONS, regardless of current self.fluid.
        '''
        return self('n', fluid=IONS) / self('n', fluid=ELECTRON)

    # # # ROSENBERG CRITERION # # #
    # [TODO] this should move to a separate file, it's too specific for "generic plasma parameters" loader.
    @known_var(deps=['nusn', 'wplasma'], aliases=['rosenberg'])
    def get_rosenberg_qn(self):
        '''Rosenberg criterion for quasineutrality, for each fluid: rosenberg_qn = (nusn / wplasma)^2.
        quasineutrality is "reasonable" (during farley-buneman analysis) iff rosenberg_qn << 1 for ions.
        (Intuitively: quasineutrality reasonable iff 'collisions much slower than plasma oscillations')

        If multiple ions, consider using self('rosenberg_multi') instead of one criterion per ion.

        see Rosenberg 1998, equation 17, for details.
        '''
        return self('nusn/wplasma')**2

    @known_var(deps=['nusn', 'abs_q', 'm'], aliases=['n_at_lmfp_eq_ldebye', 'n_at_wplasma_eq_nusn'])
    def get_rosenberg_n(self):
        '''n such that rosenberg_qn == 1, for each fluid.
        Equivalent: rosenberg_qn * n.
        To satisfy Rosenberg criterion, need rosenberg_qn << 1.
        rosenberg_qn = (nusn / wplasma)^2 = nusn^2 * m * eps0 / (n * q^2),
            which is proportional to 1 / n
            --> n is "good" if n >> rosenberg_n.

        Note: this also happens to be the solution to lmfp == ldebye...
            lmfp = (vtherm/nusn) = ((kB T / m)^0.5 / nusn) == (epsilon0 kB T / (n q^2))^0.5 = ldebye
            --> (nusn^-2 m^-1) == (epsilon0 n^-1 q^-2)
            --> n == epsilon0 nusn^2 m / q^2.
        '''
        return self('nusn')**2 * (self('m') * self.u('eps0') / self('abs_q')**2)

    @known_var(deps=['rosenberg_n', 'n'])
    def get_rosenberg_n_margin(self):
        '''n / rosenberg_n. margin of safety for rosenberg criterion. "safe" if margin is large.'''
        return self('n') / self('rosenberg_n')

    @known_var(deps=['wplasma'], ignores_dims=['fluid'])
    def get_rosenberg_multi_wplasma(self):
        '''plasma frequency for rosenberg criterion with multiple ions.
        wplasma_multi^2 = 1 / (1 / wplasma1^2 + 1 / wplasma2^2 + ...),
            with sum across all ions in self('wplasma', fluids=None)
        see rosenberg_multi for details.
        '''
        wplasma_ions = self('wplasma', fluid=IONS)
        denom = xarray_sum(1 / wplasma_ions**2, dim='fluid')
        return denom**-0.5

    @known_var(deps=['nusn'], ignores_dims=['fluid'])
    def get_rosenberg_multi_nusn(self):
        '''collision frequency for rosenberg criterion with multiple ions.
        nusn_multi = nu1 * weight1 + nu2 * weight2 + ... / (weight1 + weight2 + ...),
            where weightj = wplasma_1^2 * wplasma_2^2 * ... / wplasma_j^2.
        see rosenberg_multi for details.
        '''
        wplasma_ions = self('wplasma', fluid=IONS)
        nusn_ions = self('nusn', fluid=IONS)
        # compute weights in log-space:
        # log(weightj) = log(wplasma_1^2) + log(wplasma_2^2) + ... - log(wplasma_j^2)
        log_wplasma2 = np.log10(wplasma_ions**2)
        log_weight_prod = xarray_sum(log_wplasma2, dim='fluid')
        log_weight_j = log_weight_prod - log_wplasma2
        # compute coefficients in log space:
        # coeff_j = weightj / sum(weights)
        # log(coeff_j) = log(weightj) - log(sum(weights))
        weight_j = 10**log_weight_j
        log_sum_weights = np.log10(xarray_sum(weight_j, dim='fluid'))
        log_coeff_j = log_weight_j - log_sum_weights
        coeff_j = 10**log_coeff_j
        terms = nusn_ions * coeff_j
        return xarray_sum(terms, dim='fluid')

    @known_var(deps=['rosenberg_multi_wplasma', 'rosenberg_multi_nusn'])
    def get_rosenberg_multi(self):
        '''rosenberg criterion for multiple ions: rosenberg_multi = (nusn_multi / wplasma_multi)^2.
        quasineutrality is "reasonable" (during farley-buneman analysis) iff rosenberg_multi << 1.
        This criterion should be more accurate than using rosenberg_qn for each ion, separately.

        (Below uses '...' to denote "terms independent of wplasma_i and nu_in".)
        Rosenberg 1998 equation 17, derived from equation 14, assumed only 1 ion.
        However, equation 14 comes from 13, where wplasma_i and nu_in only appear as (Ai/wplasma_i^2).
            where Ai = omega * (omega + i nu_in) + ...   (see equation 15).
            equation 13 looks like: ... + (Ai/wplasma_i^2) = 0
        From equation 4 I infer the dispersion relation with multiple ions will be like:
            ... + sum_i (Ai/wplasma_i^2) = 0.
        Expanding this sum reveals that it can be expressed in the same algebraic form as with 1 ion:
            ... + Am/wplasma_m^2 = 0, when:
            wplasma_m^2 = 1 / (1/wplasma_1^2 + 1/wplasma_2^2 + ...),
            Am = omega * (omega + i nu_mn) + ...
            nu_mn = nu1 * weight1 + nu2 * weight2 + ... / (weight1 + weight2 + ...),
                where weightj = wplasma_1^2 * wplasma_2^2 * ... / wplasma_j^2.
        Thus, the remaining steps done by Rosenberg to derive the criterion should apply in the same way,
            and for multiple ions we can conclude the criterion is (nu_mn / wplasma_m)^2 << 1.


        Okay, actually, in practice, it's probably not useful to use this...
            it mostly just selects the least-dense ion, due to the 1/wplasma^2 scaling.
        Also, the criterion means "instability gets dampened when collisions are faster than plasma oscillations"
            But for multiple ions, it's really more like, the instability for THAT ion gets dampened...
            (Also, I think one of the assumptions in the paper probably fails when wplasma is small...)
        '''
        return self('rosenberg_multi_nusn/rosenberg_multi_wplasma')**2
