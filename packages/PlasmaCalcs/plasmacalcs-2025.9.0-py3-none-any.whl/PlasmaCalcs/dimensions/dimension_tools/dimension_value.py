"""
File Purpose: DimensionValue, DimensionValueList, UniqueDimensionValue
"""

from ...errors import (
    DimensionValueError, DimensionKeyError, DimensionalityError,
    InputError, InputMissingError,
)
from ...tools import (
    elementwise_property, alias,
    repr_simple,
    Sentinel, UNSET, ATTR_UNSET,
    is_iterable,
    is_integer, interprets_fractional_indexing,
    XarrayIoSerializable,
)
from ...defaults import DEFAULTS


### --------------------- DimensionValue --------------------- ###

class DimensionValue(XarrayIoSerializable):
    '''value of a dimension. E.g., a single Fluid or a single Snap.
    Also may know how to be converted to str and int.

    s: string or None
        str(self) --> s. if None, cannot convert to str.
    i: nonnegative int, or None
        int(self) --> i. if None, cannot convert to int.
        Must be nonnegative; negative ints are reserved for "index from end of list".

    CAUTION: intended to be immutable (but not strictly enforced)!
        changing the values of s or i after initialization might cause unexpected behavior.
        E.g., DimensionValueList.get utilizes caching and expects s & i to not change.

    testing equality shows that DimensionValue == s or i,
        e.g. val1=DimensionValue('H', 0) --> val1 == 'H' and val1 == 0.
        However when comparing to another DimensionValue, s and i must both be equal,
            e.g. val2=DimensionValue('C', 0) --> val2 != val1.
            (result also depends on DimensionValue types, if subclasses are involved.)
    '''
    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'s', 'i'}

    _kw_eq = alias('_kw_def', doc='''attributes used when testing equality. Default: alias to _kw_def.''')
    _kw_copy = alias('_kw_def', doc='''attributes used as defaults in copy(). Default: alias to _kw_def.''')

    def __init__(self, s=None, i=None):
        self.s = s
        self.i = i
        if (i is not None) and (i < 0):
            raise DimensionValueError(f"negative i not allowed, but got i={i}.")
    def __str__(self):
        return f'{type(self).__name__}_{self.i}' if self.s is None else self.s
    def __int__(self):
        return self.i

    def __eq__(self, v):
        '''return self==v. Equal if:
            - v is an instance of type(self), and
                all kw from both self._kw_eq and v._kw_eq have the same values.
                    (any kw missing attrs will be treated as UNSET.)
                For DimensionValue, just compares self.s==v.s and self.i==v.i.
                    Subclasses may add more kwargs to compare by altering _kw_def.
            - or, self.s == v or self.i == v, and v is not another DimensionValue
            - or, v is a DimensionSingleValueSpecifier and v.checker(self) gives True.
        Not equal if v is a DimensionValue but not an instance of type(self),
            e.g. class Fluid(DimensionValue):...; class Snap(DimensionValue):...;
                Fluid('H', 0) != Snap('H', 0).
        '''
        if v is self:
            return True   # an object is equal to itself
        elif isinstance(v, DimensionSingleValueSpecifier):
            return v.checker(self)
        elif isinstance(v, type(self)):
            kw_compare = self._kw_eq.union(v._kw_eq)
            for key in kw_compare:
                if getattr(self, key, UNSET) != getattr(v, key, UNSET):
                    return False
            return True
        elif isinstance(v, DimensionValue):
            if DEFAULTS.DEBUG >= 4:
                print('DimensionValue comparison of incompatible subclasses: ',
                      type(self), type(v), '--- returning False.')
            return False
        else:
            return (self.s == v) or (self.i == v)

    def equal_except_i(self, v):
        '''returns whether self == v (another DimensionValue), ignoring i.
        equal if v is an instance of type(self) and
            all kw from both self._kw_eq and v._kw_eq have the same values.
            (any kw missing attrs will be treated as UNSET.)
            For DimensionValue: self.s==v.s and self.i==v.i. Subclasses may add more.
        '''
        if not isinstance(v, type(self)):
            return False
        kw_compare = self._kw_eq.union(v._kw_eq)
        for key in kw_compare:
            if key == 'i': continue
            if getattr(self, key, UNSET) != getattr(v, key, UNSET):
                return False
        return True

    _hash_tuple_convert_len_limit = 100  # if hashing, convert shorter non-hashable iterables to tuples first.

    def __hash__(self):
        result = [getattr(self, k, ATTR_UNSET) for k in self._kw_eq]
        try:
            result = hash((type(self), *result))
        except TypeError:  # maybe one or more of the things in result were not hashable.
            for i, r in enumerate(result):
                try:  # [TODO][EFF] if this is ever a computational bottleneck, be more efficient
                    hash(r)
                except TypeError:
                    if is_iterable(r):
                        if len(r) > self._hash_tuple_convert_len_limit:
                            errmsg = (f"cannot hash {type(self).__name__} with unhashable iterable {list(self._kw_eq)[i]}"
                                      f" with length > self._hash_tuple_convert_len_limit (= {self._hash_tuple_convert_len_limit}).")
                            raise TypeError(errmsg)
                        result[i] = tuple(r)
                    else:
                        raise
            result = hash((type(self), *result))
        return result

    def copy(self, **kw_init):
        '''return a copy of self. Can provide new kwargs here to override old values in result.
        E.g. self.copy(i=7) makes a copy of self but with i=7 instead of self.i.
        '''
        for key in self._kw_copy:
            kw_init.setdefault(key, getattr(self, key))
        return type(self)(**kw_init)

    def with_i(self, i):
        '''return copy of self with i=i, or self if self.i==i already.'''
        if self.i == i:
            return self
        return self.copy(i=i)

    def to_dict(self):
        '''return dictionary of info about self. Attribute values for keys in self._kw_def.
        e.g. if _kw_def={'s', 'i'}: result = {'s': self.s, 'i': self.i}
        '''
        return {k: getattr(self, k) for k in self._kw_def}

    def lookup_dict(self):
        '''returns dict for looking up self within a DimensionValueList, given int, str, or self.
        (used by DimensionValueList.lookup_dict)
        '''
        result = dict()
        result[self] = self
        try:
            result[str(self)] = self
        except TypeError:
            pass
        try:
            result[int(self)] = self
        except TypeError:
            pass
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({self.s!r}, {self.i!r})'

    def _repr_simple(self):
        '''return simple repr for self: Classname(s, i).
        if s is None, use Classname(i) instead.
        if i is None, use Classname(s, i=None) instead.
        Called when using PlasmaCalcs.tools.repr_simple.
        '''
        if self.s is None:
            return f'{type(self).__name__}({self.i!r})'
        elif self.i is None:
            return f'{type(self).__name__}({self.s!r}, i=None)'
        else:
            return f'{type(self).__name__}({self.s!r}, {self.i!r})'

    # ndim = 0 is useful for achieving desired behavior,
    #  of being treated as "a single value of a dimension",
    #  while still allowing subclasses to implement __iter__.
    # ndim = 0 is checked by:
    #  - DimensionHaver, when checking dim_is_iterable() for an instance of this class.
    #  - xarray, when attempting to use an instance of this class as a coordinate.
    ndim = 0

    # size = 1 is also useful.
    size = 1

    # sometimes it's convenient to have an ordering for the values...
    def __lt__(self, other):
        if isinstance(other, type(self)): return (self.i, self.s) < (other.i, other.s)
        else: return NotImplemented
    def __le__(self, other):
        if isinstance(other, type(self)): return (self.i, self.s) <= (other.i, other.s)
        else: return NotImplemented
    def __gt__(self, other):
        if isinstance(other, type(self)): return (self.i, self.s) > (other.i, other.s)
        else: return NotImplemented
    def __ge__(self, other):
        if isinstance(other, type(self)): return (self.i, self.s) >= (other.i, other.s)
        else: return NotImplemented


