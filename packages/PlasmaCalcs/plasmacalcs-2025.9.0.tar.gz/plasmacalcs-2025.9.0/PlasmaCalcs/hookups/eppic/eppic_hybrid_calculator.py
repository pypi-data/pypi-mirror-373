"""
File Purpose: EppicHybridCalculator, for outputs from eppic hybrid simulations.
"""

import xarray as xr

from .eppic_calculator import EppicCalculator
from ...dimensions import IONS
from ...errors import FluidValueError, FormulaMissingError

class EppicHybridCalculator(EppicCalculator):
    '''
    EppicHybridCalculator is a subclass of EppicCalculator that is designed to
    handle hybrid simulations in EPPIC. It provides methods for loading and
    processing data specific to hybrid simulations.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hybrid = True

    @known_var(load_across_dims=['fluid'])
    def get_distribution_type(self):
        '''distribution type: DataArray of strings: 'electron', 'ion', or 'neutral'
        (useful internally for handling electrons differently,
            since electrons are fluid while ions are PIC particles.)
        '''
        if self.fluid.is_electron():
            return xr.DataArray('electron')
        elif self.fluid.is_ion():
            return xr.DataArray('ion')
        elif self.fluid.is_neutral():
            return xr.DataArray('neutral')
        else:
            raise FluidValueError(f'expected electron, ion, or neutral fluid; got {self.fluid}')

    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_deltafrac_n(self, *, distribution_type):
        '''normalized density perturbation. deltafrac_n = (n - n0) / n0.
            For hybrid simulations, electron density is the sum of the ion densities  
        '''
        if distribution_type == 'electron':
            n0 = self.get_n0()
            n = self('sum_fluids_n', fluid=IONS)
            return (n - n0) / n0
        else:
            return super().get_deltafrac_n()

    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_flux(self, *, distribution_type):
        '''flux. (for non-electrons: directly from Eppic. for electrons: not yet implemented)
        (Eventually, can determine electron flux via solving electron momentum equation for u_e,
            neglecting the du_e/dt term. Result similar to u_drift, but include P_e contribution.)
        '''
        if distribution_type == 'electron':
            raise FormulaMissingError('get_flux for electrons not yet implemented')
        else:
            return super().get_flux()
    
    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_n0(self, *, distribution_type):
        '''background density. (directly from Eppic.)
        For hybrid simulations, electron density is the sum of the ion densities  
        note: as with all other quantities, this will be output in [self.units] unit system;
            numerically equal to eppic.i value if using 'raw' units.
        '''
        if distribution_type == 'electron':
            return self('sum_fluids_n0', fluid=IONS)
        else:
            return super().get_n0()
        
    @known_var(partition_across_dim=('fluid', 'distribution_type'), aliases=['temp', 'temperature'])
    def get_T(self, *, distribution_type):
        ''' temperature in Kelvin.

        For electrons, just loads 'temperature' from snapshot.
        For ions, equivalent to rmscomps_Ta.
            (Use self.T_indim_only=True if you want to ignore Ta_z in 2D sim)
        '''
        # [TODO] actually, should probably define get_Ta_or_Tajoule for electrons,
        #    since that is the "base" var in super().
        #    e.g. I think Ta for electrons could just return 'temperature' (without varying across component);
        #    that might make it just work, but it might also take some debugging to get it right.
        #    - SE (2025/05/07)
        if distribution_type == 'electron':
            result = self.load_maindims_var_across_dims('temperature', dims=['snap']) / self.u('kB')
            return result
        else:
            return super().get_T()
    
    @known_var(partition_across_dim=('fluid', 'distribution_type'))
    def get_T_box(self, *, distribution_type):
        '''temperature of the entire simulation box, as if full of particles,
        and observed by something that could not resolve the individual cells.
        Equivalent: rmscomps(Ta_from_moment2).

        Ignores Ta components for directions in which the box has no extent.
        '''
        if distribution_type == 'electron':
            return self('mean_T')  # Te is isotropic for hybrid eppic --> T_box is just mean_T.
        else:
            return super().get_T_box()
