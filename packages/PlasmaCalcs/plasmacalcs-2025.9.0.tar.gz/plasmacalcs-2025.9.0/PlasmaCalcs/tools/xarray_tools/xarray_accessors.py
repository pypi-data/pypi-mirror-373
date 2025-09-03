"""
File Purpose: xarray attribute accessors.
accessing stuff via xr.DataArray.pc.{attr}, e.g. xr.DataArray.pc.differentiate(...)

# [TODO] __repr__ and help(). E.g. arr.pc.help() gives some help on how to get help,
#   arr.pc.help('') tells all available methods & docs,
#   arr.pc.help('searchstr') tells available methods with 'searchstr' in their name,
#   all similar to the PlasmaCalculator.help() function.
"""
import warnings

import xarray as xr

from ..properties import alias
from ..pytools import help_str
from ..sentinels import UNSET
from ...defaults import DEFAULTS
from ...errors import InputError


### --------------------- As accessors, on xarrays --------------------- ###
# access via xr.DataArray.pc.{attr}, e.g. xr.DataArray.pc.differentiate(...)

def xarray_register_dataarray_accessor_cls(name, *, warn_if_clsname_match=False):
    '''return class decorator which registers cls as an accessor for xarray.DataArray,
    as per xr.register_dataarray_accessor(name).

    warn_if_clsname_match: bool, default False
        whether to suppress AccessorRegistrationWarning,
            when xr.DataArray.name already exists AND cls.__name__ == xr.DataArray.name.

        This solves the issue that when doing pc=pc.reload(pc),
            (or otherwise using importlib.reload to reload the code attaching the accessor,)
            the code to attach the accessor would be run again, causing a warning.
            But that warning is confusing;
            it's almost certainly just overwriting the name defined by that code originally.
            Using warn_if_clsname_match=False will suppress the warning in that case.
    '''
    def decorated_register_dataaray_accessor(cls):
        with warnings.catch_warnings():  # <-- restore original warnings filter after this.
            if not warn_if_clsname_match:
                try:
                    xr_accessor = getattr(xr.DataArray, name)
                except AttributeError:
                    pass  # that's fine, we'll register cls as an accessor.
                else:
                    if xr_accessor.__name__ == cls.__name__:
                        # suppressing AccessorRegistrationWarning (from xr.register_dataarray_accessor(name))
                        warnings.filterwarnings('ignore', category=xr.core.extensions.AccessorRegistrationWarning)
            return xr.register_dataarray_accessor(name)(cls)
    return decorated_register_dataaray_accessor

# similar to above, but for dataset:
def xarray_register_dataset_accessor_cls(name, *, warn_if_clsname_match=False):
    '''return class decorator which registers cls as an accessor for xarray.Dataset,
    as per xr.register_dataset_accessor(name).

    warn_if_clsname_match: bool, default False
        whether to suppress AccessorRegistrationWarning,
            when xr.Dataset.name already exists AND cls.__name__ == xr.Dataset.name.
    '''
    def decorated_register_dataset_accessor(cls):
        with warnings.catch_warnings():  # <-- restore original warnings filter after this.
            if not warn_if_clsname_match:
                try:
                    xr_accessor = getattr(xr.Dataset, name)
                except AttributeError:
                    pass  # that's fine, we'll register cls as an accessor.
                else:
                    if xr_accessor.__name__ == cls.__name__:
                        # suppressing AccessorRegistrationWarning (from xr.register_dataset_accessor(name))
                        warnings.filterwarnings('ignore', category=xr.core.extensions.AccessorRegistrationWarning)
            return xr.register_dataset_accessor(name)(cls)
    return decorated_register_dataset_accessor


