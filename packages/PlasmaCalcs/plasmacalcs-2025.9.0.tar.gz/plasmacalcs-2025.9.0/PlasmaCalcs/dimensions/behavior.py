"""
File Purpose: Behavior object
- like a dict, but with extra features.
- for describing the current behavior of a PlasmaCalculator
"""

import itertools
import sys

import numpy as np
import xarray as xr

from ..errors import UnitsError, InputConflictError
from ..tools import (
    simple_property, alias,
    UNSET, ATTR_UNSET,
    repr_simple,
    format_docstring,
    xarray_assign, is_iterable_dim,
)
from ..defaults import DEFAULTS


class Behavior(dict):
    '''dict with 'compatible' method.

    __getitem__ altered to include values from self.dims, and 'dims' itself.
        e.g. self['dims'] == self.dims; self['fluid'] --> self.dims['fluid'], if possible.
    __contains__ altered to include values from self.dims.
        e.g. 'fluid' in self --> fluid in self.keys() or fluid in self.dims

    arg0: object
        first argument to pass to dict() constructor.
    dims: None or dict
        dict of dimension values for this behavior.
        if None, use empty dict.
    remaining **kw are passd to dict() constructor
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, arg0=UNSET, dims=None, **kw):
        '''initialize Behavior.'''
        if arg0 is UNSET:
            super().__init__(**kw)
        else:
            super().__init__(arg0, **kw)
        self.dims = dict() if dims is None else dims

    def _new_with_dims(self, dims):
        '''return new Behavior like self but with dims instead of self.dims.'''
        return type(self)(super().copy(), dims=dims)

    # # # DICT-LIKE FOR 'dims' # # #
    def __getitem__(self, key):
        '''return self[key], or self.dims[key] if key is in self.dims.
        if key is 'dims', return self.dims.
        '''
        if key == 'dims':
            return self.dims
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.dims[key]

    def __contains__(self, key):
        '''return whether key is in self or self.dims.'''
        return super().__contains__(key) or key in self.dims

    def copy(self, *, keys=None):
        '''return a copy of self, including a copy of self.dims.
        keys: None or iterable
            if provided, the copy will include keys only from this list.
            (either way, the copy will include a full copy of self.dims.)
        '''
        copy_dims = self.dims.copy()
        if keys is None:
            copy_dict = super().copy()
        else:
            copy_dict = {k: self[k] for k in keys}
        return type(self)(copy_dict, dims=copy_dims)

    # # # COMPARISON # # #
    def compatible(self, other, *, lenient=False, subdims=False):
        '''return whether self and other are compatible.
        'compatible' when self[key] == other[key] for all keys in self (and self.dims).
        only tests keys in self; other can have more keys than those in self.

        lenient: bool
            whether to only test keys which are in both self and other.
            if False, and other is missing any keys in self, return False.
        subdims: bool
            whether to be compatible if dim from self is a value within dim from other.
            when True, if only compatible due to subdims, return list of dims which are subdims.
            E.g., self = dict(fluid=1, snap=0), other = dict(fluid=[0,1,2,3], snap=0) -->
                subdims=True --> compatible; result will be ['fluid']
                subdims=False --> not compatible.
            To check whether other dim is a "list" of values, use is_iterable_dim(other_val)
        '''
        if not lenient:
            if not all(key in other for key in (*self, *self.dims)):
                return False  # other is missing key; cannot be compatible.
        # non-dims compatibility
        for key, val in self.items():
            try:
                other_val = other[key]
            except KeyError:  # skip this key, if lenient.
                assert lenient, f"coding error... other is missing {key!r}; should've already returned False"
            else:
                if val != other_val:
                    return False
        # dims compatibility
        subdims_result = []
        for key, val in self.dims.items():
            try:
                other_val = other[key]
            except KeyError:  # skip this key, if lenient.
                assert lenient, f"coding error... other is missing {key!r}; should've already returned False"
            else:
                if val != other_val:
                    if subdims and is_iterable_dim(other_val) and (val in other_val):
                        subdims_result.append(key)
                    else:
                        return False
        return True if len(subdims_result)==0 else subdims_result

    # # # CONVENIENCE # # #
    @format_docstring(DEFAULTS=DEFAULTS)
    def label_array(self, array, *, skip=UNSET):
        '''label array with coords from self.dims, attrs from self.items().
        Requires that values of self.dims are all non-iterable, according to is_iterable_dim().

        skip: None, UNSET, or list of strs
            skip these attrs, if provided.
            UNSET --> skip DEFAULTS.SKIP_BEHAVIOR_ARRAY_LABELS
                        (default {DEFAULTS.SKIP_BEHAVIOR_ARRAY_LABELS})
            None --> don't skip anything.
        '''
        coords = self.dims
        if skip is UNSET:
            skip = DEFAULTS.SKIP_BEHAVIOR_ARRAY_LABELS
        elif skip is None:
            skip = []
        attrs = {k: v for k, v in self.items() if k not in skip}
        return xarray_assign(array, coords=coords, attrs=attrs)

    def assign_attrs(self, array):
        '''return copy of array with self keys & vals (but not dims) assigned as attrs.
        if any were already attrs of array, crash if value mismatch.

        See also: assign_nondefault_attrs
        '''
        to_assign = self
        existing = array.attrs
        for e, v in existing.items():
            if e in to_assign and to_assign[e] != v:
                errmsg = ('assign_nondefault_attrs refusing to overwrite existing attr: '
                          f'{e!r} from old value {v!r} to new value {to_assign[e]}')
                raise QuantCalcError(errmsg)
        return array.assign_attrs(to_assign)

    def assign_nondefault_attrs(self, array, ql=None, *, include_xr=True):
        '''return copy of array with self.nondefault() keys & vals (but not dims) assigned as attrs.
        if any were already attrs of array, crash if value mismatch.

        ql: None or BehaviorHaver
            if provided, used to evaluate some defaults (anything defined with getdefault)
            e.g. for stat_dims, getdefault = lambda ql: getattr(ql, 'maindims', []).
        include_xr: bool
            whether to include keys whose values are xarray objects (DataArray or Dataset).

        See also: assign_attrs
        '''
        # [TODO] reduce repeated code from above
        to_assign = self.nondefault(ql=ql, include_xr=include_xr)
        existing = array.attrs
        for e, v in existing.items():
            if e in to_assign and to_assign[e] != v:
                errmsg = ('assign_nondefault_attrs refusing to overwrite existing attr: '
                          f'{e!r} from old value {v!r} to new value {to_assign[e]}')
                raise QuantCalcError(errmsg)
        return array.assign_attrs(to_assign)

    def default_keys(self, ql=None):
        '''return list of keys in self with key.is_default(value, ql=ql)
        Does not consider self.dims.
        ql: None or BehaviorHaver
            if provided, used to evaluate some defaults (anything defined with getdefault)
            e.g. for stat_dims, getdefault = lambda ql: getattr(ql, 'maindims', []).
        '''
        result = []
        for k, v in self.items():
            if hasattr(k, 'is_default') and k.is_default(v, ql=ql):
                result.append(k)
        return result

    def nondefault_keys(self, ql=None, *, include_xr=True):
        '''return list of keys in self with NOT key.is_default(value, ql=ql).
        Does not consider self.dims.
        ql: None or BehaviorHaver
            if provided, used to evaluate some defaults (anything defined with getdefault)
            e.g. for stat_dims, getdefault = lambda ql: getattr(ql, 'maindims', []).
        include_xr: bool or 'only'
            whether to include keys whose values are xarray objects (DataArray or Dataset).
            'only' --> instead return only keys whose values are xarray objects (& not default).
        '''
        result = []
        for k, v in self.items():
            if not (hasattr(k, 'is_default') and k.is_default(v, ql=ql)):
                if include_xr == 'only':
                    if isinstance(v, (xr.DataArray, xr.Dataset)):
                        result.append(k)
                elif include_xr or not isinstance(v, (xr.DataArray, xr.Dataset)):
                    result.append(k)
        return result

    def nondefault(self, ql=None, *, include_xr=True):
        '''returns Behavior like self but dropping all keys with key.is_default(value, ql=ql).
        Note: these are the keys which MIGHT not have default values;
            result includes keys where default was unknown and unchecked.

        ql: None or BehaviorHaver
            if provided, used to evaluate some defaults (anything defined with getdefault)
            e.g. for stat_dims, getdefault = lambda ql: getattr(ql, 'maindims', []).
        include_xr: bool
            whether to include keys whose values are xarray objects (DataArray or Dataset).
            'only' --> instead return a dict of only keys whose values are xarray objects (& not default).
        '''
        if include_xr == 'only':
            return {k: self[k] for k in self.nondefault_keys(ql=ql, include_xr='only')}
        else:
            return self.copy(keys=self.nondefault_keys(ql=ql, include_xr=include_xr))

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'{k}={repr_simple(v)}' for k, v in self.items()]
        contents.append(f'dims={repr_simple(self.dims)}')
        return f'{type(self).__name__}({", ".join(contents)})'

    def __str__(self):
        contents = [f'{k}={v!r}' for k, v in self.items()]
        contents.append(f'dims={self.dims}')
        return f"{type(self).__name__}({', '.join(contents)})"


class BehaviorQuantity():
    '''quantity, with value and associated behavior.
    behavior: dict or Behavior
        this BehaviorQuantity is relevant only when behavior.compatible(obj.behavior).
        E.g., behavior = dict(snap=0, units='si'),
            - relevant if obj.behavior = dict(snap=0, units='si', ...).
            - irrelevant if obj.behavior = dict(snap=1, ...).
            - irrelevant if obj.behavior = dict(units='raw', ...)
        note: if ukey is not None, and behavior is a Behavior,
            self will store a COPY of behavior, not the original object;
            this is to prevent popping 'units' from the original Behavior object.

    MB: None or number
        number of megabytes this BehaviorQuantity takes up in memory.
        if None, will be calculated from self.value, if possible.
    ukey: None, or str
        if provided (not None), pop 'units' from stored behavior, and store self.uinfo = (ukey, units).
        None --> don't pop 'units' from stored behavior.
        str --> value [any unit system] = self.value * u_convert, where
                    u_convert = UnitsHaver.u(self.uinfo[0], (that unit system), convert_from=self.uinfo[0])
                Note, for a dimensionless value, use ukey='' or ukey='1'.
        The benefit of using this is that 'units' won't be in self.behavior,
            so self.compatible(other_behavior) won't need to check units.
        (The downside is that you must be careful to properly handle the units. see also: self.get_value.)

    Every BehaviorQuantity has a unique identifier, self.id, which is a number.
    BehaviorQuantity.NEXT_UNIQUE_ID is the next number to be assigned.
    '''
    NEXT_UNIQUE_ID = 0

    # # # CREATION / INITIALIZATION # # #
    def __init__(self, value, behavior, *, MB=None, ukey=None, **kw__behavior):
        self.value = value
        if not isinstance(behavior, Behavior):
            behavior = Behavior(behavior, **kw__behavior)
        if ukey is not None:
            behavior = behavior.copy()
            self.uinfo = (ukey, behavior.pop('units', None))
        self.behavior = behavior
        self._entered_MB = MB
        self.n_used = 0  # counts number of times this value was loaded from cache.
                         # not updated by this class, but see e.g. VarCache.
        self.id = self.NEXT_UNIQUE_ID
        type(self).NEXT_UNIQUE_ID = self.id + 1  # [TODO] is this thread-safe?

    def _new_with_dims(self, dims, **kw_init):
        '''return new BehaviorQuantity like self but with dims instead of self.behavior.dims.'''
        kw_init.setdefault('MB', self.MB)
        return type(self)(self.value, self.behavior._new_with_dims(dims), **kw_init)

    # # # PROPERTIES # # #
    uinfo = simple_property('_uinfo', default=None,
            doc='''(ukey, units), indicating units of self.value;
            self.value [any unit system] = self.value * u_convert, where
                u_convert = UnitsHaver.u(ukey, (that unit system), convert_from=ukey)''')

    # # # GETTING VALUE # # #
    def get_value(self, units_manager=None):
        '''return self.value; if units_manager is provided return value in units_manager.units unit system.
        if self.uinfo[1] != units_manager.units, and value is an xarray with 'units' attr,
            result will have units attr assigned to units_manager.units.

        raise UnitsError if ALL of the following are True:
            - units_manager was provided
            - self.uinfo is None
            - units_manager.units!=self.behavior['units']
        '''
        u = units_manager
        if u is None:
            return self.value
        if self.uinfo is None:
            if self.behavior.get('units', None) != u.units:
                errmsg = (f"can't get value in units={u.units!r}, since self.uinfo is None, "
                          f"and self.behavior['units'] != {u.units!r}.")
                raise UnitsError(errmsg)
            else:
                return self.value
        else:
            value = self.value
            ukey, value_units = self.uinfo
            if value_units == u.units:
                result = value
            else:
                u_convert = u(ukey, convert_from=value_units)
                result = self.value * u_convert
                if isinstance(result, xr.DataArray) and result.attrs.get('units', None) != u.units:
                    result = result.assign_attrs(units=u.units)
            return result
        assert False, 'coding error if reached this line'

    # # # MATCHING OTHER BEHAVIORS # # #
    def compatible(self, behavior, *, lenient=False, subdims=False):
        '''tells whether this cached quantity is compatible to obj with this behavior.
        returns self.behavior.compatible(behavior, lenient=lenient, subdims=subdims)
        '''
        return self.behavior.compatible(behavior, lenient=lenient, subdims=subdims)

    def matches_behavior(self, behavior):
        '''tells whether this cached quantity matches this behavior.
        returns self.compatible(behavior, lenient=True, subdims=False).
        '''
        return self.compatible(behavior, lenient=True, subdims=False)

    def relevant(self, behavior):
        '''tells whether this cached quantity is relevant to this behavior.

        'relevant' when self[key] == other[key] for all keys in self,
            and self.dims[d] equals or is inside other.dims[d], for all d in self.dims.
        only tests keys in self; other can have more keys than those in self.

        returns self.compatible(behavior, lenient=True, subdims=True).
        '''
        return self.compatible(behavior, lenient=True, subdims=True)

    # # # LISTING POINTS # # #
    def list_points(self):
        '''returns a list of CachedQuantity objects, each with a single point (in dimension space) from self.
        dimension space includes dimensions but not maindims, e.g. fluid, snap, but not x,y,z.
        '''
        behavior = self.behavior
        keys, vals = zip(*behavior.dims.items())
        iterable = [is_iterable_dim(v, min_length=1) for v in vals]
        if not any(iterable):
            return [self]
        iters = [iter(v) if it_ else [v] for v, it_ in zip(vals, iterable)]
        # [TODO] <-- re-use the iter_dim_multi code from dimension_tools?
        result = []
        for vs_ in itertools.product(*iters):
            dims_point = dict(zip(keys, vs_))
            result.append(self._new_with_dims(dims_point))
            # [TODO] ^ that just copy-pastes the value from self, to each of the points.
            #    if the value is an xarray with dimension names as coords,
            #    then we should instead iterate over those coords too.
            #    e.g. if value has fluid=[0,1,2] and self.behavior.dims has fluid=[0,1,2],
            #      then the result should have 3 points, first with fluid 0, then fluid 1, then 2.
            #      right now, the result would be 3 points, each with fluid=[0,1,2].
        return result

    # # # MB # # #
    @property
    def MB(self):
        '''number of megabytes this cached quantity takes up in memory.
        if self._entered_MB is None, will be calculated from self.value.
        if self.value.nbytes is not available, will be 0.
        Saves value to self._MB to avoid recalculating.
        '''
        try:
            return self._MB
        except AttributeError:
            pass  # this is the first time getting MB; handle it below.
        if self._entered_MB is None:
            try:
                nbytes = self.value.nbytes
            except AttributeError:
                nbytes = sys.getsizeof(self.value)
            self._MB = nbytes / 1024**2
        else:
            self._MB = self._entered_MB
        return self._MB

    # # # DISPLAY # # #
    def __repr__(self):
        contents = self._repr_contents()
        return f'{type(self).__name__}({", ".join(contents)})'

    def _repr_contents(self):
        '''return list of contents to put in repr of self.'''
        val_str = repr(self.value)
        if len(val_str) > 20:
            val_str = val_str[:20] + '...'
        contents = [val_str, str(self.behavior)]
        if self.MB is not None:
            contents.append(f'MB={self.MB:.2e}')
        if self.uinfo is not None:
            contents.append(f'uinfo={self.uinfo}')
        return contents


class BehaviorAttr(str):
    '''string which refers to an attr controlling behavior of a class.

    might also know cls_where_defined, and is_dimension.

    default: ATTR_UNSET or any value
        if provided, does NOT affect the attribute itself;
        it's just a reference point for "maybe we don't need to show the info if == default"
    getdefault: ATTR_UNSET or callable of 1 arg
        similar to default but callable of BehaviorHaver: default=getdefault(behavior_haver),
            instead of being the same value for all BehaviorHavers.
        cannot provide both default and getdefault
    '''
    def __new__(cls, value, *, cls_where_defined=None, is_dimension=False, doc=None,
                default=ATTR_UNSET, getdefault=ATTR_UNSET):
        '''create new BehaviorAttr.
        cls_where_defined: None or type
            class where this attr is defined.
        is_dimension: bool
            whether this attr is a dimension.
        doc: None or str
            arbitrary docstring describing this attr.
        default: ATTR_UNSET or any object
            if provided (i.e. not ATTR_UNSET), tells behavior management code the "default" value.
            E.g. calculator.behavior.nondefault() includes only the non-default values.
            Does NOT affect the attribute itself (e.g. doesn't mess with fget & fset if property).
            Incompatible with is_dimension=True.
        getdefault: ATTR_UNSET or callable of 1 arg
            similar to default but as a callable of BehaviorHaver. See help(BehaviorAttr) for details.
        '''
        self = super().__new__(cls, value)
        self.cls_where_defined = cls_where_defined
        self.is_dimension = is_dimension
        self.doc = doc
        self.default = default
        self.getdefault = getdefault
        if is_dimension:
            if (default is not ATTR_UNSET):
                raise InputConflictError(f'cannot provide default when is_dimension. Got {default!r}')
            if (getdefault is not ATTR_UNSET):
                raise InputConflictError(f'cannot provide getdefault when is_dimension. Got {getdefault!r}')
        if (default is not ATTR_UNSET) and (getdefault is not ATTR_UNSET):
            raise InputConflictError('cannot provide both default and getdefault.')
        return self

    cls = alias('cls_where_defined')

    def is_default(self, value, ql=None):
        '''returns whether value == self.default.
        if no default was set, return False without checking equality.
        if set self.getdefault instead of default, call as getdefault(ql).
            (if ql None, return False without checking equality.)

        ql: None or BehaviorHaver
            if provided, used to evaluate some defaults (anything defined with getdefault)
            e.g. for stat_dims, getdefault = lambda ql: getattr(ql, 'maindims', []).
        '''
        default = self.default
        if default is ATTR_UNSET:
            if self.getdefault is ATTR_UNSET:
                return False
            elif ql is None:
                return False
            else:
                default = self.getdefault(ql)
        ndim = getattr(value, 'ndim', None)
        if (ndim is not None) and ndim >= 1:
            return np.all(value == default)
        else:
            return (value == default)

    def __repr__(self):
        return self._pretty_repr(fmt=None)

    def _pretty_repr(self, fmt=None):
        '''repr but align use fmt.format(super().__repr__()), if provided.'''
        contents = []
        if fmt is None:
            contents.append(super().__repr__())
        else:
            contents.append(fmt.format(super().__repr__()))
        if self.cls is not None:
            contents.append(f'cls={self.cls.__name__}')
        if self.is_dimension:
            contents.append(f'is_dimension={self.is_dimension}')
        if self.default is not ATTR_UNSET:
            contents.append(f'default={self.default}')
        return f'{type(self).__name__}({", ".join(contents)})'


class ClsBehaviorAttrs(list):
    '''list of attrs which control behavior of a class.
    also provides a method to register a new behavior attr.

    might also know cls_associated_with.
    '''
    behavior_attr_cls = BehaviorAttr

    cls_associated_with = simple_property('_cls_associated_with', default=None,
            doc='''class with which this list of behavior attrs is associated.''')

    def register(self, *attrs, is_dimension=False, default=ATTR_UNSET, getdefault=ATTR_UNSET):
        '''register attrs as BehaviorAttrs for self.cls_associated_with.
        returns list of newly registered BehaviorAttr objects.

        default: ATTR_UNSET or any object
            if provided (i.e. not ATTR_UNSET), tells behavior management code the "default" value.
            E.g. calculator.behavior.nondefault() includes only the non-default values.
            Does NOT affect the attribute itself (e.g. doesn't mess with fget & fset if property).
        getdefault: ATTR_UNSET or callable of 1 arg
            similar to default but callable of BehaviorHaver: default=getdefault(behavior_haver),
                instead of being the same value for all BehaviorHavers.
            cannot provide both default and getdefault
        '''
        cls = self.cls_associated_with
        result = []
        for attr in attrs:
            if not isinstance(attr, self.behavior_attr_cls):
                attr = self.behavior_attr_cls(attr, cls_where_defined=cls, is_dimension=is_dimension,
                                              default=default, getdefault=getdefault)
            result.append(attr)
        self.extend(result)
        return result

    def __repr__(self):
        attrs = sorted(self)
        if len(self) == 0:
            return f'{type(self).__name__}([])'
        lens = [len(str(attr)) for attr in attrs]
        align_len = min(max(lens), 20)
        fmt=f'{{:<{align_len}}}'
        contents = [attr._pretty_repr(fmt=fmt) if hasattr(attr, '_pretty_repr') else repr(attr) for attr in attrs]
        contents_str = ',\n  '.join(contents)
        return f'{type(self).__name__}([\n  {contents_str}\n])'


class MetaBehaviorHaver(type):
    '''metaclass for BehaviorHaver. adds cls_behavior_attrs to the class namespace;
    use cls_behavior_attrs.register(new_attr) to register a new attr as a behavior attr.

    Note that __prepare__ gets called before class definition begins, and fills class namespace,
    then __init__ gets called after class definition ends. For example:
        class MySubclass(metaclass=MetaBehaviorHaver):
            # <-- __prepare__ runs here. Roughly: locals().update(__prepare__())
            pass  # or, define other functions, variables, etc, as desired.
        # <-- __init__ runs here. Roughly: MetaBehaviorHaver.__init__(MySubclass)
    '''
    # In case anyone is looking through the codebase to understand cls_behavior_attrs.register
    # this class is the one that defines it, though it doesn't use the usual 'def' notation,
    # so, here are some strings that will pop up for searches like that, instead.
    #   def cls_behavior_attrs(...)            # see __prepare__
    #   def cls_behavior_attrs.register(...)   # see __prepare__, and ClsBehaviorAttrs

    @classmethod
    def __prepare__(_metacls, _name, bases, **kw_super):
        '''return a dict with register_behavior_attr in it.'''
        super_result = super().__prepare__(_name, bases, **kw_super)
        cls_behavior_attrs = ClsBehaviorAttrs()
        for base in bases:
            base_attrs = getattr(base, 'cls_behavior_attrs', [])
            for attr in base_attrs:
                # check for matches!
                for i, cattr in enumerate(cls_behavior_attrs):
                    # check for same str but different object, i.e. registered same str in 2 different subclasses.
                    #   if this occurs we need to be sure to keep the one from the earliest class in the mro().
                    if attr == cattr:
                        if (attr is not cattr) and issubclass(base, cattr.cls_where_defined):
                            cls_behavior_attrs[i] = attr  # attr from earlier in mro() than cattr; replace cattr with attr.
                        break  # (MetaBehaviorHaver logic guarantees there's at most 1 match.)
                else:  # didn't find a match; add attr!
                    cls_behavior_attrs.append(attr)
        return dict(**super_result, cls_behavior_attrs=cls_behavior_attrs)

    def __init__(cls, *args, **kw):
        '''initialize cls (with metaclass=MetaBehaviorHaver)'''
        cls.cls_behavior_attrs.cls_associated_with = cls
        for attr in cls.cls_behavior_attrs:
            if getattr(attr, 'cls_where_defined', None) is None:
                attr.cls_where_defined = cls
            if getattr(attr, 'doc', None) is None:
                if hasattr(cls, attr) and isinstance(getattr(cls, attr), property):
                    attr.doc = getattr(cls, attr).__doc__
        super().__init__(*args, **kw)


class BehaviorHaver(metaclass=MetaBehaviorHaver):
    '''object which has a behavior.'''
    behavior = property(lambda self: self.get_behavior(),
            doc='''dict of {attr: self.attr} for attr in self.behavior_attrs. Note dims are separate;
            dims go in behavior.dims. E.g. Behavior({'units':'si',...}, dims={'snap':0,...}).''')

    def get_behavior(self, keys=None):
        '''return value of self.behavior.
        keys: None or iterable
            if provided, only include these attrs.
            from nondim_behavior_attrs, or dims.
        '''
        attrs = self.nondim_behavior_attrs
        dims = getattr(self, 'dims', [])
        if keys is None:
            use_attrs = attrs
            use_dims = dims
        else:
            use_attrs = [key for key in keys if key in attrs]
            use_dims = [key for key in keys if key in dims]
        behavior_dict = {k: getattr(self, k) for k in use_attrs}
        self_dim_values = getattr(self, 'dim_values', None)
        dims_dict = None if self_dim_values is None else self_dim_values(use_dims)
        return Behavior(behavior_dict, dims_dict)

    @property
    def behavior_attrs(self):
        '''list of attrs in self which control behavior of self.
        Here, returns self.cls_behavior_attrs.

        Subclasses could override if any behavior attrs are not known at the class-level,
            e.g. if MySubclass's list of behavior attrs varies between instances of MySubclass.
        '''
        return self.cls_behavior_attrs

    @property
    def nondim_behavior_attrs(self):
        '''list of attrs in self which control behavior of self, but which are NOT in self.dimensions.'''
        return [attr for attr in self.behavior_attrs if not getattr(attr, 'is_dimension', False)]

    # [TODO] help methods, e.g.:
    # def help_behavior_attrs(self, search) checking all behavior_attrs
    # def help_cls_behavior_attrs(cls, search) as a classmethod checking only cls_behavior_attrs
