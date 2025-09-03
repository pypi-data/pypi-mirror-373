"""
File Purpose: base quantities for BifrostCalculator
"""

from ...mhd import MhdBasesLoader
from ...tools import simple_property


### --------------------- BifrostBasesLoader --------------------- ###

class BifrostBasesLoader(MhdBasesLoader):
    '''base quantities based on Bifrost output.'''
    
    # # # DIRECTLY FROM BIFROST # # #
    @known_var(dims=['snap'])
    def get_r(self):
        '''mass density. (directly from Bifrost)
        assumes single fluid mode, i.e. result corresponds to the single fluid from Bifrost.
        '''
        self.assert_single_fluid_mode('r')
        return self.load_maindims_var_across_dims('r', u='mass_density', dims=['snap'])

    @known_var(dims=['snap', 'component'])
    def get_p(self):
        '''momentum density. (directly from Bifrost)
        assumes single fluid mode, i.e. result corresponds to the single fluid from Bifrost.
        '''
        self.assert_single_fluid_mode('p')
        return self.load_maindims_var_across_dims('p', u='momentum_density', dims=['snap', 'component'])

    @known_var(dims=['snap'])
    def get_e(self):
        '''energy density. (directly from Bifrost)
        Per unit volume, e.g. the SI units would be Joules / meter^3.
        assumes single fluid mode, i.e. result corresponds to the single fluid from Bifrost.
        '''
        self.assert_single_fluid_mode('e')
        return self.load_maindims_var_across_dims('e', u='energy_density', dims=['snap'])

    @known_var(dims=['snap', 'component'])
    def get_B(self):
        '''magnetic field. (directly from Bifrost)'''
        return self.load_maindims_var_across_dims('b', u='b', dims=['snap', 'component'])

    @known_var
    def get_gamma(self):
        '''adiabatic index. (directly from Bifrost)'''
        return self.params['gamma']

    # # # DERIVED # # #
    @known_var(deps=['p', 'r'])
    def get_u(self):
        '''velocity. u = p / r = (momentum density / mass density)'''
        return self('p') / self('r')

    @known_var(deps=['curl_B'])
    def get_J(self):
        '''current density. J = curl(B) / mu0.
        Per unit area, e.g. the SI units would be Amperes / meter^2.
        '''
        if self.J_stagger:
            with self.using(stagger_direct=False):  # don't stagger B within load_direct
                curl_B = self('centered_facecurl_B')  # curl of B, staggered to cell centers
        else:
            curl_B = self('curl_B')
        return curl_B / self.u('mu0')

    cls_behavior_attrs.register('J_stagger', default=True)
    J_stagger = simple_property('_J_stagger', default=True,
        doc='''whether to use stagger grid for derivatives during J = curl(B) / mu0.
        False --> apply naive derivatives (e.g. xarray differentiate) to stagger-centered B.
        True --> load staggered B across full grid, apply staggered derivatives,
                center result to cell centers, then apply any slices.''')

    # # # MISC TABIN VARS (other than EOS vars ne, T, and P) # # #
    @known_var(deps=['SF_e', 'SF_r'])
    def get_kappaR(self):
        '''Rosseland opacity, from plugging r and e into eos tables (see self.tabin).'''
        return self.get_ertab_var('kappaR', 'opacity')
