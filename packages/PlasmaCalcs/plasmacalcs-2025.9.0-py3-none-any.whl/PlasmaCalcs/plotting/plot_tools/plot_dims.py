"""
File Purpose: methods related to dims for plotting.

See also: DEFAULTS.DIMS_INFER
"""

from ...errors import PlottingAmbiguityError, DimensionKeyError

from ...tools import (
    simple_tuple_property,
    NO_VALUE,
)
from ...defaults import DEFAULTS

### --------------------- inferring dimensions --------------------- ###

def infer_movie_dim(dims, dim=None, *, exclude=[], fail_ok=True):
    '''infer the dimension which movie frames should index.
    (if dim is provided, just return dim, after ensuring dim in dims)

    dims: iterable of strings
        all possible dims. Probably array.dims, if trying to infer from an array.
    dim: None or str
        the dimension which frames will index.
        if None, infer it, if possible:
            if len(dims)==1, use the only dim remaining from dims.
            otherwise, use the first dim from DEFAULTS.PLOT.DIMS_INFER['t'] which appears in dims, if possible.
            otherwise, failed to infer a dim; return None.
    exclude: iterable
        dims to exclude from dims, before inferring dim.
        E.g. if dims=('x', 'y', 'z', 't') and exclude=('x', 'y'), then infer from dims=('z', 't').
        Useful e.g. if it is already known which dims are used for x & y axes of the plot.
        Exclude can contain any values, e.g. exclude=('x', None) is fine.
    fail_ok: bool
        controls behavior when failing to infer dim:
        True --> return None
        False --> raise PlottingAmbiguityError
    '''
    dims = tuple(dims)  # compatible with generator iterables
    if dim is not None:
        if dim not in dims:
            raise DimensionKeyError(f'dim={dim!r} not found in dims={dims!r}')
        return dim
    # infer dim from dims
    dims = list(set(dims) - set(exclude))
    if len(dims)==1:
        return dims[0]
    for d in DEFAULTS.PLOT.DIMS_INFER['t']:
        if d in dims:
            return d
    # failed to infer dim.
    if fail_ok:
        return None
    raise PlottingAmbiguityError(f'failed to infer movie dim from dims={dims!r}')

def infer_xy_dims(dims, x=None, y=None, *, exclude=[], fail_ok=False):
    '''infer x and y dims from dims, if not provided.
    (if x and y are provided, just return x,y, after ensuring x,y in dims)

    dims: iterable of strings
        all possible dims. Probably array.dims, if trying to infer from an array.
    x: None or str
        the dimension which will index the plot's x axis.
        if None, infer it, if possible:
            if y is known, first set dims = dims without y.
            if len(dims)==1, use x=dims[0]
            otherwise, use the first dim from DEFAULTS.PLOT.DIMS_INFER['x'] which appears in dims, if possible.
            otherwise, try to infer y; might be able to infer x while inferring y.
    y: None or str
        the dimension which will index the plot's y axis.
        if None, infer it, if possible:
            if x is known, first set dims = dims without x.
            if len(dims)==1, use the only dim remaining from dims.
            otherwise, use the first dim from DEFAULTS.PLOT.DIMS_INFER['y'] which appears in dims, if possible.
            otherwise, if len(dims)==2 and x is None, use x, y = dims
    exclude: iterable
        dims to exclude from dims, before inferring x,y.
        E.g. if dims=('x', 'y', 'z', 't') and exclude=('x', 'y'), then infer from dims=('z', 't').
        Useful e.g. if it is already known which dims are used for x & y axes of the plot.
        Exclude can contain any values, e.g. exclude=('x', None) is fine.
    fail_ok: bool
        controls behavior when failing to infer dim:
        True --> return None for that dim
        False --> raise PlottingAmbiguityError
    '''
    dims = tuple(dims)  # compatible with generator iterables
    if (x is not None) and (x not in dims):
        raise DimensionKeyError(f'x={x!r} not found in dims={dims!r}')
    if (y is not None) and (y not in dims):
        raise DimensionKeyError(f'y={y!r} not found in dims={dims!r}')
    if (x is not None) and (y is not None):
        return (x, y)
    # infer x and/or y from dims
    dims = list(set(dims) - set(exclude))
    if x is None:
        if y is not None:
            dims = list(set(dims) - {y})
        if len(dims)==1:
            x = dims[0]
        if x is None:  # x is still None
            for dim in DEFAULTS.PLOT.DIMS_INFER['x']:
                if dim in dims:
                    x = dim
                    break
    if y is None:
        if x is not None:
            dims = list(set(dims) - {x})
        if len(dims)==1:
            y = dims[0]
        if y is None:  # y is still None
            for dim in DEFAULTS.PLOT.DIMS_INFER['y']:
                if dim in dims:
                    y = dim
                    break
        if y is None:  # y is still None
            if len(dims)==2 and x is None:
                x, y = dims
    # return result; first, crash if failed but not fail_ok.
    if not fail_ok:
        if (x is None) and (y is None):
            raise PlottingAmbiguityError(f'failed to infer x,y from dims={dims!r}')
        if x is None:
            raise PlottingAmbiguityError(f'failed to infer x from dims={dims!r}, y={y!r}')
        if y is None:
            raise PlottingAmbiguityError(f'failed to infer y from dims={dims!r}, x={x!r}')
    return (x, y)