### --------------------- DimensionValueList --------------------- ###

class SliceableList(list):
    '''list that returns a new instance of type(self) when sliced.
    Also permits slicing by an iterable (take one element for each index in the iterable).
    '''
    def _new(self, *args, **kw):
        '''return new instance of type(self), with these args and kw.'''
        return type(self)(*args, **kw)

    def __getitem__(self, ii, **kw_new):
        '''return self[ii], giving element from self if int(ii) possible, else new instance of type(self).'''
        try:
            i = int(ii)
        except TypeError:
            pass  # handled after 'else' block
        else:
            return super().__getitem__(i)
        if isinstance(ii, slice):
            return self._new(super().__getitem__(ii), **kw_new)
        else:
            return self._new([super(SliceableList, self).__getitem__(i) for i in ii], **kw_new)

    size = property(lambda self: len(self), '''alias to len(self).''')

    def inserted(self, i, element, **kw_new):
        '''return copy of self but with element inserted at i. kwargs passed to new self.__init__.'''
        elements = list(self)
        elements.insert(i, element)
        return self._new(elements, **kw_new)

    # # # DISPLAY # # #
    def _display_contents(self, f, *, nmax=3):
        '''return str to display self's contents, using f(element) for each element.
        if len(self) > nmax, instead include len(self), self[0], and self[-1], only.
        '''
        if len(self) <= nmax:
            contents = ', '.join(f(el) for el in self)
        else:
            contents = f'len={len(self)}; {f(self[0])}, ..., {f(self[-1])}'
        return contents

    def __repr__(self):
        contents = self._display_contents(repr, nmax=3)
        return f'{type(self).__name__}({contents})'

    def _repr_simple(self):
        '''return simple repr for self; includes type, len, and a repr_simple for a few elements.
        if less than 4 elements, just uses repr_simple for the elements (doesn't include len).
        '''
        contents = self._display_contents(repr_simple, nmax=3)
        return f'{type(self).__name__}({contents})'
    
    def __str__(self):
        contents = self._display_contents(str, nmax=3)
        return f'{type(self).__name__}({contents})'

    def _short_repr(self):
        '''return a shorter repr of self; just includes type & len.'''
        return f'{type(self).__name__}(with length {len(self)})'


