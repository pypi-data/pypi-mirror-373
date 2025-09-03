"""
File Purpose: tools to create grids with xarray
"""
import numpy as np
import xarray as xr

from ..iterables import is_iterable
from ..properties import alias
from ..docs_tools import format_docstring
from ..sentinels import UNSET
from ...errors import (
    InputError, InputMissingError, InputConflictError,
    DimensionSizeError,
)


### --------------------- xr1d --------------------- ###

def xr1d(arraylike, name, *, coords=dict(), **kw_data_array):
    '''create a 1D xarray.DataArray from arraylike, using name for array, dim, & coord.
    Equivalent: xr.DataArray(arraylike, coords={name: arraylike}, name=name, dims=name)

    name: str
        name of the array. Result name, dim, and coord will all use this name.
    coords: dict
        if provided, update default coords using this dict.
        E.g. xr1d([1,2,3], 'x', coords={'y': 7}) coords will be {'x': [1,2,3], 'y': 7}.
        E.g. xr1d([1,2,3], 'x', coords={'x': [1,2,3]+10}) coord for 'x' will be [11,12,13].

    Example: xr1d([1,7,3], 'x')
        <xarray.DataArray 'x' (x: 3)> Size: 24B
        array([1, 7, 3])
        Coordinates:
          * x        (x) int64 24B 1 7 3
    '''
    if not isinstance(name, str):
        raise InputError(f'expected str name, but got name={name!r}')
    coords = {name: arraylike, **coords}
    return xr.DataArray(arraylike, dims=[name], coords=coords, name=name, **kw_data_array)


### --------------------- xarray_range --------------------- ###

def xrrange(range_info, name='range', *, coords=dict(), **kw_data_array):
    '''create a 1D xarray.DataArray of np.arange(*range_info), using name for array, dim, & coord.
    if range_info is a single number, use np.arange(range_info) instead.
    Equivalent: xr.DataArray(np.arange(*range_info), coords={name: np.arange(*range_info)}, ...)
    
    range_info: int or iterable of 1, 2, or 3 ints (or None)
        (will be passed directly to np.arange.)
        1 int provided --> stop
        2 ints provided --> start, stop
        3 ints provided --> start, stop, step
    name: str
        name of the range. Result name, dim, and coord will all use this name.
    coords: dict
        if provided, update default coords using this dict.
        E.g. xrrange(4, 'x', coords={'y': 7}) coords will be {'x': np.arange(4), 'y': 7}.
        E.g. xrrange(4, 'x', coords={'x': np.arange(4)+10}) coord for 'x' will be [10,11,12,13].

    Example: xrrange(4, 'x')  # ==xr.DataArray(np.arange(4), coords={'x': np.arange(4)}, name='x')
        <xarray.DataArray 'x' (x: 4)> Size: 32B
        0 1 2 3
        Coordinates:
          * x        (x) int64 32B 0 1 2 3
    '''
    if is_iterable(range_info):
        if len(range_info) == 0 or len(range_info) > 3:
            raise ValueError(f'expected range_info to be 1, 2, or 3 ints, but got len={len(range_info)}')
    else:
        range_info = [range_info]
    arange = np.arange(*range_info)
    return xr1d(arange, name, coords=coords, **kw_data_array)

xarray_range = xrrange  # alias to xrrange


### --------------------- XarrayGrid --------------------- ###