def infer_xyt_dims(dims, *, x=None, y=None, t=None, exclude=[], xy_fail_ok=False, t_fail_ok=True):
    '''infer x, y, and t dims from dims, if not provided.
    (if x, y, and t are provided, just return x,y,t, after ensuring x,y,t in dims)

    dims: iterable of strings
        all possible dims. Probably array.dims, if trying to infer from an array.
        This function expects len(dims)==2 or 3, otherwise might behave strangely.
    x: None or str
        the dimension which will index the plot's x axis.
    y: None or str
        the dimension which will index the plot's y axis.
    t: None or str
        the dimension which will index the movie's frames.
    exclude: iterable
        dims to exclude from dims, before inferring x,y,t.
    xy_fail_ok, t_fail_ok: bool
        controls behavior when failing to infer a dim:
        True --> return None for that dim
        False --> raise PlottingAmbiguityError
        t_fail_ok corresponds to t; xy_fail_ok corresponds to x,y.

    see also: infer_xy_dims, infer_movie_dim, DEFAULTS.PLOT.DIMS_INFER
    '''
    dims = tuple(set(dims) - set(exclude))
    if len(dims) in (2,3):
        t = infer_movie_dim(dims, t, fail_ok=True)
    else:
        t = infer_movie_dim(dims, t, exclude=[x, y], fail_ok=True)
    x, y = infer_xy_dims(dims, x, y, exclude=[t], fail_ok=xy_fail_ok)
    if t is None:
        t = infer_movie_dim(dims, t, exclude=[x, y], fail_ok=t_fail_ok)
    return (x, y, t)