def string_int_lookup(dict_):
    '''return dict_ but with DimensionValue, str, and int keys. dict_ keys should be DimensionValue objects.
    if any keys can't be converted to str or int, skip converting those keys to that type.
    '''
    # [TODO] remove this. Already refactored to use lookup_dict from DimensionValue.
    #  (string_int_lookup is used elsewhere though, need to investigate further.)
    result = dict()
    for key, val in dict_.items():
        result[key] = val
        try:
            result[str(key)] = val
        except TypeError:
            pass
        try:
            result[int(key)] = val
        except TypeError:
            pass
    return result

def string_int_index(list_):
    '''return dict mapping DimensionValue, str, and int keys to the indices of corresponding DimensionValue values.'''
    return {k: i for i, val in enumerate(list_) for k in (val, str(val), int(val))}

class DimensionValueList(SliceableList):
    '''SliceableList of DimensionValue elements. Also provides get() and lookup_dict() methods,
    which allow to get values based on int or string (or slice, or tuple or int or strings).
    Those methods use caching (assume int(element) & str(element) never changes for any element).

    istart: None or int
        if provided, reindex elements with new i values, starting from istart.
        E.g. istart=0 --> result.i == 0, 1, 2, ....
        elements which already have correct i will remain unchanged.
    '''
    _dimension_key_error = DimensionKeyError
    value_type = DimensionValue

    ndim = 1  # primary use: to distinguish between this and DimensionValue.

    s = elementwise_property('s')

    # # # CREATION OPTIONS # # #
    def __init__(self, *args_list, istart=None, **kw_list):
        if istart is None:
            super().__init__(*args_list, **kw_list)
        else:
            ll = list(*args_list, **kw_list)
            for i, el in enumerate(ll):
                ll[i] = el.with_i(i=istart+i)
            super().__init__(ll)

    @classmethod
    def from_strings(cls, strings):
        '''return cls instance from iterable of strings. (i will be determined automatically.)
        Equivalent to cls(cls.value_type(s, i) for i, s in enumerate(strings)).
        '''
        return cls(cls.value_type(s, i) for i, s in enumerate(strings))

    @classmethod
    def from_dicts(cls, dicts, *, istart=UNSET, **kw_value_init):
        '''return cls instance from iterable of dicts

        values will all be DimensionValue objects, with type == cls.value_type.

        dicts: iterable of dicts
            each one corresponds to one (cls.value_type) object in result.
        istart: UNSET, None, or int
            mode for inferring i values if needed.
            UNSET --> dicts[k] uses i=dicts[k]['i'] if it exists, else i=k.
            None --> use i from dict if it exists, else None.
            int --> dicts[k] uses i=istart+k, ignoring any 'i' provided in dict.
        additional kwargs will be passed to cls.value_type.__init__
            (in case of conflict with any dicts values, use dicts values).
        '''
        if istart is UNSET:
            i_vals = [d.get('i', k) for k, d in enumerate(dicts)]
            dicts = [{**d, 'i': i} for i, d in zip(i_vals, dicts)]
        elif istart is None:
            dicts = [d if 'i' in d else {**d, 'i': None} for d in dicts]
        else:
            dicts = [{**d, 'i': istart+k} for k, d in enumerate(dicts)]
        return cls(cls.value_type(**kw_value_init, **d) for d in dicts)

    @classmethod
    def from_dict(cls, int_to_element):
        '''return DimensionValueList from dict of {i: element}.
        See also: cls.from_dicts()
        '''
        result = cls(el for i, el in sorted(int_to_element.items()))
        for i, el in enumerate(result):
            if (i != el.i) and (el.i is not None):
                raise ValueError(f"expected i and element.i to match. i={i}, element.i={el.i}. (element={el})")
        return result

    @classmethod
    def from_array(cls, array):
        '''return DimensionValueList from 0D or 1D array.
        array values should be DimensionValue objects, strings, or ints.
            DimensionValue objects --> use as-is
            strings --> use cls.value_type(s, i=i) for i in range(len(array))
            ints --> use cls.value_type(i=i) for i in array
        '''
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
            elif isinstance(v, str):
                result.append(cls.value_type(v, i=i))
            elif is_integer(v):
                result.append(cls.value_type(i=v))
            else:
                errmsg = (f'{cls.__name__}.from_array got unexpected value type at index {i}.\n'
                            f'Expected {cls.value_type.__name__}, str, or int; got value={v!r}.')
                raise InputError(errmsg)
        return cls(result)

    @classmethod
    def unique_from(cls, elements, *elements_as_args, istart=None):
        '''return DimensionValueList of unique elements from elements.
        equality checked via element.equal_except_i, i.e. ignore index.

        elements: iterable of DimensionValue of cls.value_type.
            or, single DimensionValue, in which case treat it as first arg,
            and can provide more elements as additional args.
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        # bookkeeping
        if elements_as_args:
            elements = (elements,) + elements_as_args
        else:
            ndim = getattr(elements, 'ndim', None)
            if ndim is None:
                ndim = 1 if is_iterable(elements) else 0
            if ndim == 0:
                elements = (elements,)
        # getting result
        result = []
        for e in elements:
            for r in result:
                if e.equal_except_i(r):
                    break
            else:  # did not break, i.e. element not found
                result.append(e)
        return cls(result, istart=istart)

    def unique(self, *, istart=None):
        '''return DimensionValueList of unique elements from self.
        equality checked via element.equal_except_i, i.e. ignore index.
        (if all elements are unique, return self, else return new DimensionValueList.)
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        result = []
        for e in self:
            for r in result:
                if e.equal_except_i(r):
                    break
            else:  # did not break, i.e. element not found
                result.append(e)
        cls = type(self)
        if len(result) == len(self):
            result = self.with_istart(istart)
        else:
            result = cls(result, istart=istart)
        return result

    # # # REINDEXING / MANIPULATING # # #
    reindexed = alias('with_istart')

    def with_istart(self, istart=0):
        '''return new DimensionValueList with elements reindexed, starting from istart.
        elements with incorrect i will be replaced with copies.
        if istart is None, just return self, unchanged.
        '''
        if istart is None:
            return self
        return type(self)(el.with_i(i=istart+i) for i, el in enumerate(self))

    # # # LOOKUPS / GETTING ELEMENTS # # #
    def lookup_dict(self):
        '''return dict for looking up elements given int or str (or element) in self.
        uses caching; assumes int(element) & str(element) never changes for any element.
        '''
        # [TODO] Doesn't work when changing distribution names using fluids[N].s = Name.
        try:
            lookup = self._lookup
        except AttributeError:
            lookup = dict()
            for element in self:
                lookup.update(element.lookup_dict())
            self._lookup = lookup
        return lookup

    def lookup(self, key, *, unique_missing_ok=False, handle_special=True):
        '''return element given int, str, or element in self. raise DimensionKeyError if key not in self.
        unique_missing_ok: bool
            whether it is okay for self to be missing key if key is a UniqueDimensionValue.
            if True and key is a UniqueDimensionValue, return key instead of raising error.
        handle_special: bool
            whether to handle DimensionSpecialValueSpecifier in special way,
                i.e. if key is a DimensionSpecialValueSpecifier, return key.getter(self).
        '''
        if unique_missing_ok and isinstance(key, UniqueDimensionValue):
            return key
        if handle_special and isinstance(key, DimensionSpecialValueSpecifier):
            return key.getter(self)
        try:
            return self.lookup_dict()[key]
        except KeyError:
            raise self._dimension_key_error(key) from None

    def get(self, key):
        '''return element(s) corresponding to key.
        key: None, int, str, element, DimensionSpecialValueSpecifier, range, slice, or tuple/list
            Some keys will look up and return corresponding element(s):
                nonnegative int, str, or element --> return corresponding element.
                DimensionSpecialValueSpecifier spec --> return spec.getter(self).
                tuple --> return tuple(self.get(k) for k in key)
                list --> return list(self.get(k) for k in key)
                range --> return type(self)(self.get(k) for k in key).
            Other keys will index self using the usual list-like indexing rules:
                None --> return self, unchanged.
                negative int --> return self[key], i.e. the key'th element, counting from end.
                slice --> return self[key], i.e. apply this slice to self.
                        Note that the result will have the same type as self.
                        Note that this supports interprets_fractional_indexing,
                          e.g. slice(0.3, 0.7) will slice(len(self) * 0.3, len(self) * 0.7).
            if any element in a tuple or list is not in self,
                keep it unchanged if it is a UniqueDimensionValue,
                else raise DimensionKeyError.
        Note that the result will always be single element, a tuple, a list, or a DimensionValueList.
        '''
        if key is None:
            return self
        elif isinstance(key, DimensionSpecialValueSpecifier):
            return key.getter(self)
        # index self like it is a list:
        elif isinstance(key, slice):
            key = interprets_fractional_indexing(key, len(self))
            return self[key]
        elif is_integer(key) and key < 0:
            return self[key]
        # index by looking up key(s) in self:
        elif isinstance(key, (tuple, list)):
            return type(key)(self.lookup(k, unique_missing_ok=True) for k in key)
        elif isinstance(key, range):
            return type(self)(self.lookup(k) for k in key)
        else:
            return self.lookup(key, unique_missing_ok=False)

    def indices(self, key, *, return_get=False, to_list=False):
        '''return indices of element(s) corresponding to key, during self.get(key).
        to_list: bool.
            True --> return [index] instead of index, if self.get(key) is a single DimensionValue.
        return_get: bool
            True --> return (indices, self.get(key)) instead of just indices.
        result will have same length as self.get(key); self[result[i]] is self.get(key)[i].
        '''
        id2index = {id(el): i for i, el in enumerate(self)}
        if len(id2index) != len(self):
            raise NotImplementedError(f'{type(self).__name__}.indices() with non-unique elements.')
        got = self.get(key)
        if isinstance(got, DimensionValue):
            if to_list:
                got = [got]
            else:
                return id2index[id(got)]
        indices = [id2index[id(g)] for g in got]
        return (indices, got) if return_get else indices

    def without_i(self, i, **kw_init):
        '''return a copy of self but dropping elements currently at these indices.
        i: int or iterable of int. indices to remove.
        kw_init are passed to __init__ when making the copy of self.
        '''
        if not is_iterable(i):
            i = [i]
        ikeep = sorted(set(range(len(self))) - set(i))
        return self.__getitem__(ikeep, **kw_init)

    def popped(self, key, *, return_indices=False, **kw_init):
        '''return (self.get(key), self.without_i(indices corresponding to key)).
        see help(self.get) for details on allowed keys.

        return_indices: bool
            if True, also return the indices (as a list) of the popped element(s),
            i.e. return (indices, popped element(s), self.without_i(...), self with elements removed).
            index will be None if no elements were removed.
        kw_init are used when making the copy of self. E.g. use istart=0 to make the copy start at 0.
        '''
        indices, pop = self.indices(key, return_get=True, to_list=True)
        newself = self.without_i(indices, **kw_init)
        return (index, pop, newself) if return_index else (pop, newself)

    # # # SERIALIZING # # #
    def to_dict(self):
        '''returns a list of dictionaries,
        each dictionary corresponds to each DimensionValue in the DimensionValueList.
        '''
        result_list = []
        for dimension_value in self:
            result_list.append(dimension_value.to_dict())
        return result_list

    def serialize(self):
        '''return serialization of self, into a list of dictionaries.'''
        # [TODO][EFF] use dimension_value.serialize(include_typename=False) for all except the first?
        result_list = []
        for dimension_value in self:
            result_list.append(dimension_value.serialize())
        return result_list