class _BoundObjCaller():
    '''remembers f & instance. calls f(instance.obj, *args, **kw).
    
    Helper class for pcAccessor so that the methods can be compatible with multiprocessing.
    '''
    def __init__(self, f, instance):
        self.f = f
        self.instance = instance
        self.__doc__ = f'caller of {help_str(f, blankline=True)}'
        #functools.update_wrapper(self, f)

    def __call__(self, *args, **kw):   # maybe self, instance, *args, **kw ?
        '''returns self.f(self.instance.obj, *args, **kw).'''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return self.f(self.instance.obj, *args, **kw)

    def __repr__(self):
        obj = self.instance.obj
        obj_info = f'{type(obj).__name__} at {hex(id(obj))}'
        f_info = f'{type(self.f).__name__} {self.f.__name__}'
        return f'<{type(self).__name__} of {f_info} for {obj_info}>'


class _ObjCaller():
    '''behaves like a bound method but calls f(self.obj, ...) instead of f(self, ...)'''
    def __init__(self, f):
        self.f = f
        self.__doc__ = f'caller of {help_str(f, blankline=True)}'

    def __get__(self, instance, owner):
        if instance is None:  # called on class, not instance
            return self
        else:
            return _BoundObjCaller(self.f, instance)

    def __repr__(self):
        f_info = f'{type(self.f).__name__} {self.f.__name__}'
        return f'<{type(self).__name__} of {f_info}>'


