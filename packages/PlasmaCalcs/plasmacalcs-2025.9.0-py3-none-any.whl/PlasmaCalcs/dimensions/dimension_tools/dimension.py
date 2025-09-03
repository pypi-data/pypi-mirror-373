"""
File Purpose: Dimension
"""

import builtins

from .dimension_value import DimensionSpecialValueSpecifier

from ...errors import DimensionError, DimensionKeyError, DimensionValueError
from ...tools import (
    simple_property,
    is_iterable_dim, take_along_dimension, join_along_dimension, xarray_assign,
    format_docstring,
    alias_child,
    using_attrs, maintaining_attrs,
    UNSET,
)


### --------------------- Dimension --------------------- ###

_paramdocs_dimension = {
    'v': '''v: None, DimensionValue, or DimensionValueList
                current value of this dimension. Might be multiple values.
                None --> use self.values instead.
                note: when setting self.v = value, will attempt to match value(s) from self.values if possible:
                    if value is None, set self.v = None.
                    else, if self.values exists (and is not None), attempt self.v = self.values.get(v).
                    By default (if the previous cases fail or don't hold), sets self.v = value.''',
    'values': '''values: UNSET, None, or DimensionValueList
                all possible values of this dimension.
                UNSET (or, del self.values) --> raise an AttributeError when trying to access.
                None --> disables the AttributeError, but also disables the "smart" behavior of self.v,
                        where setting self.v tries to match value(s) from self.values.''',
    'on_set_v': '''on_set_v: None or callable of 1 argument.
                if not None, call self.on_set_v(value) immediately after doing self.v = value.''',
    }

