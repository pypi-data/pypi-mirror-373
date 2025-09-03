"""
File Purpose: The main calculator class for multifluid analysis from single-fluid mhd,
for hookups to inherit from.
"""

from .mhd_multifluid_bases import MhdMultifluidBasesLoader
from .mhd_multifluid_densities import MhdMultifluidDensityLoader
from .mhd_multifluid_ionization import MhdMultifluidIonizationLoader
from ..mhd_calculator import MhdCalculator
from ...plasma_calculator import MultifluidPlasmaCalculator

class MhdMultifluidCalculator(MhdMultifluidDensityLoader, MhdMultifluidIonizationLoader,
                              MhdMultifluidBasesLoader, MultifluidPlasmaCalculator,
                              MhdCalculator):
    '''class for multi-fluid analysis of single-fluid MHD outputs.

    set self.fluid=SINGLE_FLUID to get single-fluid values,
        otherwise will get inferred multifluid values.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    # parent class ordering notes:
    # - MhdMultifluidIonizationLoader must go before MhdMultifluidBasesLoader,
    #     because MhdMultifluidBasesLoader parent BasesLoader defines get_ionfrac too;
    #     this affects known_var results... (maybe it's a bug in known_var code?)
    #     with this ordering, KNOWN_VARS['ionfrac'].cls_where_defined is MhdMultifluidIonizationLoader;
    #     without this ordering, it is BasesLoader instead, which gives wrong deps.

    @property
    def fluids_elements(self):
        '''ElementList of unique elements found in any of self.fluids.
        To alter self.elements, adjust self.fluids; will infer new self.elements automatically.
        '''
        return self.fluids.unique_elements(istart=0)

    def init_fluids(self):
        '''initialize self.fluid, fluids, jfluid, and jfluids
        [Not implemented by MhdMultifluidCalculator; subclass should implement].
        '''
        raise NotImplementedError(f'{type(self).__name__}.init_fluids()')

    def use_mix_heavy_ions(self, m_tol=0.1, *, m_min=5, m_mean_mode='simple', **kw_mix_heavy_ions):
        '''self.init_fluids() then set self.fluids = self.fluids.mix_heavy_ions(...). returns self.fluids.
        See self.fluids.mix_heavy_ions for more details.

        m_tol: number
            maximum allowed relative mass deviation from mean within a group (an IonMixture).
            within each group, all ions have |m_ion - mean(m)| < m_tol * mean(m).
            E.g. 0.1 --> all ions in each group are within 10% of that group's mean mass.
        m_min: number
            minimum mass (in amu, i.e. m_H ~= 1) for an ion to be considered "heavy".
            ions with m < m_min are ignored.
        m_mean_mode: str
            mode for calculating mean mass of each IonMixture.
            'simple' (default) or 'density' (weighted by number density).
        '''
        self.init_fluids()
        mix = self.fluids.mix_heavy_ions(m_tol=m_tol, m_min=m_min, m_mean_mode=m_mean_mode, **kw_mix_heavy_ions)
        self.fluids = mix
        return self.fluids


    # # # COLLISIONS # # #
    # aliases to check during set_collisions_crosstab_defaults
    #    (which gets called the first time self.collisions_cross_mapping is accessed).
    # override from super() to avoid 'H' and 'He' aliases to avoid ambiguity with Element fluids.
    _COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES = \
        MultifluidPlasmaCalculator._COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES.copy()
    _COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES.update({
        'H_I'   : ['H_I',    'H I'],  # excludes 'H', since 'H' might be an Element.
        'He_I'  : ['He_I',   'He I'], # excludes 'He', since 'He' might be an Element.
        })

    # note: lots of other functionality inherited from parents.