class XarrayAccessor():
    '''access attributes of DataArrays or Datasets.
    e.g. xr.DataArray.accessor_name.accessor_method(...).

    Not intended for direct use. See pcAccessor for example usage.
    Check cls.registry for details about available methods.
    [TODO] cls.help() which lists available methods...

    accessor_name: None or str
        name for accessor associated with this class.
        E.g., 'pc' for pcAccessor.
        None --> use accessor_name from parent class.
    access_type: UNSET, None, 'array', or 'dataset'
        which type of xarray objects methods registered here apply to (by default).
        UNSET --> use access_type from parent class.
        None --> methods apply to both DataArrays and Datasets.
        'array' --> methods apply to DataArrays only
        'dataset' --> methods apply to Datasets only.

    Implementation assumes when creating a new accessor name, you will follow the pattern:
        class customAccessor(XarrayAccessor, accessor_name='custom', access_type=None): ...
        class customArrayAccessor(customAccessor, access_type='array'): ...
        class customDatasetAccessor(customAccessor, access_type='dataset'): ...
    '''
    def __init_subclass__(cls, *, accessor_name=None, access_type=UNSET, **kwargs):
        super().__init_subclass__(**kwargs)
        if accessor_name is not None:
            cls.accessor_name = accessor_name
        if access_type is None:
            cls.registry = {}  # {name: (type, f)} for all registered methods.
            cls.attrs_registry = {}  # {name: (type, value)} for all registered attrs.
            cls.access_type_to_cls = {}   # {access_type: cls} for single-type access types.
            cls.alias_registry = {}  # {name: [aliases]} for all registered aliases.
        if access_type is not UNSET:
            cls.access_type = access_type
            if not hasattr(cls, 'access_type_to_cls'):
                errmsg = ('access_type_to_cls missing. Probably provided access_type != None, '
                          'for a class which does not inherit from a class with access_type=None.')
                raise NotImplementedError(errmsg)
            if access_type in (None, 'array', 'dataset'):
                if access_type in cls.access_type_to_cls:
                    errmsg = (f'Multiple accessors for access_type={access_type!r}: '
                             f'{cls.access_type_to_cls[access_type].__name__} and {cls.__name__}')
                    raise NotImplementedError(errmsg)
                cls.access_type_to_cls[access_type] = cls
                if access_type == 'array':
                    xarray_register_dataarray_accessor_cls(cls.accessor_name)(cls)
                if access_type == 'dataset':
                    xarray_register_dataset_accessor_cls(cls.accessor_name)(cls)
            else:
                raise InputError(f'Unexpected access_type: {access_type}')

    def __init__(self, xarray_obj):
        self.obj = xarray_obj

    # obj = weakref_property_simple('_obj', doc='''the xarray this object is attached to.''')
    # weakref actually not desireable.. if using it:
    #   e.g. xr.DataArray(0).pc.obj would be None; the array isn't stored so the weakref dies.
    #   meanwhile, arr=xr.DataArray(0); arr.pc.obj would be arr; the weakref didn't die.
    # [TODO][EFF] do xarray data accessors prevent original array from being garbage-collected?

    @classmethod
    def register(cls, f_or_name, *, aliases=[], totype=UNSET, _name=None):
        '''attaches method which applies f(self.obj, *args, **kw) to xr.DataArray.pc.{name}, then returns f.
        (in general, use cls.accessor_name, not necessarily 'pc'; 'pc' is for pcAccessor.)

        This ensures f can be accessed via xr.DataArray.pc.{name} or xr.Dataset.pc.{name}.
            pcAccessor.register --> available on both DataArrays and Datasets.
            pcArrayAccessor.register --> available on DataArrays only.
            pcDatasetAccessor.register --> available on Datasets only.

        f_or_name: str or callable
            str --> returns a function: f -> register(f, name=f_or_name)
            callable --> register this function then return it.
                        will be registered at _name if provided, else at f.__name__.
            This enables this method to be used directly as a decorator, or as a decorator factory.
        aliases: list of str
            aliases for f. Create alias property for each of these.
        totype: UNSET, None, 'array', or 'dataset'
            which type of xarray objects the registered method applies to.
            UNSET --> use cls.access_type.
            None --> methods apply to both DataArrays and Datasets.
            'array' --> methods apply to DataArrays only
            'dataset' --> methods apply to Datasets only.
        _name: str, optional
            name to register f at. If not provided, use f.__name__.
            Not intended to be provided directly.


        Examples (using pcAccessor subclass for concreteness):
            @pcAccessor.register
            def my_method1(xarray_object, arg1):
                print(arg1)
                print(xarray_obj)
            xr.DataArray(data).pc.my_method1(7)   # prints 7 then prints DataArray(data).
            xr.Dataset(data).pc.my_method1(5)   # prints 5 then prints Dataset(data).

            @pcAccessor.register(name='my_method2', totype='array')
            def xarray_my_method2(xarray_object):
                print(xarray_object * 10)
            xr.DataArray(data).pc.my_method2()   # prints 10*DataArray(data).
            xr.Dataset(data).pc.my_method2()   # crashes; my_method2 not registered to datasets.
        '''
        if isinstance(f_or_name, str):
            name = f_or_name
            return lambda f: cls.register(f, _name=name, aliases=aliases, totype=totype)
        else:
            f = f_or_name
            name = _name or f.__name__
            caller = _ObjCaller(f)
            if totype is UNSET:
                totype = cls.access_type
            target_cls = cls.access_type_to_cls[totype]
            setattr(target_cls, name, caller)
            # bookkeeping:
            target_cls.registry[name] = (totype, f)
            # handle aliases if provided:
            for alias_ in aliases:
                setattr(target_cls, alias_, alias(name))
                target_cls.alias_registry.setdefault(name, []).append(alias_)
            return f

    @classmethod
    def register_attr(cls, name, value, *, totype=UNSET):
        '''register cls.{name} = value, using a similar interface as cls.register.
        when totype is UNSET, this is equivalent to:
            cls.{name} = value; cls.attrs_registry[name] = (cls.access_type, value),
        when totype is provided, use cls=cls.access_type_to_cls[totype], instead.

        returns value, after doing setattr(cls, name, value)

        totype: UNSET, None, 'array', or 'dataset'
            which type of xarray objects the registered attr applies to.
            UNSET --> use cls.access_type.
            None --> methods apply to both DataArrays and Datasets.
            'array' --> methods apply to DataArrays only
            'dataset' --> methods apply to Datasets only.

        Examples (using pcAccessor subclass for concreteness):
            pcAccessor.register_attr('MY_CONSTANT1', 7)
            pcAccessor.register_attr('MY_CONSTANT2', 5, totype='array')
            pcAccessor.register_attr('nMbytes', property(lambda self: self.obj.nbytes/1024**2))
            arr = xr.DataArray(some_data)
            ds  = xr.Dataset(other_data)
            arr.pc.MY_CONSTANT1  # == 7
            ds.pc.MY_CONSTANT1   # == 7
            arr.pc.MY_CONSTANT2  # == 5
            ds.pc.MY_CONSTANT2   # crashes; MY_CONSTANT2 not registered to datasets.
            arr.pc.nMbytes       # == DataArray(data).nbytes/1024**2
            ds.pc.nMbytes        # == Dataset(data).nbytes/1024**2
        '''
        if totype is UNSET:
            totype = cls.access_type
        target_cls = cls.access_type_to_cls[totype]
        setattr(target_cls, name, value)
        # bookkeeping:
        target_cls.attrs_registry[name] = (totype, value)
        return value

    registered_methods = property(lambda self: sorted(self.registry.keys()))
    registered_attrs = property(lambda self: sorted(self.attrs_registry.keys()))
    registered_aliases = property(lambda self: {k: v for k, v in sorted(self.alias_registry.items())})

    def __repr__(self):
        contents = []
        methods = self.registered_methods
        if len(methods)>0:
            contents.append(f'registered_methods={methods}')
        attrs = self.registered_attrs
        if len(attrs)>0:
            contents.append(f'registered_attrs={attrs}')
        aliases = self.registered_aliases
        if len(aliases)>0:
            contents.append(f'registered_aliases={aliases}')
        contents_str = ',\n    '.join(contents)
        return f'{type(self).__name__}({object.__repr__(self.obj)},\n    {contents_str})'


