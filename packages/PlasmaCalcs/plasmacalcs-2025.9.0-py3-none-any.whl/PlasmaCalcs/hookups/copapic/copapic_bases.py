"""
File Purpose: base quantities for CopapicCalculator
"""
import numpy as np

import xarray as xr

from ...errors import (
    InputConflictError, FluidValueError, DimensionAttributeError,
    FormulaMissingError,
)
from ...quantities import AllBasesLoader, SimpleDerivedLoader
from ...tools import UNSET, is_iterable_dim


class CopapicBasesLoader(AllBasesLoader, SimpleDerivedLoader):
    '''base quantities based on Copapic output.'''

    # # # BASE_QUANTS directly from Copapic # # #

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
        return xr.DataArray(self.fluid.params['nu'] * self.u('Hz'), attrs=self.units_meta())

    @known_var(load_across_dims=['component'], aliases=['dspace'])
    def get_ds(self):
        '''grid spacing (of output files). vector(ds), e.g. [dx, dy, dz]. Depends on self.component.
        '''
        x = str(self.component)
        dx_raw = self.input_deck.get_dspace(x) 
        dx = dx_raw * self.u('length')
        return xr.DataArray(dx, attrs=self.units_meta())

    @known_var(dims=['snap', 'fluid'], aliases=['den'], deps=['n'])
    def get_deltafrac_n(self):
        '''normalized density perturbation. (directly from Copapic.) deltafrac_n = (n - n0) / n0.'''
        n = self('n')
        n0 = self('n0')
        return (n - n0) / n0

    @known_var(load_across_dims=['fluid'])
    def get_n0(self):
        '''background density. (directly from Copapic.)
        '''
        try:
            n0 = self.fluid.n0
        except AttributeError:
            errmsg = f'{type(self.fluid).__name__} object has no attribute "n0".'
            raise DimensionAttributeError(errmsg) from None
        return xr.DataArray(n0 * self.u('n'), attrs=self.units_meta())
    
    @known_var(dims=['snap'])
    def get_phi(self):
        '''electric potential. (directly from Copapic)'''
        return self.load_maindims_var_across_dims('phi', u='E length', dims=['snap'])

    @known_var(load_across_dims=['component'])
    def get_E_ext(self):
        '''external electric field. (directly from Copapic).'''
        x = str(self.component)
        E = self.input_deck.get('E_extern', [0, 0, 0])
        if x == 'x':
            Ex = E[0] * self.u('E')
        elif x =='y':
            Ex = E[1] * self.u('E')
        elif x == 'z':
            Ex = E[2] * self.u('E')
        return xr.DataArray(Ex, attrs=self.units_meta())

    @known_var(load_across_dims=['component'])
    def get_B(self):
        '''magnetic field. (directly from Copapic)'''
        x = str(self.component)
        B = self.input_deck.get('B_extern', [0, 0, 0])
        if x == 'x':
            Bx = B[0] * self.u('b')
        elif x == 'y':
            Bx = B[1] * self.u('b')
        elif x == 'z':
            Bx = B[2] * self.u('b')
        return xr.DataArray(Bx, attrs=self.units_meta())

    @known_var(deps=['E_ext', 'E_phi'])
    def get_E(self):
        '''electric field. E = E_external + E_phi = E_external - grad(phi)'''
        E_ext = self('E_ext')
        E_phi = self('E_phi')
        return E_ext + E_phi
    

    @known_var(deps=['grad_phi'])
    def get_E_phi(self):
        '''electric field, from phi. E_phi = -grad(phi). Doesn't include E_ext component.'''
        return -self('grad_phi')
    

    @known_var(dims=['snap', 'fluid'])
    def get_n(self):
        '''Number density. Directly from Copapic'''
        return self.load_maindims_var_across_dims('den', dims=['snap', 'fluid'])  # [dimensionless]

    @known_var(load_across_dims=['fluid'])
    def get_collType(self):
        '''collision type. (directly from Copapic)'''
        return xr.DataArray(self.fluid.params["collision_type"])
    
    @known_var(load_across_dims=['fluid'])
    def get_vadvanceType(self):
        '''advance type. (directly from Copapic)'''
        return xr.DataArray(self.fluid.params["vadvance_type"])
    
    @known_var(load_across_dims=['fluid'])
    def get_npercell(self):
        '''number of particles per cell. (directly from Copapic)'''
        return xr.DataArray(self.fluid.params["npercell"], attrs=self.units_meta())
    
    @known_var(load_across_dims=['fluid', 'component'])
    def get_v0(self):
        '''Initial Drift Velocity. (directly from Copapic)'''
        x = str(self.component)
        v0 = self.fluid.params["v0"]
        if x == 'x':
            v0 = v0[0] * self.u('l') / self.u('t')
        elif x == 'y':
            v0 = v0[1] * self.u('l') / self.u('t')
        elif x == 'z':
            v0 = v0[2] * self.u('l') / self.u('t')
        return xr.DataArray(v0, attrs=self.units_meta())
    
    @known_var(load_across_dims=['fluid', 'component'])
    def get_vth(self):
        '''thermal velocity. (directly from Copapic)'''
        x = str(self.component)
        vth = self.fluid.params["vth"]
        if x == 'x':
            vth = vth[0] * self.u('l') / self.u('t')
        elif x == 'y':
            vth = vth[1] * self.u('l') / self.u('t')
        elif x == 'z':
            vth = vth[2] * self.u('l') / self.u('t')
        return xr.DataArray(vth, attrs=self.units_meta())
    
    @known_var(load_across_dims=['fluid','component','snap'])
    def get_flux(self):
        '''flux. (directly from Copapic)'''
        return self.load_maindims_var_across_dims('flux', u='flux', dims=['snap', 'fluid', 'component'])  # [dimensionless]

    
    
    @known_var(load_across_dims=['component','snap'])
    def get_Eraw(self):
        '''Electric field. (directly from Copapic)'''
        x = str(self.component)
        varname = f'E_{x}'
        return self.load_maindims_var_across_dims(varname, u='E', dims=['snap'])  # [dimensionless]
    
    @known_var(load_across_dims=['snap'])
    def get_rho(self):
        '''charge density. (directly from Copapic)'''
        return self.load_maindims_var_across_dims('rho', dims=['snap'])