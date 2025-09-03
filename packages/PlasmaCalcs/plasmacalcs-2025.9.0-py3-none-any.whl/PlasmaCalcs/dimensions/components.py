"""
File Purpose: Component, ComponentList, ComponentDimension, ComponentHaver
"""
import xarray as xr

from .dimension_tools import (
    DimensionValue, DimensionValueList, string_int_lookup,
    Dimension, DimensionHaver,
)
from ..errors import ComponentKeyError, ComponentValueError, InputError
from ..tools import is_integer

### --------------------- Component & ComponentList --------------------- ###

class Component(DimensionValue):
    '''a single vector component coordinate (e.g. x, y, or z).
    Knows how to be converted to str and int. e.g. 'y' or 1.

    s: string or None
        str(self) --> s. if None, cannot convert to str.
    i: int or None
        int(self) --> i. if None, cannot convert to int.

    Note: not related to "coordinates", e.g. location in space.
    '''
    def __init__(self, s=None, i=None):
        super().__init__(s, i)


class ComponentList(DimensionValueList):
    '''list of vector component coordinates.'''
    _dimension_key_error = ComponentKeyError
    value_type = Component

    @classmethod
    def from_strings(cls, strings):
        '''return ComponentList from iterable of strings. (i will be determined automatically.)'''
        return cls(Component(s, i) for i, s in enumerate(strings))

    @classmethod
    def from_array(cls, array):
        '''return ComponentList from 0D or 1D array.
        array values should be Component objects, strings, or ints.
            Component objects --> use as-is
            strings --> if 'x', 'y', or 'z', use XYZ.get(string).
                        Else, use Component(s, i=i) for i in range(len(array))
            ints --> if 0, 1, or 2, use XYZ.get(int).
                     Else, use Component(i=i) for i in array
        '''
        # [TODO] use super() instead of repeating code from DimensionValueList.from_array?
        if array.ndim == 0:
            values = [array.item()]
        elif array.ndim == 1:
            values = array.values
        else:
            errmsg = f'{cls.__name__}.from_array expects array.ndim=0 or 1; got ndim={array.ndim}'
            raise DimensionalityError(errmsg)
        result = []
        for i, v in enumerate(values):
            if isinstance(v, cls.value_type):
                result.append(v)
            elif (isinstance(v, str) or isinstance(v, int)) and v in cls.value_type.XYZ:
                result.append(cls.value_type.XYZ.get(v))
            elif isinstance(v, str):
                result.append(cls.value_type(v, i=i))
            elif is_integer(v):
                result.append(cls.value_type(i=v))
            else:
                errmsg = (f'{cls.__name__}.from_array got unexpected value type at index {i}.\n'
                            f'Expected {cls.value_type.__name__}, str, or int; got value={v!r}.')
                raise InputError(errmsg)
        return cls(result)
        

XYZ = ComponentList.from_strings('xyz')
X, Y, Z = XYZ
YZ_FROM_X = string_int_lookup({X:(Y,Z), Y:(Z,X), Z:(X,Y)})  # right-handed coord system x,y,z given x.

Component.YZ_FROM_X = YZ_FROM_X  # add to Component class for convenience.
Component.XYZ = XYZ  # add to Component class for convenience.

XHAT = xr.DataArray([1,0,0], coords={'component': XYZ})
YHAT = xr.DataArray([0,1,0], coords={'component': XYZ})
ZHAT = xr.DataArray([0,0,1], coords={'component': XYZ})


### --------------------- ComponentDimension, ComponentHaver --------------------- ###

class ComponentDimension(Dimension, name='component', plural='components',
                     value_error_type=ComponentValueError, key_error_type=ComponentKeyError):
    '''component dimension, representing current value AND list of all possible values.
    Also has various helpful methods for working with this Dimension.
    '''
    pass  # behavior inherited from Dimension.


@ComponentDimension.setup_haver
class ComponentHaver(DimensionHaver, dimension='component', dim_plural='components'):
    '''class which "has" a ComponentDimension. (ComponentDimension instance will be at self.component_dim)
    self.component stores the current vector component (possibly multiple). If None, use self.components instead.
    self.components stores "all possible vector components" for the ComponentHaver.
    Additionally, has various helpful methods for working with the ComponentDimension,
        e.g. current_n_component, iter_components, take_component.
        See ComponentDimension.setup_haver for details.

    components defaults to XYZ (==ComponentList.from_strings('xyz'))
    '''
    def __init__(self, *, component=None, components=XYZ, **kw):
        super().__init__(**kw)
        if components is not None: self.components = components
        self.component = component