### --------------------- DimensionSpecialValueSpecifier --------------------- ###

class DimensionSpecialValueSpecifier():
    '''behaves in a special way when used to specify a dimension value:
        dim.v = specifier --> dim.v = specifier.getter(dim.values)
        dlist.get(specifier) --> specifier.getter(dlist)
    (for DimensionSpecialValueSpecifier specifier,
        Dimension dim, and DimensionValueList dlist.)
    
    getter: str or callable
        self specifies to use the dimension value(s): self.getter(dlist)
        callable --> callable of 1 arg; will be passed dlist.
        str --> use dlist.{getter}(). E.g. getter='get_ion' --> use dlist.get_ion().
        internally stored at self.init_getter.
    iseler: None, str, or callable
        if provided, can use self in calls to PlasmaCalcs' xarray_isel and xarray_sel,
            commonly via array.pc.sel(dim=self) or array.pc.isel(dim=self).
        None --> crash with InputError if used in xarray_isel or xarray_sel.
        callable --> callable of 1 arg; will be passed list of coord values for dim,
            (probably a list of DimensionValue objects, maybe converted to DimensionValueList).
            must return index (or indexes) appropriate for xarray.isel.
        str --> use dlist.{iseler}(), where dlist=isel_cls(list of coord values for dim).
            E.g. iseler='i_ions', isel_cls=FluidList --> use FluidList(values).i_ions().
        internally stored at self.init_iseler.
    isel_cls: UNSET, None, or type
        if provided, iseler calls use iseler(isel_cls(list of coord values for dim)),
        else, iseler calls use iseler(list of coord values for dim).
        (None --> set self.isel_cls = None. UNSET --> do not set self.isel_cls.)
    '''
    def __init__(self, getter, *args__None, iseler=None, isel_cls=UNSET, **kw__None):
        self.init_getter = getter
        if isinstance(getter, str):
            self.getter = self._getter_from_str
        else:
            self.getter = getter
        self.init_iseler = iseler
        if isinstance(iseler, str):
            self.iseler = self._iseler_from_str
        else:
            self.iseler = self._iseler_when_none
        if isel_cls is not UNSET:
            self.isel_cls = isel_cls

    def _getter_from_str(self, dlist):
        '''get the value from dlist specified by str self.getter.'''
        return getattr(dlist, self.init_getter)()

    def _iseler_from_str(self, dvals):
        '''get the indexes from dlist specified by str self.iseler.'''
        if getattr(self, 'isel_cls', None) is None:
            raise InputMissingError("coding error. self.isel_cls is required if using str iseler.")
        dlist = self.isel_cls(dvals.values)
        return getattr(dlist, self.init_iseler)()

    def _iseler_when_none(self, dvals):
        '''crash, because self was passed to xarray_isel or xarray_sel but self.iseler is None.'''
        raise InputError(f"{self} has iseler=None, so it cannot be used in xarray_isel or xarray_sel.")

    # # # DISPLAY # # #
    def _getter_as_str(self):
        '''returns str representation of self.getter.
        Use self.init_getter if it exists, else self.getter if it exists, else 'UNKNOWN_GETTER'.
        '''
        return getattr(self, 'init_getter', getattr(self, 'getter', 'UNKNOWN_GETTER'))

    def _iseler_as_str(self):
        '''returns str representation of self.iseler.
        Use self.init_iseler if it exists, else self.iseler if it exists, else 'UNKNOWN_ISELER'.
        '''
        return getattr(self, 'init_iseler', getattr(self, 'iseler', 'UNKNOWN_ISELER'))

    def _repr_contents(self):
        '''contents for repr; used by __repr__.'''
        result = [f'getter={self._getter_as_str}']
        if self.init_iseler is not None:
            result.append(f'iseler={self._iseler_as_str}')
        return result

    def __repr__(self):
        return f'{type(self).__name__}({", ".join(self._repr_contents())})'