class XarrayGrid():
    '''class to help with making xarray.DataArray grids.
    call self (e.g.: self()) or self.grid() to get the grid as an xarray.DataArray.
    
    intended to be "immutable" after creation;
        altering self.min, self.max or other attrs may produce unexpected results.

    Inputs and outputs will always be in linear space (even if logspace=True)!


    --- Params related to lims ---

        min: None, number, DataArray, or callable
            min value (or array of min values)
            None --> infer from max and other params.
            callable f --> infer min = f(max)
        max: None, number, DataArray, or callable
            max value (or array of max values)
            None --> infer from min and other params.
            callable f --> infer max = f(min)
        span: None or number
            max - min. None = "unspecified".
            only allowed if min or max is None.
        ratio: None or number
            max / min. None = "unspecified".
            only allowed if min or max is None.

    --- Params related to grid size & spacing ---
        N: None or number
            number of points in grid. None = "unspecified"
        step: None or number
            step size between points (in linear space). None = "unspecified"
            if provided, implies logspace=False.
        logspace: None or bool
            whether the grid will be evenly spaced in log-space.
            None --> True if provided logstep; False if provided N or step.
            True --> must have provided N or logstep.
            False --> must have provided N or step.
        logstep: None or number
            step size between points, in log-space (base 10). None = "unspecified"
            if provided, implies logspace=True.
        inclusive: tuple of 2 bools
            whether to include min and max in the output.
        reverse: bool
            whether to reverse the output when creating grid.
            Equivalent to using result.isel(grid_dim=slice(None, None, -1)),
                but replacing 'grid_dim' with the appropriate name.

    --- Other params ---
        name: str
            result.name; also result.assign_coords({name:result})
            (ops with result keep coords[name], e.g. result + 10, or result * other_array)
        dim: None or str
            grid dimension. For scalar min & max, dim=name works great & intuitively.
            However, when self.array_lims, dim cannot equal name,
                because result will be n+1 dimensional (n=ndims from max-min),
                so setting result.assign_coords({name:result}) would fail if name is a dim.
            None --> dim=name if not self.array_lims else '{name}_dim'
            str --> use dim.format(name=name).
        math_coord: bool or str
            whether to add coord related to the grid-producing math, if self.array_lims.
            default name '{name}_normed', with values a 1D array from 0 to 1, such that:
                if linspace, result = min + (max - min) * coord
                if logspace, result = 10**(log10(min)+(log10(max)-log10(min))*coord)
            str --> use this coord, after doing math_coord.format(name=name).
        N_min: UNSET, None or number
            if provided, tells minimum allowed number of points in grid.
            None --> no minimum. UNSET --> use type(self).N_min (default=2)
        N_max: UNSET, None or number
            if provided, tells maximum allowed number of points in grid.
            None --> no maximum. UNSET --> use type(self).N_max (default=1e8)

    --- notes about result coords ---
        result.name = `name`
        result.coords[name] == result.
        result.dims = [dim, *dims from min and/or max (broadcasted appropriately)]
        If inputs are scalars:
            dim = `name`, unless explicitly provided `dim`.
                Either way, then use dim.format(name=name).
            result.dims = [dim]
            if dim == name, no additional coords added to result,
            otherwise, add coord: result[name] = result.
        If inputs are arrays, 
            dim = '{name}_dim' unless explicitly provided. 
                Either way, then use dim.format(name=name).
            result.dims = [dim, *dims from min and/or max]
            dim == name is NOT allowed.
            always add coord: result[name] = result
            if math_coord=True, may also add coord '{name}_normed'

    --- bookkeeping - values computed during init ---
    (__init__ computes these. Here is some documentation about what they mean.)

        self.step_param: 'N', 'step', or 'logstep'
            tells which step-related param was provided.
            (exactly 1 of these must be provided, else will crash.)
        self.array_lims: bool
            tells whether min or max is an array.
    '''
    DEFAULT_DIM = '{name}_dim'  # used when inputs are arrays, unless dim explicitly provided.
    NORMED_COORD = '{name}_normed'

    N_min = 2
    N_max = 1e8

    def __init__(self, min=None, max=None, N=None, name='grid', *, step=None,
                 span=None, ratio=None,
                 logspace=None, logstep=None,
                 inclusive=(True, True), reverse=False,
                 dim=None, math_coord=False,
                 N_min=UNSET, N_max=UNSET):
        self.init_step_params(N=N, step=step,
                              logspace=logspace, logstep=logstep,
                              inclusive=inclusive)
        self.reverse = reverse
        if N_min is not UNSET: self.N_min = N_min
        if N_max is not UNSET: self.N_max = N_max
        self.init_lims(min=min, max=max, span=span, ratio=ratio)
        self.init_labels(name=name, dim=dim, math_coord=math_coord)

    def init_step_params(self, *, N, step, logspace, logstep, inclusive):
        '''initialize N, step, logspace, logstep, inclusive from kwargs.
        Also sets self.step_param = 'N', 'step', or 'logstep'
        '''
        kw_step_input = dict(N=N, step=step, logstep=logstep)
        provided = [k for k, v in kw_step_input.items() if v is not None]
        if len(provided) == 0:
            raise InputMissingError('must provide one of: N, step, logstep.')
        if len(provided) >= 2:
            errmsg = f'expected only one of: N, step, logstep; got values for: {provided}'
            raise InputConflictError(errmsg)
        step_param = provided[0]
        self.step_param = step_param
        # bookkeeping for logspace
        if logspace is None:  # then, infer it:
            if step_param in ['N', 'step']:
                logspace = False
            elif step_param in ['logstep']:
                logspace = True
            else:
                assert False, 'coding error if reached this line'
        elif (logspace) and (step_param == 'step'):
            raise InputConflictError('logspace=True incompatible with step. Use N or logstep instead.')
        elif (not logspace) and (step_param == 'logstep'):
            raise InputConflictError('logspace=False incompatible with logstep. Use N or step instead.')
        # setting params internally
        self.N = N
        self.step = step
        self.logspace = logspace
        self.logstep = logstep
        self.inclusive = inclusive

    def init_lims(self, *, min, max, span, ratio):
        '''initialize self.min, max, span, and ratio. Also calls callables.
        Also sets self.array_lims = bool (True if min or max is an array).
        Also, if provided min and max, but np.any(min > max), raise InputConflictError.
        '''
        if callable(min):
            min = min(max)
        if callable(max):
            max = max(min)
        if min is None and max is None: raise InputMissingError('must provide min or max.')
        if span is None and ratio is None:
            if min is None: raise InputMissingError('must provide min, span, or ratio.')
            if max is None: raise InputMissingError('must provide max, span, or ratio.')
        if min is not None and max is not None:
            check = min > max  # <-- bad if True anywhere...
            if np.any(check):
                if getattr(check, 'ndim', 0) > 0:
                    errmsg = f'min > max (at {int(check.sum())} points, out of {check.size}).'
                else:
                    errmsg = f'min > max... cannot make grid.'
                raise InputConflictError(errmsg)
        if min is not None and max is not None:
            if span is not None: 
                raise InputConflictError('cannot provide span when providing both min & max.')
            if ratio is not None:
                raise InputConflictError('cannot provide ratio when providing both min & max.')
        if span is not None and ratio is not None:
            raise InputConflictError('cannot provide both span and ratio.')
        if getattr(span, 'ndim', 0) > 0:
            raise InputError(f'non-scalar span; got span=\n{span}')
        if getattr(ratio, 'ndim', 0) > 0:
            raise InputError(f'non-scalar ratio; got ratio=\n{span}')
        self.min = min
        self.max = max
        self.span = span
        self.ratio = ratio
        self.array_lims = (isinstance(min, xr.DataArray) or isinstance(max, xr.DataArray))
        if self.array_lims:
            if self.step_param=='step' and self.span is None:
                errmsg = ("array_lims=True when providing 'step', only allowed if provided span too.\n"
                          "Either provide 'span' (and leave ratio=None, and min=None or max=None),\n"
                          "or provide 'N' (and leave step=None).")
                raise InputConflictError(errmsg)
            if self.step_param=='logstep' and self.ratio is None:
                errmsg = ("array_lims=True when providing 'logstep', only allowed if provided ratio too.\n"
                          "Either provide 'ratio' (and leave span=None, and min=None or max=None),\n"
                          "or provide 'N' (and leave logstep=None).")
                raise InputConflictError(errmsg)
        
    def init_labels(self, *, name, dim, math_coord):
        '''initialize self.name, dim, and math_coord, using defaults if needed.
        result depends on whether self.min and max are arrays (i.e. self.array_lims).
        See help(type(self)) for more details.
        '''
        self.name = name
        if dim is None:
            dim = self.DEFAULT_DIM if self.array_lims else name
        if self.array_lims and dim == name:
            errmsg = (f'name==dim (=={dim!r}) when self.array_lims==True, is not allowed.\n'
                      'grid result[name] == result.values which will vary across array_lims dims,\n'
                      'so name cannot equal a dimension name, since result[name] will be >1D.')
            raise InputConflictError(errmsg)
        dim = dim.format(name=name)
        self.dim = dim
        if math_coord == True:
            if self.varied_step:
                math_coord = self.NORMED_COORD
            else:
                math_coord = self.OFFSET_COORD
        if isinstance(math_coord, str):
            math_coord = math_coord.format(name=name)
        self.math_coord = math_coord

    # # # GETTING RELEVANT PARAMS # # #
    def get_N_full(self):
        '''return N as if inclusive=(True, True). infer N if needed,
        and ensuring actual N is within acceptable range N_min < N < N_max.

        might return a non-integer; if that occurs, self.grid() will handle it properly.
        '''
        step_param = self.step_param
        inclusive_adjust = (0 if self.inclusive[0] else 1) + (0 if self.inclusive[1] else 1)
        if step_param == 'N':
            result = self.N + inclusive_adjust  # easiest case possible!!
        else:
            span = self.span
            ratio = self.ratio
            if step_param == 'step':
                if span is None:
                    min, max = self.get_lims()
                    span = max - min
                result = 1 + span / self.step
            elif step_param == 'logstep':
                if ratio is None:
                    min, max = self.get_lims()
                    ratio = max / min
                result = 1 + np.log10(ratio) / self.logstep
            else:
                assert False, 'coding error'
            result = result
        actual_N = int(result - inclusive_adjust)
        intN = int(result)
        if intN == result:
            result = intN
        else:  # self._adjust_if_nonint_N later will set inclusive[0]=True or inclusive[1]=True,
            # so here we need to adjust actual_N by adding 1.
            actual_N = actual_N + 1
        if self.N_min is not None and actual_N < self.N_min:
            raise DimensionSizeError(f'N={actual_N} too small! (N_min={self.N_min})')
        if self.N_max is not None and actual_N > self.N_max:
            raise DimensionSizeError(f'N={actual_N} too large! (N_max={self.N_max})')
        return result

    def get_N(self):
        '''return N, appropriate given self.inclusive.
        
        might return a non-integer; if that occurs, self.grid() will handle it properly.
        '''
        N_full = self.get_N_full()
        inclusive_adjust = (0 if self.inclusive[0] else 1) + (0 if self.inclusive[1] else 1)
        return N_full - inclusive_adjust

    def get_lims(self):
        '''return (self.min, self.max), inferring (from span or ratio) if needed.'''
        min = self.min
        max = self.max
        span = self.span
        ratio = self.ratio
        if span is not None:
            if min is None:
                min = max - self.span
            if max is None:
                max = min + self.span
        elif ratio is not None:
            if min is None:
                min = max / self.ratio
            if max is None:
                max = min * self.ratio
        return min, max

    def _adjust_if_nonint_N(self, min, max, N, inclusive):
        '''returns min, max, N, and inclusive; adjusted appropriately if N is not an integer.
        (if N is an integer, returns min, max, N unchanged.)
        (N should be N_full, i.e. the value of N as if inclusive=(True, True); e.g. from self.get_N_full())

        The adjustment depends on self.inclusive.
        if inclusive = (True, True), crash.
        else, use original step (or logstep) while dropping the input value for max or min.
            (if inclusive=(False, True), keep original max, adjust original min;
             else, adjust original max, keep original min.)

        N will always be rounded down to the nearest integer.
        '''
        intN = int(N)
        if N == intN:
            return min, max, intN, inclusive
        elif inclusive == (True, True):
            errmsg = (f'non-integer N={N} incompatible with inclusive=(True, True);\nProbably provided '
                      'step (or logstep) which does not evenly divide span (or ratio) between max and min.\n'
                      'Consider using inclusive=(True,False) or (False,False), to use original step (or logstep),\n'
                      'while dropping the input value for max.')
            raise InputConflictError(errmsg)
        elif inclusive[1]:
            if self.step_param == 'step':
                min = max - (intN-1) * self.step
                inclusive = (True, inclusive[1])  # adjusted min such that final point is at new min; old min still not included.
            elif self.step_param == 'logstep':
                min = max / 10**((intN-1) * self.logstep)
                inclusive = (True, inclusive[1])  # adjusted min such that final point is at new min; old min still not included.
            else:
                raise NotImplementedError(f'[TODO] handle non-integer N when step_param={self.step_param!r}')
        else:
            if self.step_param == 'step':
                max = min + (intN-1) * self.step
                inclusive = (inclusive[0], True)  # adjusted max such that final point is at new max; old max still not included.
            elif self.step_param == 'logstep':
                max = min * 10**((intN-1) * self.logstep)
                inclusive = (inclusive[0], True)  # adjusted max such that final point is at new max; old max still not included.
            else:
                raise NotImplementedError(f'[TODO] handle non-integer N when step_param={self.step_param!r}')
        return min, max, intN, inclusive

    # # # CREATING THE GRID # # #
    grid = alias('__call__')

    def __call__(self):
        '''return grid from self.'''
        if self.array_lims:
            return self.array_grid()
        else:
            return self.scalar_grid()

    def scalar_grid(self):
        '''return grid from scalar min to scalar max, with int(self.get_N()) points.
        fails with InputError if min or max are arrays (i.e. if self.array_lims.)
        '''
        if self.array_lims:
            raise InputError('cannot make scalar grid when min or max are arrays.')
        N = self.get_N_full()
        min, max = self.get_lims()
        inclusive = self.inclusive
        min, max, N, inclusive = self._adjust_if_nonint_N(min, max, N, inclusive)
        name = self.name
        d = self.dim
        if self.logspace:
            grid = np.logspace(np.log10(min), np.log10(max), N)
        else:
            grid = np.linspace(min, max, N)
        if not inclusive[0]:
            grid = grid[1:]
        if not inclusive[1]:
            grid = grid[:-1]
        if self.reverse:
            grid = grid[::-1]
        result = xr.DataArray(grid, dims=[d], coords={name: (d, grid)}, name=name)
        return result

    def math_grid01(self):
        '''return XarrayGrid(0, 1, N=self.get_N()).grid(), maybe removing endpoints (see: inclusive),
        and labeled for helping with array_grid().
        '''
        N = self.get_N()
        math_coord = '_internal_name_' if self.math_coord==False else self.math_coord
        grid01_obj = XarrayGrid(0, 1, N=N, name=math_coord, dim=self.dim, inclusive=self.inclusive)
        result = grid01_obj.scalar_grid()
        if self.math_coord==False:
            result = result.drop_vars('_internal_name_')
        return result

    def array_grid(self):
        '''return grid from array min to array max, with self.get_N() points along grid dimension.
        fails with InputError if min and max are both not arrays (i.e. not self.array_lims)
        '''
        if not self.array_lims:
            raise InputError('cannot make array grid when min and max are not arrays.')
        min, max = self.get_lims()
        dim = self.dim
        # make an evenly spaced grid from 0 to 1 then do array math to expand range to min & max.
        grid01 = self.math_grid01()
        if self.logspace:
            logmin = np.log10(min)
            logmax = np.log10(max)
            result = 10**(logmin + (logmax - logmin) * grid01)
        else:
            result = min + (max - min) * grid01
        result = result.rename(self.name).assign_coords({self.name: result})
        # reverse if needed
        if self.reverse:
            result = result.isel({dim: slice(None, None, -1)})
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        contents = []
        for mname, m in (('min', self.min), ('max', self.max)):
            if isinstance(m, xr.DataArray):
                name = '' if m.name is None else f'name={m.name!r}, '
                m = f'DataArray({name}sizes={dict(m.sizes)})'
            elif callable(m):
                if hasattr(m, '__name__'):
                    m = m.__name__
                else:
                    m = f'(callable of type={type(m).__name__})'
            contents.append(f'{mname}={m}')
        if self.span is not None:
            contents.append(f'span={self.span}')
        contents.append(f'{self.step_param}={getattr(self, self.step_param)}')
        if self.step_param == 'N' and self.logspace:
            contents.append('logspace=True')
        if self.inclusive != (True, True):
            contents.append(f'inclusive={self.inclusive}')
        contents.append(f'dim={self.dim!r}')
        return f'{type(self).__name__}({", ".join(contents)})'