@format_docstring(**_paramdocs_dimension)
class Dimension():
    '''a single dimension, representing a current value AND a list of all possible values.

    when creating a subclass, provide:
            name: None or str
                name of this dimension. E.g. 'fluid'.
                None --> this will not be a useable dimension.
                        (use None if creating a subclass which is intended to be subclassed again)
            plural: None or str
                name of this dimension, in plural form. E.g. 'fluids'.
                None --> use str(name)+'s'.
            value_error_type: None or type
                type for cls.dimension_value_error. E.g. FluidValueError
                None --> use DimensionValueError
            key_error_type: None or type
                type for cls.dimension_key_error. E.g. FluidKeyError
                None --> use DimensionKeyError

        Note that docstrings for DIM_METHODS will be formatted using these names,
            via docstring.format(dim=name, dims=plural), if name is provided.


    when creating an instance (possibly an instance of a subclass), can provide:
            {v}
            {values}
            {on_set_v}


    --- Example ---
        class FluidDimension(Dimension, name='fluid'):
            pass   # no special methods for this example

        @FluidDimension.setup_haver  # setup FluidHaver by attaching various relevant properties & methods.
        class FluidHaver(DimensionHaver, dimension='fluid'):
            pass   # no special methods for this example

        after the lines above, FluidHaver will "have" a fluid dimension, e.g.:
            - fluid_haver.fluid_dim       --> FluidDimension instance associated with this fluid_haver instance
            - fluid_haver.fluid           --> fluid_haver.fluid_dim.v
            - fluid_haver.fluids          --> fluid_haver.fluid_dim.values
            - fluid_haver.current_n_fluid --> fluid_haver.fluid_dim.current_n
            - fluid_haver.iter_fluids     --> fluid_haver.fluid_dim.iter_values
            - fluid_haver.take_fluid      --> fluid_haver.fluid_dim.take
        where fluid_haver is an instance of FluidHaver.
        Note that FluidHaver has those attributes as well but they are properties or methods, e.g.:
            FluidHaver.fluid       = property(lambda self: self.fluid_dim.v)             # roughly.
            FluidHaver.iter_fluids = property(lambda self: self.fluid_dim.iter_values)   # roughly.

        For a complete list of all methods which will be attached, see Dimension.setup_haver and DIM_METHODS.
    '''
    name = None
    plural = None
    dimension_value_error = DimensionValueError
    dimension_key_error = DimensionKeyError

    def __init__(self, v=None, values=UNSET, *, on_set_v=None, **kw_super):
        super().__init__(**kw_super)
        self.on_set_v = on_set_v
        if values is not UNSET: self.values = values
        self.v = v  # ^note: set values before v, because v setter might use self.values.

    def __init_subclass__(cls, *, name=None, plural=None,
                          value_error_type=None, key_error_type=None,
                          **kw_super):
        '''setup cls based on provided name and plural.

        name: None or str
            if provided, does the following:
            - sets cls.name
            - sets cls.plural
            - replace DIM_METHODS keys with key.format(dim=name, dims=plural).
        plural: None or str
            plural form of name. If None, use str(name)+'s'. (Only used if name is not None)
        value_error_type: None or type
            if provided, set cls.dimension_value_error = value_error_type
        key_error_type: None or type
            if provided, set cls.dimension_key_error = key_error_type
        '''
        super().__init_subclass__(**kw_super)
        if name is not None:
            cls.name = name
            if plural is None: plural = f'{name}s'
            cls.plural = plural
            dim_methods_orig = cls.DIM_METHODS
            cls.DIM_METHODS = dict()  # new dict, to avoid overwriting the old dict.
            for key, method in dim_methods_orig.items():
                cls.DIM_METHODS[key.format(dim=name, dims=plural)] = method
                # note: difficult to format docstring;
                #   having different docstring requires having multiple copies of the method,
                #   which makes the code less clean. That is why the next line is commented-out.
                # method.__doc__ = method.__doc__.format(dim=name, dims=plural)
        if value_error_type is not None: cls.dimension_value_error = value_error_type
        if key_error_type is not None: cls.dimension_key_error = key_error_type

    # # # SETUP IN ANOTHER CLASS -- TRACKING DIM_METHODS # # #
    @classmethod
    def setup_haver(cls, haver_cls):
        '''setup haver_cls, so that it "has" this dimension,
        in the sense that the following are defined (replacing "fluid" with cls.name):

        - h = haver_cls
        - plural = cls.plural
        - h.fluid_dim_cls  = cls
        - h.fluid_dim      = alias to the instance of cls associated with an instance of h
        - h.fluid          = alias to h.fluid_dim.v
        - h.{plural}       = alias to h.fluid_dim.values
        - h._loading_fluid = alias to h.fluid_dim.loading
        - for (key, method) in cls.DIM_METHODS.items():
            # assert that h.{key} doesn't exist yet, then define:
            h.{key}        = alias to h.fluid_dim.{method}
            # (e.g., h.assign_snap_coord = alias to h.snap_dim.assign_coord)

        Also, call haver_cls.__setup_haver__(cls) if it exists.

        returns haver_cls, so that this function may be used as a class decorator.
        '''
        h = haver_cls
        dim = cls.name   # e.g. 'fluid'
        dim_dim = f'{dim}_dim'  # e.g. 'fluid_dim'
        dim_dim_cls = f'{dim}_dim_cls'   # e.g. 'fluid_dim_cls'

        # e.g. h.fluid_dim_cls = cls
        assert not hasattr(h, dim_dim_cls), f"haver_cls.{dim_dim_cls} already exists!"
        setattr(h, dim_dim_cls, cls)

        # e.g. h.fluid_dim --> the instance of cls which is associated with the instance of h.
        # if h.{dim_dim} hasn't been set, use h.{dim_dim} = h.{dim_dim_cls}().
        assert not hasattr(h, dim_dim), f"haver_cls.{dim_dim} already exists!"
        h_dim_dim = simple_property(f'_{dim_dim}', setdefault=getattr(h, dim_dim_cls),
                                    doc=f'''{dim} dimension for {h.__name__}.''')
        setattr(h, dim_dim, h_dim_dim)

        # e.g. h.fluid --> alias to h.fluid_dim.v
        assert not hasattr(h, dim), f"haver_cls.{dim} already exists!"
        setattr(h, dim, alias_child(dim_dim, 'v'))

        # e.g. h.fluids --> alias to h.fluid_dim.values
        assert not hasattr(h, cls.plural), f"haver_cls.{cls.plural} already exists!"
        setattr(h, cls.plural, alias_child(dim_dim, 'values'))

        # e.g. h._loading_fluid --> alias to h.fluid_dim.loading
        assert not hasattr(h, f'_loading_{dim}'), f"haver_cls._loading_{dim} already exists!"
        setattr(h, f'_loading_{dim}', alias_child(dim_dim, 'loading'))

        # e.g. h.iter_fluid --> alias to h.fluid_dim.iter   # for each method in cls.DIM_METHODS
        for fmtname, methodname in cls.DIM_METHODS.items():
            assert not hasattr(h, fmtname), f"haver_cls.{fmtname} already exists!"
            setattr(h, fmtname, alias_child(dim_dim, methodname))

        # call haver_cls.__setup_haver__(cls) if it exists.
        try:
            h_setup_haver = h.__setup_haver__
        except AttributeError:
            pass
        else:
            h_setup_haver(cls)

        # return haver_cls, so that this function may be used as a class decorator.
        return h


    DIM_METHODS = dict()  # dict of methods to use in cls.setup_haver_cls; {fmtname: method}

    def _dim_method(fmtname, dim_methods=DIM_METHODS):
        '''return decorator(f) which returns f after putting {fmtname: f.__name__} into dim_methods'''
        def decorator(f):
            dim_methods[fmtname] = f.__name__
            return f
        return decorator

    # # # CONVENIENCE # # #
    using = using_attrs
    maintaining = maintaining_attrs

    # # # PROPERTIES # # #
    @property
    def v(self):
        '''current value in self.
        Getting self.v:
            Return self._v if it exists (and is not None), else return self.values.
        Setting self.v = value:
            Attempt to match value from self.values if possible:
                if value is None, set self.v = None
                if value is a DimensionSpecialValueSpecifier, call value.value_to_set(self).
                else, if self.values exists (and is not None), attempt self.v = self.values.get(value).
                By default (if the previous cases fail or don't hold), sets self.v = value.
            Afterwards, call self.on_set_v(value), if self.on_set_v is not None.
        '''
        v = getattr(self, '_v', None)
        return self.values if v is None else v
    @v.setter
    def v(self, val):
        '''set self.v, matching value from self.values if possible.
        See help(type(self).v) for details.
        '''
        if val is None:
            result = val
        elif isinstance(val, DimensionSpecialValueSpecifier):
            result = val.getter(self.values)
        else:
            values = self.values   # <-- will raise AttributeError if self.values doesn't exist!
            if values is None:
                result = val
            else:  # self.values is not None; attempt to use self.values.get(val).
                try:
                    self_values_get = self.values.get
                except AttributeError:
                    result = val  # self.values doesn't have a 'get' method! (it's not a DimensionValueList.)
                else: 
                    result = self_values_get(val)
        self._v = result
        if self.on_set_v is not None:
            self.on_set_v(val)

    @property
    def values(self):
        '''all possible values of this dimension.
        If values does not exist, raise an AttributeError with a helpful message.
            (the message is most helpful at "high level", when using DimensionHaver,
            so it uses the dimension's name instead of 'v' and 'values'.)
        If you want to avoid using DimensionValueList (at the cost of not using its smart behavior..)
            you can use self.values=None, to disable that error message.
        You can del self.values to re-enable that error message.
            (del self.values will do nothing if self.values doesn't exist, as opposed to crashing.)

        Settings self.values will also reset self.v to None afterwards.
        '''
        try:
            return self._values
        except AttributeError:
            name, plural = self.name, self.plural
            errmsg = (f"{plural} hasn't been set yet!\n(self={object.__repr__(self)})\n"
                      f"You can use: {plural}=None, to disable this error, "
                      f"but it will also disable the 'smart' behavior of setting/getting self.{name}.\n"
                      f"(Note: that 'smart' behavior may have triggered this error message, "
                      f"by trying to get self.{plural}.)\nSee help(type(self).{name}) for more info.\n"
                      f"You can also use: del self.{plural}, to re-enable this error.")
            raise AttributeError(errmsg) from None
    @values.setter
    def values(self, val):
        is_new = (val is not getattr(self, '_values', None))
        self._values = val
        if is_new:
            self.v = None
    @values.deleter
    def values(self):
        try:
            del self._values
        except AttributeError:
            pass  # self.values doesn't exist, so there's nothing to delete.

    loading = simple_property('_loading', default=False,
            doc='''whether this dimension is currently being loaded across, via self.load_across().''')

    # # # METHODS # # #
    @_dim_method('current_n_{dim}')
    def current_n(self):
        '''return number of values currently represented by self.v
        0 if None, else len(self.v) if possible, else 1.
        '''
        v = self.v
        if v is None:
            return 0
        try:
            return len(v)
        except TypeError:
            return 1

    @_dim_method('{dim}_is_iterable')
    def is_iterable(self, *, min_length=None):
        '''return whether self.v represents multiple values.
        False if self.v represents only one value.

        if min_length is provided, return bool((result) and (len(self.v) >= min_length)).
        '''
        return is_iterable_dim(self.v, min_length=min_length)

    @_dim_method('{dim}_list')
    def list(self):
        '''return self.v, but guaranteed to be a list.
        if self.v is iterable, return self.v, unchanged;
        else, return [self.v].
        '''
        v = self.v
        if self.is_iterable():
            return v
        else:
            return [v]

    @_dim_method('iter_{dims}')
    def iter_values(self, *, restore=True, enumerate=False):
        '''iterate through self.values. sets AND yields self.v, for each value in self.values.
        
        restore: bool, default True
            whether to restore original self.v after iteration.
        enumerate: bool, default False
            whether to yield indices too, i.e. (i, v) instead of just v.
            if True, indices correspond to position of value in self.values.
        '''
        with self.maintaining(v=restore):
            for i, val in builtins.enumerate(self.values):
                self.v = val
                if enumerate:
                    yield i, val
                else:
                    yield val

    @_dim_method('iter_{dim}')
    def iter(self, *, restore=True, enumerate=False):
        '''iterate through self.v. sets AND yields self.v, for each value in self.v when iteration began.
        
        Note the difference between this method and iter_values;
            this method uses self.v when called, to determine which values to iterate through,
            while iter_values instead uses self.values to determine which values to iterate through.

        if self.v is not iterable, yield self.v once and do not change its value.

        restore: bool, default True
            whether to restore original self.v after iteration.
        enumerate: bool, default False
            whether to yield indices too, i.e. (i, v) instead of just v.
            if True, indices correspond to position of value in the original self.v (not necessarily self.values!)
        '''
        if not self.is_iterable():
            if enumerate:
                yield 0, self.v
            else:
                yield self.v
            return
        # else, self.v is iterable.
        original = self.v
        with self.maintaining(v=restore):
            for i, val in builtins.enumerate(original):
                self.v = val
                if enumerate:
                    yield i, val
                else:
                    yield val

    @_dim_method('enumerate_{dims}')
    def enumerate_values(self, *, restore=True):
        '''iterate through self.values, seting self.v and yielding (i, v) for each v in self.values.
        Equivalent to self.iter_values(restore=restore, enumerate=True).
        '''
        return self.iter_values(restore=restore, enumerate=True)

    @_dim_method('enumerate_{dim}')
    def enumerate(self, *, restore=True):
        '''iterate through self.v. sets self.v and yields (i, v), for each value in self.v when iteration began.
        i corresponds to position of value in original self.v (not necessarily self.values).
        Equivalent to self.iter(restore=restore, enumerate=True).
        '''
        return self.iter(restore=restore, enumerate=True)

    @_dim_method('iter_{dims}_partition')
    def iter_partition(self, partition, *, restore=True):
        '''iterate through self.values. setting self.v=vlist, yielding (partkey, self.v) from partition.items()
        partition: dict-like of {partkey: vlist}
            use to partition values into groups.
            Note: iter_partition doesn't return vlist directly, but instead sets self.v = vlist,
                then returns self.v. If vlist is a list of v-specifiers, the actual v will be returned.
                E.g. if vlist = [0,3,4], result has self.values.get([0,3,4]), not [0,3,4].
        restore: bool, default True
            whether to restore original self.v after iteration.

        E.g. partition = {'a': ['v0', 'v1', 'v4'], 'b': ['v2', 'v3'], 'c': ['v5']}
            --> yields ('a', ['v0', 'v1', 'v4']), then ('b', ['v2', 'v3']), then ('c', ['v5']),
              setting self.v=['v0', 'v1', 'v4'], then self.v=['v2', 'v3'], then self.v=['v5'].
        '''
        with self.maintaining(v=restore):
            for partkey, partvals in partition.items():
                self.v = partvals
                yield partkey, self.v

    @_dim_method('assign_{dim}_coord')
    def assign_coord(self, array, value=UNSET, *, overwrite=None, expand_if_iterable=False):
        '''returns array.assign_coords(dict({cls.name}=self.v)).
        if not self.is_iterable(), raise DimensionalityError, unless expand_if_iterable=True.

        value: UNSET, or value to use instead of self.v
            if provided, temporarily set self.v = value, then restore it afterwards.
            This means value can be "shorthand" for actual values,
                e.g. value = 0 --> self.v = self.values.get(0).
        overwrite: None or bool
            whether to overwrite an existing value for this coord in array.
            (note - array will never be altered here; only the result might be altered.)
            If this coord already in array.coords, behavior depends on overwrite:
                None --> crash with DimensionKeyError.
                True --> overwrite this coord.
                False --> return array, unchanged.
        expand_if_iterable: bool
            whether to expand_dims if self.is_iterable(),
            e.g. array.expand_dims(dict({cls.name}=self.v))
        '''
        if value is not UNSET:
            with self.using(v=value):
                return self.assign_coord(array, overwrite=overwrite)
        # else, value is UNSET.
        if (not expand_if_iterable) and self.is_iterable():
            errmsg = f"assign_coord requires non-iterable self.v"
            raise self.dimension_value_error(errmsg)
        kw_pass = dict(overwrite=overwrite, expand_if_iterable=expand_if_iterable)
        return xarray_assign(array, coords={self.name: self.v}, **kw_pass)

    @_dim_method('assign_{dim}_along')
    def assign_coord_along(self, array, dim, value=UNSET, **kw_assign_coords):
        '''assign value as coords along the indicated dimension.
        Equivalent to array.assign_coords({self.name: (dim, value)})
        requires self.is_iterable() else raises DimensionValueError.

        value: UNSET, or value to use instead of self.v
            if provided, temporarily set self.v = value, then restore it afterwards.
        '''
        if value is not UNSET:
            with self.using(v=value):
                return self.assign_coord_along(array, dim)
        # else, value is UNSET.
        if not self.is_iterable():
            errmsg = f"assign_coord_along requires iterable self.v"
            raise self.dimension_value_error(errmsg)
        v = self.v
        if isinstance(v, tuple):
            v = list(v)  # for some reason, xarray.assign_coords doesn't like tuples.
        return array.assign_coords({self.name: (dim, v)}, **kw_assign_coords)

    @classmethod
    @_dim_method('take_{dims}')
    def take_along(cls, array, at=None, *, i=None, drop_labels=False,
                   as_dict=False, item=False, **kw__take_along_dimension):
        '''return a list of the array value for each {cls.name} in array.

        array: xarray.DataArray
            array to take from.
            E.g., array with coords fluid ['e', 'H+', 'C+'], cls.name=='fluid'
                --> take_along(array) gives [array value for 'e', value for 'H+', value for 'C+'].
        at: None or list-like of values in this dimension
            take at these values. None --> use values from array.coords[this dimension]
        i: None or indices
            (if provided) take only at these indices; use isel.
        drop_labels: bool, default False
            whether to remove this dimension from arr.coords for arr in result.
        as_dict: bool, default False
            if True, return dict of {dim value: array value at this dim} instead of list.
        item: bool
            if True, convert arrays to single values via array.item().
        additional kwargs go to tools.take_along_dimension
        '''
        kw = dict(at=at, i=i, drop_labels=drop_labels, as_dict=as_dict, item=item, **kw__take_along_dimension)
        return take_along_dimension(cls.name, array=array, **kw)

    @_dim_method('take_{dim}')
    def take(self, array, value=UNSET, *, drop_labels=False,
             as_dict=False, squeeze=True, item=False, **kw__take_along):
        '''take the array at array.{cls.name} == self.v (or at value, if provided).
        if self.is_iterable(), return [array at array.{cls.name}==val for val in self.v].
        otherwise, return a single array: array at array.{cls.name}==self.v.

        array: xarray.DataArray
            array to take from.
            E.g., self.v=='e', cls.name=='fluid', array has coord 'fluid' with one value equal to 'e'
                --> take(array) gives array value at fluid=='e'.
        value: UNSET or value
            if provided, temporarily set self.v = value, then restore it afterwards.
            This means value can be "shorthand" for actual values,
                e.g. value = 0 --> self.v = self.values.get(0)
                    value = None --> self.v = None, so self.v gives self.values.
                    See help(type(self).v) for more info.
        drop_labels: bool, default False
            whether to remove this dimension from arr.coords for arr in result.
        as_dict: bool, default False
            if True, return dict of {dim value: array value at this dim} instead.
        squeeze: bool, default True
            if False, always return list (with length==1 if not self.is_iterable()),
            unless as_dict=True. (Ignore squeeze if as_dict.)
        item: bool
            if True, convert arrays to single values via array.item().
        '''
        kw__take_along.update(drop_labels=drop_labels, as_dict=as_dict, item=item)
        if value is not UNSET:
            with self.using(v=value):
                return self.take(array, squeeze=squeeze, **kw__take_along)
        # else, value is UNSET.
        if self.is_iterable():
            return self.take_along(array, at=self.v, **kw__take_along)
        else:
            result = self.take_along(array, at=[self.v], **kw__take_along)
            if as_dict:
                return result
            elif squeeze:
                return result[0]
            else:
                return result

    @classmethod
    @_dim_method('join_{dims}')
    def join_along(self, arrays, labels=None, **kw__join_along_dimension):
        '''return arrays joined along the {cls.name} dimension.
        if labels is provided, set result[{cls.name}] = labels.
        '''
        if len(arrays) == 0:
            raise DimensionError(f"expected at least one array, but got {len(arrays)} arrays.")
        return join_along_dimension(self.name, arrays=arrays, labels=labels, **kw__join_along_dimension)

    @_dim_method('_as_single_{dim}')
    def _as_single(self, val=None):
        '''return the single value at self.v, or self.v corresponding to val if provided.
        If result is not a single value, raise DimensionValueError.
        '''
        if val is not None:
            with self.using(v=val):
                return self._as_single(val=None)
        v = self.v
        if self.is_iterable():
            errmsg = f"expected single value, but got {type(self.v).__name__} with length={len(v)}"
            raise self.dimension_value_error(errmsg)
        else:
            return v

    @_dim_method('_get_first_{dim}')
    def _get_first(self, val=None):
        '''return first value from self.v, or self.v corresponding to val if provided.
        If iterable, return self.v[0], else return self.v.
        '''
        if val is not None:
            with self.using(v=val):
                return self._as_single(val=None)
        return self.v[0] if self.is_iterable() else self.v

    @_dim_method('{dim}_type')
    def get_type(self, *, check_all=False):
        '''get type of single value in self.v.
        check_all: bool, default False
            if True, check all values in self.v to ensure they are all the same type.
        '''
        result = None
        for val in self.iter():
            if result is None:
                result = type(val)
                if not check_all:
                    break
            elif type(val) != result:
                errmsg = f"cannot get_single_type when types don't all match. Found {result} and {val}."
                raise self.dimension_value_error(errmsg)
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        '''return repr for an instance of this class.'''
        contents = []
        v = self.v
        try:
            rep = v._short_repr()
        except AttributeError:
            rep = repr(v)
        contents.append(f'v={rep}')
        values = self.values
        try:
            rep = values._short_repr()
        except AttributeError:
            rep = repr(values)
        contents.append(f'values={rep}')
        return f'{type(self).__name__}({", ".join(contents)})'