class DimensionSingleValueSpecifier(DimensionSpecialValueSpecifier):
    '''DimensionSpecialValueSpecifier which includes checker, to check if single value matches.
    getter gets appropriate single value from list.
    checker checks if value is a match for this specifier.

    e.g. fluids.py defines ELECTRON,
        with getter calling FluidList.get_electron,
        and checker calling Fluid.is_electron().

    getter: str or callable
        self specifies to use the dimension value(s): self.getter(dlist)
        callable --> callable of 1 arg; will be passed dlist.
        str --> use dlist.{getter}(). E.g. getter='get_ion' --> use dlist.get_ion().
        internally stored at self.init_getter.
    checker: str or callable
        when checking value==self (or self==value): use self.checker(value)
        callable --> callable of 1 arg; will be passed value.
        str --> use value.{checker}(). E.g. checker='is_electron' --> use value.is_electron().
        internally stored at self.init_checker.
    iseler: None, str, or callable
        if provided, can use self in calls to PlasmaCalcs' xarray_isel and xarray_sel,
            commonly via array.pc.sel(dim=self) or array.pc.isel(dim=self).
        callable --> callable of 1 arg; will be passed list of coord values for dim,
            (probably a list of DimensionValue objects, maybe converted to DimensionValueList).
            must return index (or indexes) appropriate for xarray.isel.
        str --> use dlist.{iseler}(), where dlist=isel_cls(list of coord values for dim).
            E.g. iseler='i_ions', isel_cls=FluidList --> use FluidList(values).i_ions().
        internally stored at self.init_iseler.
    isel_cls: None or type
        if provided, iseler calls use iseler(isel_cls(list of coord values for dim)),
        else, iseler calls use iseler(list of coord values for dim).
    '''
    def __init__(self, getter, checker, *args_super, **kw_super):
        super().__init__(getter, *args_super, **kw_super)
        self.init_checker = checker
        if isinstance(checker, str):
            self.checker = self._checker_from_str
        else:
            self.checker = checker

    def _checker_from_str(self, value):
        '''check if value is a match for str self.checker.'''
        return getattr(value, self.init_checker)()

    # # # DISPLAY # # #
    def _checker_as_str(self):
        '''returns str representation of self.checker.
        Use self.init_checker if it exists, else self.checker if it exists, else 'UNKNOWN_CHECKER'.
        '''
        return getattr(self, 'init_checker', getattr(self, 'checker', 'UNKNOWN_CHECKER'))

    def _repr_contents(self):
        '''contents for repr; used by __repr__.'''
        result = super()._repr_contents()
        result.append(f'checker={self._checker_as_str}')
        return result