@format_docstring(xarray_grid_docs=XarrayGrid.__doc__)
def xarray_grid(min=None, max=None, N=None, name='grid', *, step=None, span=None, ratio=None,
                 logspace=None, logstep=None, inclusive=(True, True), reverse=False,
                 dim=None, math_coord=False, N_max=UNSET, N_min=UNSET):
    '''create and return a grid, via XarrayGrid(...).grid().
    (If you want to inspect the grid-making process more closely, use XarrayGrid instead)

    XarrayGrid docs copied below for convenience:
    ---------------------------------------------
    {xarray_grid_docs}
    '''
    grid = XarrayGrid(min=min, max=max, N=N, name=name, step=step, span=span, ratio=ratio,
                      logspace=logspace, logstep=logstep, inclusive=inclusive, reverse=reverse,
                      dim=dim, math_coord=math_coord, N_max=N_max, N_min=N_min)
    return grid()


### --------------------- xarray_angle_grid --------------------- ###

def xarray_angle_grid(min=0, max=360, N=None, name='ang', *, rad_in=False,
                      step=None, span=None,
                      radstep=None, degstep=None, radspan=None, degspan=None,
                      inclusive=(True, False), N_min=UNSET, N_max=UNSET):
    '''create and return a grid of angles; output will always be in [radians].
    (The default is to create a grid from 0 to 360 degrees, including 0 but not 360)

    The main advantage of this method is to make simple 1D angle grids.
    For more precise control, and/or 2D+ grids, use xarray_grid or XarrayGrid instead.

    min: None, number, or callable
        min value. None --> infer from max & span.
        callable f --> infer min [radians] = f(max [radians])
    max: None, number, or callable
        max value. None --> infer from min & span.
        callable f --> infer max [radians] = f(min [radians])
    N: None or number
        number of points in grid. None = "unspecified"
    name: str
        result.name; also result.assign_coords({name:result})
    rad_in: bool, default False.
        whether the inputs are in radians (if True) or degrees (if False).
    step: None or number
        step size between points, in same units as input (depends on rad_in). None = "unspecified"
    radstep: None or number
        step size between points, in radians. None = "unspecified"
    degstep: None or number
        step size between points, in degrees. None = "unspecified"
    span: None or number
        max - min, in same units as input (depends on rad_in). None = "unspecified"
    radspan: None or number
        max - min, in radians. None = "unspecified"
    degspan: None or number
        max - min, in degrees. None = "unspecified"
    inclusive: tuple of 2 bools
        whether to include min and max in the output.
    N_min: UNSET, None or number
        if provided, tells minimum allowed number of points in grid.
        None --> no minimum. UNSET --> use XarrayGrid.N_min default (==2)
    N_max: UNSET, None or number
        if provided, tells maximum allowed number of points in grid.
        None --> no maximum. UNSET --> use XarrayGrid.N_max default (==1e8)
    '''
    steps = dict(step=step, radstep=radstep, degstep=degstep)
    if sum([1 for v in steps.values() if v is not None]) > 1:
        raise InputConflictError(f'cannot provide more than one of: step, radstep, degstep; but got {steps}')
    spans = dict(span=span, radspan=radspan, degspan=degspan)
    if sum([1 for v in spans.values() if v is not None]) > 1:
        raise InputConflictError(f'cannot provide more than one of: span, radspan, degspan; but got {spans}')
    # convert all to radians:
    if not rad_in:
        if (min is not None) and (not callable(min)):
            min = np.deg2rad(min)
        if (max is not None) and (not callable(max)):
            max = np.deg2rad(max)
        if step is not None:
            step = np.deg2rad(step)
        if span is not None:
            span = np.deg2rad(span)
    if step is None:
        step = (None if degstep is None else np.deg2rad(degstep)) if radstep is None else radstep
    if span is None:
        span = (span if degspan is None else np.deg2rad(degspan)) if radspan is None else radspan
    # create & return grid:
    return xarray_grid(min=min, max=max, N=N, name=name, step=step, span=span,
                       inclusive=inclusive, N_min=N_min, N_max=N_max)
