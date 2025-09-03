"""
File Purpose: EppicInstabilityCalculator with tfbi-specific methods
"""
import re

import numpy as np
import xarray as xr

from .eppic_instability_calculator import EppicInstabilityCalculator
from ..eppic_calculator import EppicCalculator

from ....dimensions import ELECTRON
from ....errors import (
    InputError, InputMissingError,
    DimensionalityError,
)
from ....tools import (
    simple_property,
    xarray_grid, xarray_promote_index_coords, xarray_demote_index_coords,
    xarray_log_coords,
)


class EppicTfbiCalculator(EppicInstabilityCalculator):
    '''EppicInstabilityCalculator with tfbi-specific methods.
    [TODO] some of these are generic enough to [MV] to a TfbiCalculator parent,
        if ever wanting to use a non-Eppic TfbiCalculator.
        E.g., with_chargesep_e_scaling could work for any TfbiCalculator.

    See also: EppicCalculatorWithTfbi, for an EppicCalculator which also has tfbi-related methods.
    (EppicTfbiCalculator is a FromDatasetCalculator. Not from an eppic.i file.)
    '''

    def chargesep_e_scaling(self, N=24, *, safety=0.1, name='n_mul'):
        '''returns xarray_grid of n_mul from 1 to safety * ne_at_wplasma_eq_nusn / ne.
        (Implementation assumes ne > ne_at_wplasma_eq_nusn; will crash otherwise.)

        n_at_wplasma_eq_nusn = epsilon0 nusn^2 m / q^2,
            and has aliases rosenberg_n, n_at_lmfp_eq_ldebye.

        (result * ne) spans (evenly in logspace) from ne to ne_at_wplasma_eq_nusn.

        N: int
            number of points in result
        name: str
            name of resulting array and coordinate.
        safety: number, probably less than 1
            safety factor for the range of n_mul.
            smaller safety is MORE safe (extending the search into more drastic n_mul).
        '''
        ne = self('n', fluid=ELECTRON)
        ne_at_wplasma_eq_nusn = self('n_at_wplasma_eq_nusn', fluid=ELECTRON)
        rat = ne_at_wplasma_eq_nusn/ne
        if rat.size == 1:     # if rat can be converted to a single scalar, do that,
            rat = rat.item()  #   to avoid using array_lims mode (which includes 'n_mul_dim').
        result = xarray_grid(safety*rat, 1, N, name=name, logspace=True, reverse=True)
        return result

    def with_chargesep_e_scaling(self, N=24, safety=0.1, **kw_init):
        '''returns self with_scaling all n by grid from 1 to safety * ne_at_wplasma_eq_nusn / ne.
        solve tfbi across result to evaluate the "okay-ness" of scaling all number densities.
        At some point in this range, will probably see significant changes in tfbi solution.

        smaller safety is MORE safe (extending the search into more drastic n_mul).

        Equivalent: self.with_scaling({'n': self.chargesep_e_scaling(...)})
        '''
        chargesep_e_scaling = self.chargesep_e_scaling(N, safety=safety, name='n_mul')
        return self.with_scaling({'n': chargesep_e_scaling}, **kw_init)


