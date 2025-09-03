"""
File Purpose: binding xarray-related methods to classes defined elsewhere in tools.
(No other xarray_tools file should import this one.)
(This is to avoid circular dependencies.
    E.g. DictOfSimilar is defined in iterables.py,
    and should have the to_ds() method, which relies on some xarray_tools,
    but iterables.py is imported into various xarray_tools files already.)
"""
import xarray as xr

from .xarray_coords import xarray_str_coords
from ..docs_tools import format_docstring
from ..iterables import DictOfSimilar
from ..oop_tools import Binding
from ...errors import InputError, InputConflictError

binding = Binding(locals())


### --------------------- DictOfSimilar.to_da and .to_ds --------------------- ###

with binding.to(DictOfSimilar):
    # # # CONVERT DictOfSimilar TO XARRAY OBJECT # # #
    @binding
    def to_ds(self, da_dim=None, *, var=None, drop_coords=False, str_coords=False, item=False,
              errors_ok=False):
        '''return Dataset based on values in self.
        The default behavior of this method is equivalent to:
            return xr.Dataset(self)

        The main reason to use to_ds is to do common processing steps on the values first.
        No processing steps will be attempted by default.
        Providing inputs can enable various steps, in this order:
            (1) replace values with value[var]
            (2) convert values to DataArray via value.to_dataarray(da_dim)
            (3) drop some coords from each value
            (4) convert values' coords to strings via xarray_str_coords
            (5) convert values to scalars via value.item()
        Input options described below.

        var: None, str, or iterable of str.
            if provided, will get value[var] for each value in self.
        da_dim: None or str
            if provided, will call value.to_dataarray(da_dim) for each value in self.
        drop_coords: bool, str, or list of strs
            whether to call value.drop_vars(...) for each value in self.
            True --> value.drop_vars(value.coods)
            str or list of strs --> value.drop_vars(drop_coords)
        str_coords: bool, str, or list of strs
            whether to call xarray_str_coords on each value in self.
            True --> converts all coords' values to strs.
            str or list of strs --> xarray_str_coords(value, str_coords, promote=True)
        item: bool
            whether to call value.item() for each value in self.
        errors_ok: bool
            whether to ignore simple errors during processing.
            if True:
                var non-None but value not dict or Dataset --> skip this step.
                da_dim non-None but values are not Datasets --> skip this step.
                drop_coords --> value.drop_vars(drop_coords, errors='ignore').
                str_coords --> xarray_str_coords(value, str_coords, missing_ok=True).
                item but value.item() fails with ValueError or AttributeError --> skip this step.

        Example:
            mc = pc.MultiCalculator(...)
            dos = mc('mean_n', snap=7)   # depends on 'fluid' dim, but also has 'snap' and 't' coords.
            n_vals = dos.to_ds(str_coords='fluid', drop_coords=('snap', 't'))
            # str_coords='fluid' because 'fluid' might be different objects for each calculator
            # drop_coords=('snap', 't') because 'snap' and 't' info won't necessarily agree across all calculators.
        '''
        result = {k: v for k, v in self.items()}
        if var is not None:
            if isinstance(var, str):
                var = [var]
            for k, v in result.items():
                if not isinstance(v, dict) and not isinstance(v, xr.Dataset):
                    if errors_ok:
                        continue
                    else:
                        errmsg = (f'provided var={var!r}, but value not a dict or Dataset, and errors_ok=False.'
                                  f' Got value of type={type(v)}, at key={k!r}.')
                        raise InputError(errmsg)
                result[k] = v[var]
        if da_dim is not None:
            for k, v in result.items():
                if not isinstance(v, xr.Dataset):
                    if errors_ok:
                        continue
                    else:
                        errmsg = (f'provided da_dim={da_dim!r}, but value not a Dataset, and errors_ok=False.'
                                  f' Got value of type={type(v)}, at key={k!r}.')
                        raise InputError(errmsg)
                result[k] = v.to_dataarray(da_dim)
        if drop_coords:
            for k, v in result.items():
                to_drop = list(v.coords) if drop_coords == True else drop_coords
                try:
                    result[k] = v.drop_vars(to_drop, errors='ignore' if errors_ok else 'raise')
                except Exception as e:
                    if not errors_ok:
                        errmsg = f'provided drop_coords={drop_coords!r}, but crashed during drop_vars, and errors_ok=False.'
                    else:
                        errmsg = f"crash in drop_vars({drop_coords!r}, errors='ignore') -- not sure why."
                    raise Exception(errmsg) from e
        if str_coords:
            for k, v in result.items():
                try:
                    result[k] = xarray_str_coords(v, str_coords, promote=True, missing_ok=errors_ok)
                except Exception as e:
                    if not errors_ok:
                        errmsg = (f'provided str_coords={str_coords!r}, but crashed during xarray_str_coords, '
                                  f'and errors_ok=False.')
                    else:
                        errmsg = f"crash in xarray_str_coords(arr, {str_coords!r}, missing_ok=True) -- not sure why."
                    raise Exception(errmsg) from e
        if item:
            for k, v in result.items():
                try:
                    result[k] = v.item()
                except (ValueError, AttributeError) as e:
                    if not errors_ok:
                        errmsg = (f'provided item=True, but crashed during value.item(), and errors_ok=False.'
                                  f' Got value of type={type(v)}, at key={k!r}.')
                        raise InputError(errmsg) from e
        return xr.Dataset(result)

    @binding
    @format_docstring(to_ds_doc=to_ds.__doc__)
    def to_da(self, dim='variable', *, ds=False,
              da_dim=None, var=None, drop_coords=False, str_coords=False, item=False,
              errors_ok=False, **kw_to_ds):
        '''return DataArray based on values in self.
        The default behavior of this method is equivalent to:
            return xr.Dataset(self).to_dataarray(dim=dim)

        The other inputs enable to do some processing steps on self.values first.
        If passing any inputs other than `dim` and `ds`, self.to_da(dim, **kw) is equivalent to:
            return self.to_ds(**kw).to_dataarray(dim=dim)

        dim: str
            name of new dimension, across which to stack the data_vars from the dataset.
        ds: bool
            whether to convert result back into a Dataset.
            shorthand for the pattern:
                self.to_ds(dim, da_dim='dadim', **kw).to_dataset('dadim')
            Useful e.g. if self.values are datasets already,
                and the goal is to end up with a Dataset just like each value in self,
                but with the result also having the new `dim` dimension (with size==len(self))
            if True, cannot also provide `da_dim`, and internally uses da_dim='__da_dim_internal__'

        Docs for to_ds() copied below, for convenience:
        -----------------------------------------------
        {to_ds_doc}
        '''
        if ds:
            if da_dim is not None:
                raise InputConflictError('cannot provide both ds=True and da_dim!=None.')
            else:
                da_dim = '__da_dim_internal__'
        as_ds = self.to_ds(da_dim=da_dim, var=var, drop_coords=drop_coords,
                        str_coords=str_coords, item=item, errors_ok=errors_ok, **kw_to_ds)
        result = as_ds.to_dataarray(dim=dim)
        if ds:
            result = result.to_dataset(da_dim)
        return result

    @binding
    def to_xr(self, dim='variable', da_dim=None, *,
              var=None, drop_coords=False, str_coords=False, item=False,
              errors_ok=False, **kw_to_ds):
        '''return xarray.DataArray or Dataset, stacking values in self along the new dimension.
        This is shorthand for self.to_da() or self.to_ds()
            (depending on `da_dim` and whether self.values are already xarray.Dataset objects).

        dim: str
            the new dimension, along which to stack values from self.
        da_dim: None or str
            if provided, will call value.to_dataarray(da_dim) for each value in self.

        If da_dim provided or if there are no Dataset values in self,
            result will be a DataArray, as per self.to_da(dim, ds=False, da_dim=da_dim, **kw).
        Otherwise, if all self.values are Datasets,
            result will be a Dataset, as per self.to_da(dim, ds=True, da_dim=None).
        Otherwise (only some values are Datasets, and da_dim not provided),
            crash with InputError.

        The remaining kwargs go to self.to_ds() (see help(self.to_ds) for details):
            var: None, str, or iterable of str.
                if provided, will get value[var] for each value in self.
            drop_coords: bool, str, or list of strs
                whether to call value.drop_vars(...) for each value in self.
            str_coords: bool, str, or list of strs
                whether to call xarray_str_coords on each value in self.
            item: bool
                whether to call value.item() for each value in self.
            errors_ok: bool
                whether to ignore simple errors during processing.
        '''
        kw_to_ds.update(var=var, drop_coords=drop_coords, str_coords=str_coords, item=item, errors_ok=errors_ok)
        if (da_dim is not None) or not any(isinstance(v, xr.Dataset) for v in self.values()):
            return self.to_da(dim=dim, ds=False, da_dim=da_dim, **kw_to_ds)
        elif all(isinstance(v, xr.Dataset) for v in self.values()):
            return self.to_da(dim=dim, ds=True, da_dim=None, **kw_to_ds)
        else:
            errmsg = ('to_xr cannot decide whether to return DataArray or Dataset, '
                      'when some values are Datasets and some are not, and da_dim=None.\n'
                      'Consider using to_da or to_ds directly instead.')
            raise InputConflictError(errmsg)