class pcAccessor(XarrayAccessor, accessor_name='pc', access_type=None):
    '''access attributes of DataArrays or Datasets e.g. xr.DataArray.pc.differentiate(...).

    This is the base class inherited by pcArrayAccessor and pcDatasetAccessor.
    When deciding where to attach a method, think:
        pcAccessor.register if it applies to DataArrays and Datasets the same way,
        pcAccessor.register(totype='array') if it applies to DataArrays only,
        pcAccessor.register(totype='dataset') if it applies to Datasets only.

    Example:
        @pcAccessor.register
        def my_method(xarray_object, arg1):
            print(arg1)
            print(xarray_obj)
        # --> can later do:
        xr.DataArray(data).pc.my_method(7)   # prints 7 then prints DataArray(data).

        @pcAccessor.register(name='my_method2', totype='array')
        def xarray_my_method2(xarray_object):
            print(xarray_object * 10)
        # --> can later do:
        xr.DataArray(data).pc.my_method2()   # prints DataArray(data).
    '''
    # note: internal pc code should prefer to import the relevant methods from xarray_tools,
    #   for improved compatibility with non-xarray objects.
    # however, scripts should prefer to use the method attached to the array, since it's easier.

    pass  # attach methods & attrs via pcAccessor.register & register_attr.


class pcArrayAccessor(pcAccessor, access_type='array'):
    '''access attributes of DataArrays e.g. xr.DataArray.pc.differentiate(...).
    for more help see help(xr.DataArray.pc).
    '''
    pass  # attach methods & attrs via pcAccessor.register & register_attr with totype='array'


class pcDatasetAccessor(pcAccessor, access_type='dataset'):
    '''access attributes of Datasets e.g. xr.Dataset.pc.differentiate(...).
    for more help see help(xr.Dataset.pc).
    '''
    pass  # attach methods & attrs via pcAccessor.register & register_attr with totype='dataset'


pcAccessor.register_attr('nMbytes', property(lambda self: self.obj.nbytes/1024**2,
                                             doc='''size of array in Mbytes'''))

pcAccessor.register_attr('size', totype='array',
    value=property(lambda self: self.obj.size,
        doc='''total number of elements in the DataArray. Equivalent to array.size.
        Provided for consistent interface for DataArray or Dataset size: use obj.pc.size.'''))

pcAccessor.register_attr('size', totype='dataset',
    value=property(lambda self: sum(v.size for v in self.obj.values()),
        doc='''total number of elements across all values in the Dataset'''))