class DimensionSpecialValue(DimensionSingleValueSpecifier):
    '''a single special value for a dimension, which doesn't necessarily appear in '''


class DimensionFractionalIndexer(DimensionSpecialValueSpecifier):
    '''DimensionSpecialValueSpecifier which specifies to do interprets_fractional_indexing.
    
    Example:
        indexer = DimensionFractionalIndexer(0.5)
        snaps.get(indexer) --> gets the value at 0.5*len(snaps).
        DimensionFractionalIndexer([0.2, 0.3])  # values at 0.2*len(dlist) and 0.3*len(dlist).
        DimensionFractionalIndexer(slice(0, None, 0.1))  # values at 0%, 10%, 20%, ..., of len(dlist).
    '''
    def __init__(self, indexer, *args__None, **kw__None):
        self.indexer = indexer

    def _getter_as_str(self):
        '''return str representation of self.indexer.'''
        return self.indexer

    def getter(self, dlist):
        '''get the value(s) from dlist specified by self.indexer, with interprets_fractional_indexing.'''
        indexes = interprets_fractional_indexing(self.indexer, len(dlist))
        return dlist[indexes]


### --------------------- SpecialDimensionValue --------------------- ###

class SpecialDimensionValue(DimensionValue, DimensionSpecialValueSpecifier):
    '''a special dimension value, not corresponding to a usual value from a DimensionValueList.
    E.g., BifrostScrSnap is a SpecialDimensionValue for the snap corresponding to the scr files.
        Even though BifrostScrSnap instances won't appear in BifrostSnapList,
        we still want to allow bifrost_calculator.snap = BifrostScrSnap(...).
    '''
    def getter(self, dlist):
        '''get the value from dlist specified by self.
        (Here, just returns self, the SpecialDimensionValue)
        '''
        return self


### --------------------- UniqueDimensionValue --------------------- ###

class UniqueDimensionValue(Sentinel, SpecialDimensionValue):
    '''a unique dimension value, not corresponding to a usual value from a DimensionValueList.
    E.g., INPUT_SNAP (defined in snaps.py) is the UniqueDimensionValue for the snap corresponding to the input deck.

    Cannot provide any args or kwargs to __init__.
    Equality with other dimension values only holds if the other value is a UniqueDimensionValue of the same type.
    str(UniqueDimensionValue) will return the type name.
    int(UniqueDimensionValue) will return None.
    '''
    _kw_def = {'name'}
    # _kw_copy = {'name'}   # might be necessary if subclasses are editing _kw_copy defaults, but not sure...

    def __init__(self, *args__None, **kw__None):
        pass  # do nothing (instead of super().__init__)

    i = None
    name = None  # overwrite parent's 'name' property, if one exists...
    s = alias('name')  # from Sentinel

    def __hash__(self):
        return super().__hash__()  # we need to do this since we define __eq__ here...

    def __eq__(self, other):
        return type(self) == type(other)

    def copy(self, **kw__None):
        '''return self; self is a Sentinel so there is only 1 instance.'''
        return self