class PlotDimsMixin():
    '''adds methods for inferring plot dims, and properties for plot dims.
    subclasses should define plot_dims_attrs = dict(
        x = name of attr which stores the un-inferred dim for plot x axis
        y = name of attr which stores the un-inferred dim for plot y axis
        t = name of attr which stores the un-inferred dim for plot t axis (i.e. frames in a movie)
        dims = name of attr which stores the list of all possible dims, from which other dims might be inferred.
        t_necessary_if = name of attr which stores the condition under which t does not need to be inferred.
    ). If not all of these are provided, some (or all) InferrablePlotDimsMixin methods will crash.

    defines properties:
        x_plot_dim, y_plot_dim, t_plot_dim:
            infer the related dim (x,y,t, respectively),
            using values at plot_dims_attrs, and DEFAULTS.PLOT.DIMS_INFER.
            setting x_plot_dim=value also sets self.{plot_dims_attrs['x']}=value, etc.
        xy_plot_dims:
            (x_plot_dim, y_plot_dim); setting value also sets self.x_plot_dim and y_plot_dim.
        xyt_plot_dims:
            similar to xy_plot_dims, but for (x_plot_dim, y_plot_dim, t_plot_dim).

    For an example of using this Mixin, see XarrayImage.
    '''
    def _get_plot_dims_attr_value(self, x, default=NO_VALUE):
        '''get value of self.{plot_dims_attrs[x]}, where x = 'x', 'y', 't', 'dims', or 't_necessary_if'.'''
        attr = self.plot_dims_attrs[x]
        return getattr(self, attr) if default is NO_VALUE else getattr(self, attr, default)
    def _set_plot_dims_attr_value(self, x, value):
        '''set value of self.{plot_dims_attrs[x]}, where x = 'x', 'y', 't', 'dims', or 't_necessary_if'.'''
        attr = self.plot_dims_attrs[x]
        setattr(self, attr, value)

    @property
    def x_plot_dim(self):
        '''the dimension which is actually used to index the plot's x axis.
        setting self.x_plot_dim=value also sets self.{plot_dims_attrs['x']}=value.
        getting self.x_plot_dim will get self.{plot_dims_attrs['x']} if it is not None;
            otherwise, infer from self.{plot_dims_attrs['dims']}, self.{plot_dims_attrs['t']}, and self.{plot_dims_attrs['y']}.
        '''
        # [TODO][EFF] cache inferred value? (Only worthwhile if profiling reveals this is slow.)
        result = self._get_plot_dims_attr_value('x')
        if result is not None:
            return result
        x, y, t = self.infer_xyt_dims(xy_fail_ok=False, t_fail_ok=True)
        return x
    @x_plot_dim.setter
    def x_plot_dim(self, value):
        self._set_plot_dims_attr_value('x', value)

    @property
    def y_plot_dim(self):
        '''the dimension which is actually used to index the plot's y axis.
        setting self.y_plot_dim=value also sets self.{plot_dims_attrs['y']}=value.
        getting self.y_plot_dim will get self.{plot_dims_attrs['y']} if it is not None;
            otherwise, infer from self.{plot_dims_attrs['dims']}, self.{plot_dims_attrs['t']}, and self.{plot_dims_attrs['x']}.
        '''
        result = self._get_plot_dims_attr_value('y')
        if result is not None:
            return result
        x, y, t = self.infer_xyt_dims(xy_fail_ok=False, t_fail_ok=True)
        return y
    @y_plot_dim.setter
    def y_plot_dim(self, value):
        elf._set_plot_dims_attr_value('y', value)

    @property
    def t_plot_dim(self):
        '''the dimension which is actually used to index the movie's frames (i.e. the "time axis").
        setting self.t_plot_dim=value also sets self.{plot_dims_attrs['t']}=value.
        getting self.t_plot_dim will get self.{plot_dims_attrs['t']} if it is not None;
            otherwise, infer from self.{plot_dims_attrs['dims']}, self.{plot_dims_attrs['x']}, and self.{plot_dims_attrs['y']}
            if self.{plot_dims_attrs['t_necessary_if']}(), result might be None.
        '''
        result = self._get_plot_dims_attr_value('t')
        if result is not None:
            return result
        x, y, t = self.infer_xyt_dims(xy_fail_ok=True, t_fail_ok=True)
        if t is None:
            t_necessary_if = self._get_plot_dims_attr_value('t_necessary_if', default=lambda: True)
            if t_necessary_if():
                tattr = self.plot_dims_attrs['t']
                errmsg = f'failed to infer t_plot_dim (self.{tattr}) from dims={self.array.dims!r}, x={x!r}, y={y!r}'
                raise PlottingAmbiguityError(errmsg)
        return t
    @t_plot_dim.setter
    def t_plot_dim(self):
        self._set_plot_dims_attr_value('t', value)

    def infer_xyt_dims(self, *, xy_fail_ok=False, t_fail_ok=True):
        '''infers (x,y,t) dims from self.x, y, dim.
        xy_fail_ok, t_fail_ok: bool
            controls behavior when failing to infer a dim:
            True --> return None for that dim
            False --> raise PlottingAmbiguityError
            t_fail_ok corresponds to t; xy_fail_ok corresponds to x,y.

        see also: DEFAULTS.PLOT.DIMS_INFER, plotting.infer_xyt_dims, infer_xy_dims, infer_movie_dim
        '''
        x = self._get_plot_dims_attr_value('x')
        y = self._get_plot_dims_attr_value('y')
        t = self._get_plot_dims_attr_value('t')
        return infer_xyt_dims(self.array.dims, x=x, y=y, t=t, xy_fail_ok=xy_fail_ok, t_fail_ok=t_fail_ok)

    xy_plot_dims = simple_tuple_property('x_plot_dim', 'y_plot_dim',
                                         doc='''(self.x_plot_dim, self.y_plot_dim)''')
    xyt_plot_dims = simple_tuple_property('x_plot_dim', 'y_plot_dim', 't_plot_dim',
                                          doc='''(self.x_plot_dim, self.y_plot_dim, self.t_plot_dim)''')