class EppicCalculatorWithTfbi(EppicCalculator):
    '''EppicCalculator which knows some tfbi-related methods.
    see help(EppicCalculator) for more details.
    '''

    # # # BASES # # #
    def _get_n_neutral(self):
        '''get the number density of self.fluid when it is an EppicNeutral or EppicNeutralList.
        (Or, crash with a helpful FormulaMissingError error message.)

        The implementation here returns the value of _coord_ngrid,
            either from eppic.i file, or from self.tfbi_grid1_zeros if available.
            (Both should be very similar, but value from eppic.i file has only 4 sigfigs.)
        Does NOT check super()._get_n_neutral().
            Setting self.set_var('nj', value, ...) is untested; might not do anything.

        result will be a xarray.DataArray with ndim=0.
        '''
        input_coord = self.input_deck['_coord_ngrid']
        if self.tfbi_grid1_zeros is None:
            result = input_coord
        else: # get the more precise value
            index = self.input_deck['_coord_ngrid_index']
            result = self.tfbi_grid1_zeros['ngrid'].isel(ngrid=index).item()
        return xr.DataArray(result)


    # # # INDEX1 STUFF # # #

    INDEX1_KEYS = ('EBspeed', 'Tgrid', 'ionfrac_H', 'kappae', 'ngrid')

    cls_behavior_attrs.register('tfbi_grid1_zeros', default=None)
    tfbi_grid1_zeros = simple_property('_tfbi_grid1_zeros', default=None,
        doc='''5D grid of zeros including all possibilities for tfbi_index1 coordinates.
        Must be provided separately in order to compute self('tfbi_index1_delta'),
            the array of all zeros EXCEPT at the point corresponding to index1 of this calculator.
        Example:
            DSR_DIR = 'Grid01.pcxarr'
            dsR00 = pc.xarray_load(DSR_DIR).load().drop_vars('T')  # T==Tgrid; don't keep both
            dsR0 = dsR00.pc.index_coords(max_ndim=1)  # add the index coords into the grid
            self.tfbi_grid1_zeros = xr.zeros_like(dsR0.it.growth_kmax())''')

    @known_var
    def get_tfbi_index1_with_eppici_coords(self):
        '''tfbi index1 value as a size=1 DataArray with 5-tuple as its element, and dtype=object.
        The index1 tells indexes from "grid01" for (in this order):
            EBspeed, Tgrid, ionfrac_H, kappae, ngrid

        indexes come from the input deck, from param names like '_coord_EBspeed_index'.

        Result has shape (1,1,1,1,1). Result also has coords for each key.
        '''
        KEYS = self.INDEX1_KEYS
        indexes = {k: self.input_deck[f'_coord_{k}_index'] for k in KEYS}
        cvalues = {k: self.input_deck[f'_coord_{k}'] for k in KEYS}  # approximate; has rounding errors.
        indexes_coords = {f'{k}_index': (k, [index]) for k, index in indexes.items()}
        cvalues_coords = {k: (k, [cval]) for k, cval in cvalues.items()}
        index1 = tuple(indexes[k] for k in KEYS)
        result = np.array([[[[[None]]]]], dtype=object)
        result[0,0,0,0,0] = index1
        return xr.DataArray(result, dims=KEYS, coords={**indexes_coords, **cvalues_coords})

    @known_var(deps=['tfbi_index1_with_eppici_coords'])
    def get_tfbi_index1(self):
        '''tfbi index1 value as a size=1 DataArray with 5-tuple as its element, and dtype=object.
        The index1 tells indexes from "grid01" for (in this order):
            EBspeed, Tgrid, ionfrac_H, kappae, ngrid
        The dims of result will {k}_index, e.g. 'EBspeed_index'.

        Result has shape (1,1,1,1,1). Result does NOT also have coords for each key.
        '''
        result = self('tfbi_index1_with_eppici_coords')
        result = xarray_promote_index_coords(result)
        return result.drop_vars(self.INDEX1_KEYS)

    @known_var(deps=['tfbi_index1_with_eppici_coords'])
    def get_tfbi_index1_with_coords(self):
        '''tfbi index1 value as a size=1 DataArray with 5-tuple as its element, and dtype=object.
        The index1 tells indexes from "grid01" for (in this order):
            EBspeed, Tgrid, ionfrac_H, kappae, ngrid

        indexes come from the input deck, from param names like '_coord_EBspeed_index'.
        Result has shape (1,1,1,1,1). Result also has coords for each key.

        Coords for each key come from the input deck UNLESS self.tfbi_grid1_zeros is available,
        in which case the more precise values from tfbi_grid1_zeros are used.
        (e.g. coord from eppic.i might say 3.162, while tfbi_grid1_zeros might say 3.162277660)
        '''
        result = self('tfbi_index1_with_eppici_coords')
        if self.tfbi_grid1_zeros is not None:
            result = self.assign_tfbi_index1_coords(result)
        return result

    @known_var(deps=['tfbi_index1_with_coords'])
    def get_tfbi_index1_with_log_coords(self):
        '''tfbi index1 value as a size=1 DataArray with 5-tuple as its element, and dtype=object.
        Like tfbi_index1_with_coords, but also has 'log_{key}' coords for easy reference.
        i.e., result has log_EBspeed, log_Tgrid, log_ionfrac_H, log_kappae, and log_ngrid coords, too.
        '''
        result = self('tfbi_index1_with_coords')
        return xarray_log_coords(result, self.INDEX1_KEYS, promote=False, drop=False)

    @known_var(deps=['tfbi_index1'])
    def get_tfbi_index1_bool(self):
        '''tfbi index1 value as a size=1 DataArray([[[[[True]]]]]),
        with "grid01" dims each having size=1, and including coords & index coords for each:
            EBspeed, Tgrid, ionfrac_H, kappae, ngrid
        '''
        return xr.ones_like(self('tfbi_index1'), dtype=bool)

    @known_var
    def get_tfbi_grid1_zeros(self):
        '''5D grid of zeros including all possibilities for tfbi_index1 coordinates.
        Internally stored (and can be altered) via self.tfbi_grid1_zeros.
        '''
        if self.tfbi_grid1_zeros is None:
            errmsg = ('self.tfbi_grid1_zeros must be provided (i.e. not None)\n'
                      'See help(type(self)).tfbi_grid1_zeros for more details.')
            raise InputMissingError(errmsg)
        return self.tfbi_grid1_zeros

    @known_var(deps=['tfbi_index1_bool', 'tfbi_grid1_zeros'])
    def get_tfbi_index1_delta(self):
        '''5D grid of zeros EXCEPT at the index1 for this calculator.
        The 5D grid includes all possible coordinate combinations for tfbi_index1.
        '''
        i1 = self('tfbi_index1_bool')
        grid1 = self('tfbi_grid1_zeros')
        grid1 = xarray_promote_index_coords(grid1)  # align by index; coord values include rounding errors.
        result = i1.reindex_like(grid1, fill_value=0)
        result = result + grid1   # include original grid1 coord values (for non-index coords)
        result = xarray_demote_index_coords(result)
        return result.astype(bool)

    def tfbi_index1_from_str(self, s, *, to='bool'):
        '''determine tfbi index1 from str like "index1=(1,2,3,4,5)" or just "(1,2,3,4,5)".
        
        to: 'tuple', 'xrtuple', 'bool', or 'delta'
            tuple --> just return 5-tuple of ints.
            xrtuple --> result is formatted like self('tfbi_index1') result.
                    i.e., size=1 DataArray with 5-tuple as its element, and dtype=object.
                    result dims will be {key}_index, e.g. 'EBspeed_index'.
            bool --> result is formatted like self('tfbi_index1_bool') result.
                    i.e., size=1 DataArray([[[[[True]]]]]), with all 5 index1 dims.
                    result dims will be {key}_index, e.g. 'EBspeed_index'.
            delta --> result is formatted like self('tfbi_index1_delta') result.
                    i.e., 5D grid of zeros EXCEPT at the index1 for this calculator.
                    result dims will be {key}, e.g. 'EBspeed'.
                    requires non-None self.tfbi_grid1_zeros.
        '''
        i = r'\s*(\d+)\s*'
        pattern = rf'.*index1\s*=\s*\({i},{i},{i},{i},{i}\).*'
        match = re.match(pattern, s)
        if match is None:
            raise InputError(f'input not like "index1=(1,2,3,4,5)". Got: {s!r}')
        indexes_from_str = match.groups()
        index1 = tuple(int(i) for i in indexes_from_str)
        if to == 'tuple':
            return index1
        # [TODO] encapsulate repeated code from earlier in this class.
        KEYS = self.INDEX1_KEYS
        indexes = dict(zip(KEYS, index1))
        indexes_coords = {f'{k}_index': (f'{k}_index', [index]) for k, index in indexes.items()}
        result = np.array([[[[[None]]]]], dtype=object)
        result[0,0,0,0,0] = index1
        result = xr.DataArray(result, dims=indexes_coords.keys(), coords=indexes_coords)
        if to == 'xrtuple':
            return result
        result = xr.ones_like(result, dtype=bool)
        if to == 'bool':
            return result
        if to != 'delta':
            errmsg = (f'unknown to={to!r}. Expected "tuple", "xrtuple", "bool", or "delta".')
            raise InputError(errmsg)
        # to == delta:
        grid1 = self('tfbi_grid1_zeros')
        grid1 = xarray_promote_index_coords(grid1)
        result = result.reindex_like(grid1, fill_value=0)
        result = result + grid1
        result = xarray_demote_index_coords(result)
        return result.astype(bool)

    def assign_tfbi_index1_coords(self, array):
        '''return array after assigning any index-related coords from tfbi_index1,
        based on values from self.tfbi_grid1_zeros, and index coords in array.

        This method expects array to have 'index' coords (possibly as dims),
            and overwrites the associated non-index coords.
            E.g. array has EBspeed_index --> result's EBspeed coord comes from grid1.
        '''
        grid1 = self('tfbi_grid1_zeros')
        for k in self.INDEX1_KEYS:
            k_index = f'{k}_index'
            if k_index not in array.coords:
                continue
            gdim = grid1.coords[k].dims[0]
            gcvalk = grid1.coords[k]
            acvalk = array.coords[k_index]
            if acvalk.ndim == 0:  # scalar coord, don't need to worry about array dims
                to_assign = gcvalk.isel({gdim: acvalk.item()}).values
                array = array.assign_coords({k: to_assign})
            elif acvalk.ndim == 1:  # need to determine which array dim has k_index coord
                to_assign = gcvalk.isel({gdim: acvalk.values}).values
                adim = acvalk.dims[0]
                array = array.assign_coords({k: (adim, to_assign)})
            else:  # acvalk.ndim >= 2
                errmsg = f'assign_tfbi_index1_coords when array[{k_index!r}].ndim > 1'
                raise DimensionalityError(errmsg)
        return array
