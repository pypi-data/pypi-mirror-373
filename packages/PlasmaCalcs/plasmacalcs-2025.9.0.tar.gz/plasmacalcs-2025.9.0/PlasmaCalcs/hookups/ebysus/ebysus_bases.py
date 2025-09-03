"""
File Purpose: base quantities for EbysusCalculator
"""
import xarray as xr

from ...quantities import AllBasesLoader, SimpleDerivedLoader

class EbysusBasesLoader(AllBasesLoader, SimpleDerivedLoader):
    '''base quantities based on Ebysus output.'''

    # # # BASE_QUANTS which are properties of Ebysus # # #

    @known_var
    def get_gamma(self):
        '''adiabatic index.'''
        return 5/3   # it's always 5/3 for ebysus... other values remain untested.


    # # # BASE_QUANTS directly from Ebysus # # #
    
    @known_var(load_across_dims=['fluid'])
    def get_m(self):
        '''mass.'''
        return xr.DataArray(self.u('amu') * self.fluid.m, attrs=dict(units=self.units))

    @known_var(load_across_dims=['fluid'])
    def get_q(self):
        '''charge. (directly from Ebysus)'''
        return xr.DataArray(self.u('qe') * self.fluid.q, attrs=dict(units=self.units))

    @known_var(load_across_dims=['component'], aliases=['dspace', 'ds_sim'])
    def get_ds(self):
        '''vector(spatial scale), e.g. [dx, dy, dz]. Depends on self.component.'''
        x = str(self.component)
        dx = getattr(self.dd, f'd{x}') * self.dd.uni('l')
        return xr.DataArray(dx, attrs=dict(units=self.units))


    # # # BASE_QUANTS loaded directly # # #

    @known_var(dims=['snap', 'component'])
    def get_B(self):
        '''magnetic field. (directly from Ebysus)'''
        return self.load_maindims_var_across_dims('b', dims=['snap', 'component'])


    # # # other ebysus direct inputs # # #

    @known_var(dims=['snap', 'fluid'])
    def get_r(self):
        '''mass density. (directly from Ebysus)'''
        return self.load_maindims_var_across_dims('ri', dims=['snap', 'fluid'])

    @known_var(dims=['snap', 'fluid', 'component'])
    def get_p(self):
        '''momentum density. (directly from Ebysus)'''
        return self.load_maindims_var_across_dims('pi', dims=['snap', 'fluid', 'component'])


    # # # BASE_QUANTS derived from ebysus  # # #

    @known_var(deps=['r', 'm'])
    def get_n(self):
        '''number density. n = (r / m) = (mass density / mass)'''
        return self('r') / self('m')

    @known_var(deps=['p', 'r'])
    def get_u(self):
        '''velocity. u = p / r = (momentum density / mass density)'''
        return self('p') / self('r')


    # # # BASE_QUANTS calculated by helita, from ebysus  # # #
    # [TODO] calculate these in PlasmaCalcs instead.
    #    check PlasmaCalcs results against the helita calculations, for accuracy;
    #    check whether PlasmaCalcs or helita is faster.
    #    E.g. get_J_helita vs get_J, defined below.

    @known_var(dims=['snap', 'fluid'])
    def get_T(self):
        '''temperature. (directly from Ebysus).
        "maxwellian" temperature (classical T in thermodynamics).
        '''
        return self.load_maindims_var_across_dims('tg', dims=['snap', 'fluid'])

    # def get_nusj(self):
    #   defined in ebysus_collisions.py, instead.

    # def get_E(self):
    #   defined in ebysus_efield.py, instead.


    # # # CURRENT DENSITY (helita & here)  # # #

    @known_var(dims=['snap', 'component'])
    def get_J_helita(self):
        '''current density. (directly from Ebysus)'''
        return self.load_maindims_var_across_dims('j', dims=['snap', 'component'])

    @known_var(load_across_dims=['component'], aliases=['J_imposed'])
    def get_J_ext(self):
        '''imposed current density; see ic_ix, ic_iy, ic_iz from Ebysus.'''
        if self.dd.get_param('do_imposed_current', 0) <= 0:
            return self('0')  # not imposing any current.
        x = str(self.component)
        ic_units = self.dd.get_param('ic_units', 'ebysus').strip().lower()
        if ic_units == 'ebysus': ic_units = 'simu'
        result = self.dd.get_param(f'ic_i{x}', 0) * self.dd.uni('i', units_input=ic_units)
        return xr.DataArray(result, attrs=dict(units=self.units))

    @known_var(deps=['curl_B'])
    def get_J_B(self):
        '''current density from magnetic field (ignoring J_ext). J_B = curl(B) / mu0.'''
        return self('curl_B') / self.dd.uni('mu0')

    @known_var(deps=['J_B', 'J_ext'])
    def get_J(self):
        '''total current density. J == J_B + J_ext == curl(B) / mu0 + J_imposed.'''
        # [EFF] (2024/03/16) faster than J_helita when getting 10+ snaps with 3 components.
        #     Slower than J_helita when getting only 1 snap or only 1 component.
        #     (within a factor of 2x speed of J_helita either way.)
        # accuracy check: seems to be reasonably similar when using dd.stagger_kind='first';
        #     also similar (but more outliers) when using dd.stagger_kind='fifth'.
        return self('J_B') + self('J_ext')
