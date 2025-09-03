"""
File Purpose: tools for iterables
"""
import operator

import numpy as np

from . import properties  # for unambiguous "alias" inside DictWithAliases class.
from .properties import alias, alias_child, simple_property
from .sentinels import UNSET
from .timing import ProgressUpdater
from ..errors import InputError, InputMissingError, InputConflictError, DimensionalityError
from ..defaults import DEFAULTS


### --------------------- Misc --------------------- ###

def is_iterable(x):
    '''returns True if x is iterable, False otherwise.'''
    try:
        iter(x)
        return True
    except TypeError:
        return False

def is_dictlike(x):
    '''returns True if x is dict-like, False otherwise.
    returns x.is_dictlike if it exists,
    else returns whether x has keys() and __getitem__.
    '''
    try:
        x_is_dictlike = x.is_dictlike
    except AttributeError:
        return hasattr(x, 'keys') and hasattr(x, '__getitem__')
    else:
        return x_is_dictlike()

def argmax(iterable):
    '''returns first occurence of maximum value in iterable.
    converts iterable to tuple before beginning search.
    [EFF] might not be efficient for large iterables, but it's probably fine.
    '''
    l = tuple(iterable)
    return l.index(max(l))

def rargmax(iterable):
    '''returns first occurence of maximum value in iterable, starting search from the end.
    converts iterable to tuple before beginning search.
    [EFF] might not be efficient for large iterables, but it's probably fine.
    '''
    l = tuple(iterable)
    return len(l) - 1 - l[::-1].index(max(l))

def scalar_item(arraylike):
    '''returns the single item from arraylike. raise InputError if not possible.
    if arraylike.ndim or .size exists:
        return arraylike.item() if ndim==0 or size==1, else crash.
    else:
        return arraylike[0] if len(arraylike)==1, else crash.
    '''
    if hasattr(arraylike, 'ndim') or hasattr(arraylike, 'size'):
        if getattr(arraylike, 'ndim', None) == 0 or getattr(arraylike, 'size', None) == 1:
            return arraylike.item()
        else:
            errmsg = f'expected array with ndim==0 or size==1, but got ndim={ndim} and size={size}'
            raise InputError(errmsg)
    else:
        if len(arraylike) == 1:
            return arraylike[0]
        else:
            errmsg = f'expected iterable with len==1, but got len={len(arraylike)}'
            raise InputError(errmsg)


### --------------------- dict with aliases --------------------- ###

class DictWithAliases(dict):
    '''dict but some keys are aliases for other keys.
    E.g. d = AliasDict({'x': 7}); d.alias('x', 'y');
        d['y'] == d['x'] == 7
        d['y'] = 8
        d['y'] == d['x'] == 8

    Checking "key in self" also checks aliases.
        (use "key in self.keys()" to exclude aliases.)
    Looping through self.keys() or self.items() does NOT include aliases.

    add alias via self.alias(key0, key1),
        and/or provide dict of aliases during __init__.
    '''
    DEFAULT_ALIASES = {}  # dict of {alias: official key}

    aliases = simple_property('_aliases', setdefaultvia='_default_aliases', setable=False,
        doc='''aliases known by this dict. aliases is a dict of {alias: key}''')
        # aliases.keys() must be the aliases because each key can have multiple aliases.

    def _default_aliases(self):
        '''returns default aliases for this dict.
        the implementation here just returns self.DEFAULT_ALIASES.copy().
        '''
        return self.DEFAULT_ALIASES.copy()

    def __init__(self, *args_dict, aliases=UNSET, **kwargs_dict):
        '''initialize self with key-value pairs, and optionally aliases.
        aliases: UNSET, or dict of {key1: key0} pairs to be aliased.
            UNSET --> self will use self.DEFAULT_ALIASES.
            dict --> self.alias(key0, key1) for each (key0, key1) pair.
                    (key1 is more likely to become the "alias", internally.)
        '''
        super().__init__(*args_dict, **kwargs_dict)
        if aliases is not UNSET:
            self.add_aliases(aliases)

    def __getitem__(self, key):
        return super().__getitem__(self.aliases.get(key, key))

    def __setitem__(self, key, value):
        return super().__setitem__(self.aliases.get(key, key), value)

    def __delitem__(self, key):
        '''deletes value associated with key (or alias) from self.
        does NOT alter anything about known aliases.
        '''
        return super().__delitem__(self.aliases.get(key, key))

    def pop(self, key, default=UNSET):
        '''pop key from self, returning self[key].
        does NOT alter anything about known aliases.

        default: UNSET or any value
            if key not in self, return default if provided (i.e., not UNSET)
        '''
        if default is UNSET:
            return super().pop(self.aliases.get(key, key))
        else:
            return super().pop(self.aliases.get(key, key), default)

    def update(self, *args_dict, **kwargs_dict):
        '''update self with new key-value pairs.
        does NOT alter anything about known aliases.
        handles appropriately any known aliases in key implied by *args and **kwargs.
        '''
        for k, v in dict(*args_dict, **kwargs_dict).items():
            self[self.aliases.get(k, k)] = v

    def copy(self):
        '''return a shallow copy of self. Result aliases are the same as self.aliases.'''
        return type(self)(self)

    def __contains__(self, key):
        return super().__contains__(self.aliases.get(key, key))

    @property
    def _known_nonalias_keys(self):
        '''all keys known by self as "official" keys (not aliases).
        (official keys and aliases behave the same way - user shouldn't need to worry about this.)
        set of all self.keys() plus all values in self.aliases.
        '''
        return set(self.keys()) | set(self.aliases.values())

    def alias(self, key0, key1):
        '''tell self to treat these keys as the same key.
        key0 is more likely to become the official key, while key1 will be the alias.
        (however, if either is already known to self, decides "official vs alias" appropriately.)
        '''
        # decide which is the "official" key (in self.keys()) and which is the alias.
        if key0 == key1:
            raise InputConflictError(f'cannot alias key to itself: key={key0!r}')
        known_nonalias_keys = self._known_nonalias_keys
        if key0 in known_nonalias_keys:
            official, alias = key0, key1
        elif key1 in known_nonalias_keys:
            official, alias = key1, key0
        else:  # we have no prior info about these keys. Use default: official = key0.
            official, alias = key0, key1
        # check for conflict with existing keys
        if official in self.keys() and alias in self.keys():
            raise InputError( f'cannot alias({key0!r}, {key1!r}); both keys already in self.keys()!')
        # check for conflict with existing aliases.
        if alias in self.aliases:
            if self.aliases[alias] != official:
                errmsg = (f'alias({key0!r}, {key1!r}) conflicts with existing alias: '
                         f'{alias!r} <--> {self.aliases[alias]!r}.'
                         f'\nConsider using self.un_alias to remove a known alias.')
                raise InputError(errmsg)
        # done!
        self.aliases[alias] = official

    add_alias = properties.alias('alias')  # a perfectly sensible line of code :)

    def add_aliases(self, aliases):
        '''add multiple aliases at once.
        aliases: dict of {alias: key} pairs.

        Equivalent to calling self.alias(key, alias) for each (alias, key) pair.
        '''
        for alias, key in aliases.items():
            self.alias(key, alias)

    def un_alias(self, alias):
        '''remove alias from self.
        If alias is an "official" key with a known alias,
            swap the alias for the official key, then remove the previously-official key.
        '''
        raise NotImplementedError('[TODO] DictWithAliases.un_alias')

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [super().__repr__()]
        if len(self.aliases)>0:
            contents.append(f'aliases={self.aliases}')
        contents_str = f",\n{DEFAULTS.TAB}".join(contents)
        return f'{type(self).__name__}({contents_str})'


### --------------------- custom Dictlike --------------------- ###

class DictlikeFromKeysAndGetitem():
    '''Dict-like object, assuming keys() and __getitem__ are defined.'''
    def __getitem__(self, key):
        '''get value for this key'''
        raise NotImplementedError(f'{type(self).__name__}.__getitem__')

    def keys(self):
        '''return tuple of keys in self.'''
        raise NotImplementedError(f'{type(self).__name__}.keys()')

    def __iter__(self):
        '''raises TypeError; use .keys(), .values(), or .items() instead.'''
        raise TypeError(f'{type(self).__name__} is not iterable; use .keys(), .values(), or .items() instead.')

    def values(self):
        '''return tuple of values corresponding to self.keys().'''
        return tuple(self[key] for key in self.keys())

    def items(self):
        '''return tuple of (key, value) pairs corresponding to self.keys() and self.values().'''
        return tuple(zip(self.keys(), self.values()))

    def get(self, key, default=UNSET):
        '''return self[key]. if default is provided and self[key] doesn't exist, return default.'''
        try:
            return self[key]
        except KeyError:
            if default is UNSET:
                raise
            return default


### --------------------- partitioning stuff --------------------- ###

class Partition(DictlikeFromKeysAndGetitem):
    '''(ordered) dict of lists partitioned by category.
    (assumes python >= 3.7, i.e. dict order is guaranteed to be insertion order)
    self assumes it will remain unchanged after originally being created.

    self.partition stores {key: list of elements in category}
    self.idx stores {key: list of indices of elements in original}
    self.flat stores all elements in category order, in a single list.
    self.idx_flat concatenates self.idx.values().
    self.ridx stores {key: [i such that self.flat[i] == x for x in this category]}
    self.ridx_flat stores [i such that self.flat[i] == x for x in original]

    iterating through self yields (key, value) pairs.

    original: list-like
        the original iterable, to be partitioned.
    f: callable
        maps original elements to category keys. categories must be hashable.
        Will call f(x) for x in original, to determine categories.
    keys: ordered list of categories
        use these as known categories if provided.
    '''
    def __init__(self, original, f, *, keys=[]):
        self.original = original
        self.f = f
        self._init_keys = keys
        self.init_all()

    def init_all(self):
        '''init all the things, based on self.original, self.f, and self._init_keys'''
        self.init_partition()
        self.init_flat()
        self.init_ridx()

    def init_partition(self):
        '''creates self.partition and self.idx'''
        f = self.f
        partition = dict()
        idx = dict()
        for key in getattr(self, '_init_keys', []):
            partition[key] = []
            idx[key] = []
        for i, x in enumerate(self.original):
            key = f(x)
            partition.setdefault(key, []).append(x)
            idx.setdefault(key, []).append(i)
        self.partition = partition
        self.idx = idx

    def init_flat(self):
        '''create self.flat and self.idx_flat.
        self.flat stores all elements in order of categories, in a single list.
        self.idx_flat stores the indices of all elements in self.flat.
        '''
        flat = []
        for key in self.keys():
            flat.extend(self.partition[key])
        self.flat = flat
        idx_flat = []
        for key in self.keys():
            idx_flat.extend(self.idx[key])
        self.idx_flat = idx_flat

    def init_ridx(self):
        '''create self.ridx and self.ridx_flat.
        self.ridx stores {key: [i such that self.flat[i] == x for x in this category]}
        self.ridx_flat stores [i such that self.flat[i] == x for x in original]
        '''
        ridx_flat = []
        for i, x in enumerate(self.flat):
            ridx_flat.append(self.idx_flat.index(i))
        self.ridx_flat = ridx_flat
        ridx = dict()
        istart = 0
        for key in self.keys():
            cat_len = len(self.partition[key])
            ridx[key] = ridx_flat[istart:istart+cat_len]
            istart = istart + cat_len
        self.ridx = ridx

    def __getitem__(self, key):
        return self.partition[key]

    def keys(self):
        return list(self.partition.keys())

    # intentionally does not define __setitem__; expects to remain unchanged after __init__.

    def __iter__(self):
        '''iterate through (key, val) pairs.'''
        return iter(self.partition.items())

    def __contains__(self, key):
        '''tells whether key is in self.partition'''
        return key in self.partition

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}({self.partition})'


class PartitionFromXarray(Partition):
    '''(ordered) dict of lists partitioned by category.
    (assumes python >= 3.7, i.e. dict order is guaranteed to be insertion order)
    self assumes it will remain unchanged after originally being created.

    self.partition stores {key: list of elements in category}
    self.idx stores {key: list of indices of elements in original}
    self.flat stores all elements in category order, in a single list.
    self.idx_flat concatenates self.idx.values().
    self.ridx stores {key: [i such that self.flat[i] == x for x in this category]}
    self.ridx_flat stores [i such that self.flat[i] == x for x in original]

    iterating through self yields (key, value) pairs.

    xarray: xarray.DataArray with ndim <= 1
        data array determining partition category for o in original.
        self.partition keys will be values of xarray;
        partition values will be lists of o from original for which xarray[coord] == o.
        E.g. xr.DataArray(['a', 'a', 'b', 'a', 'c'], coords={coord: ['o1', 'o2', 'o3', 'o4', 'o5']})
            --> self.partition = {'a': ['o1', 'o2', 'o4'], 'b': ['o3'], 'c': ['o5']}
    coord: None or str
        coordinate of xarray containing all values from original.
        None --> infer as coord = xarray.dims[0] if ndim=1,
                 else xarray.coords[0] if ndim=0 and len(xarray.coords)==1,
                 else crash.
    original: None or list-like
        the original iterable, to be partitioned.
        None --> use list(xarray[coord].values).
    '''
    def __init__(self, xarray, coord=None, original=None):
        if not hasattr(xarray, 'ndim'):
            raise InputError(f'expected xarray-like object, but obj does not even have ndim attr: obj={obj}')
        if xarray.ndim >= 2:
            raise DimensionalityError(f'PartitionFromXarray expects xarray.ndim<=1; got {xarray.ndim}.')
        self.xarray = xarray
        if coord is None:
            if xarray.ndim == 1:
                coord = xarray.dims[0]
            elif xarray.ndim == 0:
                if len(xarray.coords) == 1:
                    coord = list(xarray.coords)[0]
                else:
                    raise InputMissingError(f'coord, when xarray.ndim=0 and len(xarray.coords)>1')
            else:
                raise InputMissingError(f'coord, when xarray.ndim>1')
        if original is None:
            original = list(xarray[coord].values)
        self.original = original
        self.coord = coord
        self.init_all()

    def f(self, x):
        '''return category for x.'''
        # don't use xarray.sel; use == instead:
        cname = self.coord
        array = self.xarray
        cvals = array[cname].values
        if array.ndim == 0:
            if x == cvals.item():
                return array.item()
        else:
            for i, c in enumerate(cvals):
                if x == c:
                    return array.isel({cname: i}).item()
        raise InputConflictError(f'x={x!r} not found in self.xarray[{cname!r}]; cannot determine f(x)')


### --------------------- Generic Containers --------------------- ###

class Container():
    '''a container for multiple objects, & rules for enumerating & indexing.
    Here, implements self.__getitem__ so that self[i]=self.data[i],
        and self.enumerate which yields (i, self[i]) pairs.
    subclass should implement __init__, _enumerate_all, and new_empty.
    '''
    # # # THINGS THAT SUBCLASS SHOULD IMPLEMENT # # #
    def __init__(self, stuff):
        '''should set self.data = something related to stuff.'''
        raise NotImplementedError(f'{self.__class__.__name__}.__init__')

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.
        Equivalent to self.enumerate(idx=None).
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}._enumerate_all')

    def new_empty(self, fill=UNSET):
        '''return a new container of the same shape as self, filled with the value fill.
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}.new_empty')

    def _size_all(self):
        '''return the number of objects in the container.
        The implementation will depend on the container type; subclass should implement.
        '''
        raise NotImplementedError(f'{self.__class__.__name__}.size_all')

    # # # GETITEM & ENUMERATE # # #
    def __getitem__(self, idx):
        return self.data[idx]

    def enumerate(self, idx=None):
        '''iterate through i in idx, yielding (i, self[i]) pairs.
        If idx is None, iterate through all objs in self (see self._enumerate_all).
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if idx is None:
            for i, selfi in self._enumerate_all():
                yield (i, selfi)
        else:
            for i in idx:
                yield (i, self[i])

    def size(self, idx=None):
        '''return the number of objects in the container, or in idx if provided.'''
        if idx is None:
            return self._size_all()
        return len(idx)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{self.__class__.__name__}({self.data})'


class ContainerOfList(Container):
    '''a list-like container.'''
    def __init__(self, objs):
        self.data = [o for o in objs]

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return enumerate(self.data)

    def new_empty(self, fill=UNSET):
        '''return a new list of the same shape as self, filled with the value fill.'''
        return [fill for _ in self.data]

    def _size_all(self):
        '''the number of objects in this container. == len(self.data)'''
        return len(self.data)


class ContainerOfArray(Container):
    '''a numpy-array-like container.'''
    def __init__(self, arr):
        self.data = np.asanyarray(arr)

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return np.ndenumerate(self.data)

    def new_empty(self, fill=UNSET):
        '''return a new array of the same shape as self, filled with the value fill.'''
        return np.full_like(self.data, fill, dtype=object)

    def _size_all(self):
        '''the number of objects in this container. == self.data.size'''
        return self.data.size

    shape = alias_child('data', 'shape')
    ndim = alias_child('data', 'ndim')
    dtype = alias_child('data', 'dtype')


class ContainerOfDict(Container):
    '''a dict-like container.'''
    def __init__(self, d):
        self.data = dict(d)  # copy the dict (and ensure dict-like)

    def _enumerate_all(self):
        '''iterate through all objs in self, yielding (i, self[i]) pairs.'''
        return self.data.items()

    def new_empty(self, fill=UNSET):
        '''return a new dict of the same shape as self, filled with the value fill.'''
        return {k: fill for k in self.data.keys()}

    def _size_all(self):
        '''the number of objects in this container. == len(self.data)'''
        return len(self.data)


### --------------------- Bijection --------------------- ###

class Bijection(dict):
    '''stores forward and backward mapping.
    behaves like forward mapping, but self.inverse is the reverse mapping.
    '''
    inverse = simple_property('_inverse', setdefault=dict,
        doc='''reverse mapping. {value: key} for all items in this bijection.''')

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.inverse[value] = key

    def __getitem__(self, key):
        result = super().__getitem__(key)
        return result

    def __delitem__(self, key):
        value = self.pop(key)

    def clear(self):
        '''clear all items from this bijection.'''
        super().clear()
        self.inverse.clear()

    def pop(self, key, default=UNSET):
        '''pop the value for this key, and return it.'''
        value = super().pop(key, default)
        if value is not UNSET:
            del self.inverse[value]
        return value

    def popitem(self):
        '''pop an item from this bijection, and return it.'''
        key, value = super().popitem()
        del self.inverse[value]
        return key, value

    def update(self, *args, **kw):
        '''update this bijection with new items.'''
        super().update(*args, **kw)
        self.inverse.update({v: k for k, v in self.items()})

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'


class BijectiveMemory(Bijection):
    '''bijection which also stores the next key to use. Keys should be numbers.
    self.nextkey is never decremented (don't "fill in gaps" after deleting keys)
    '''
    nextkey = simple_property('_nextkey', setdefaultvia='_default_nextkey',
        doc='''next key for self.key(value) if new value.
        nextkey >= max(self.keys(), default=-1) + 1.''')
    def _default_nextkey(self):
        return max(self.keys(), default=-1) + 1

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.nextkey = max(self.nextkey, key) + 1

    def update(self, *args, **kw):
        super().update(*args, **kw)
        self.nextkey = max([self.nextkey-1, *self.keys()]) + 1

    def key(self, value):
        '''return the key associated with this value; store the value if not already stored.'''
        if value in self.inverse:
            return self.inverse[value]
        else:
            key = self.nextkey
            self[key] = value
            return key


### --------------------- SymmetricPairMapping --------------------- ###

class SymmetricPairMapping():
    '''mapping with keys pairs, where order of the pair doesn't matter.

    mapping: dict of {(obj1, obj2): value}

    The keys (obj2, obj1) and (obj1, obj2) will be treated the same way,
        when getting/setting/deleting items, and when checking if key in self.
        [EFF] For efficiency, only stores one of these pairs (the one where obj1 <= obj2).
    '''
    def __init__(self, mapping=dict()):
        self.mapping = dict()
        for key, value in mapping.items():
            self[key] = value

    def _sanitize_key(self, key):
        '''return sanitized key (obj1, obj2) such that obj1 <= obj2.'''
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError(f'key={key!r} must be a tuple of 2 objs')
        if key[1] < key[0]:
            key = (key[1], key[0])
        return key
    
    def __setitem__(self, key, value):
        key = self._sanitize_key(key)
        self.mapping[key] = value

    def __getitem__(self, key):
        key = self._sanitize_key(key)
        return self.mapping[key]

    def __delitem__(self, key):
        key = self._sanitize_key(key)
        del self.mapping[key]

    def __contains__(self, key):
        key = self._sanitize_key(key)
        return key in self.mapping

    def update(self, other):
        '''update self with other.
        other: dict of {(obj1, obj2): value}
        '''
        for key, value in other.items():
            self[key] = value

    def clear(self):
        '''remove all known items from self.'''
        self.mapping.clear()

    def pop(self, key, default):
        '''remove self[key], and return its value. if key not in self, return default.'''
        key = self._sanitize_key(key)
        return self.mapping.pop(key, default)

    def __len__(self):
        return len(self.mapping)
    def values(self):
        return self.mapping.values()
    def items(self):
        return self.mapping.items()
    def keys(self):
        return self.mapping.keys()

    def __iter__(self):
        '''iterate over self.items (not self.keys).'''
        return iter(self.items())

    def copy(self):
        '''return a shallow copy of self.'''
        return type(self)(self.mapping)

    def __eq__(self, other):
        if not isinstance(other, SymmetricPairMapping):
            return False
        return self.mapping == other.mapping

    # # # DISPLAY # # #
    _repr_newlines = False  # whether to put newlines between keys in repr.

    def __repr__(self):
        if self._repr_newlines:
            SEP = f'\n{DEFAULTS.TAB}'
            JOINSEP = f',{SEP}'
            contents = [f'{k}: {v!r}' for k, v in self.mapping.items()]
            STARTSEP = SEP if len(contents) > 1 else ''
            ENDSEP = f'\n' if len(contents) > 3 else ''
            return f'{type(self).__name__}({STARTSEP}{JOINSEP.join(contents)}{ENDSEP})'
        else:
            return f'{type(self).__name__}({self.mapping!r})'


### --------------------- DictOfSimilar --------------------- ###

class DictOfSimilar(dict):
    '''dict of similar objects with similar attributes.
    similar attributes list stored in SIMILAR_ATTRS.

    In many ways, simply broadcasts operations to all values in the dict.

    See self.to_ds(), to_da(), and to_xr() for helpful methods to convert result to xarray objects
        (These are defined in xarray_tools and bound to the DictOfSimilar class there).
    '''
    REPR_ITEM_MAXLEN = 50  # max length for repr for a single item; abbreviate if longer.
    SIMILAR_ATTRS = []
    cls_new = None  # if provided, use this to create new objects instead of type(self).

    def _new(self, *args, **kw):
        '''return a new DictOfSimilar of the same type as self.'''
        cls = type(self) if self.cls_new is None else self.cls_new
        return cls(*args, **kw)

    def apply(self, func, *args, **kw):
        '''return func(obj, *args, **kw) for each object in self.'''
        result = dict()
        for k, obj in self.items():
            result[k] = func(obj, *args, **kw)
        return self._new(result)

    do = alias('apply')

    gi = alias('getitems')
    si = alias('setitems')
    ga = alias('getattrs')
    sa = alias('setattrs')
    ca = alias('callattrs')

    def getitems(self, i):
        '''get obj[i] for each object in self.'''
        result = dict()
        for k, obj in self.items():
            result[k] = obj[i]
        return self._new(result)

    def setitems(self, i, value):
        '''set obj[i] = value for each object in self.'''
        for obj in self.values():
            obj[i] = value

    def getattrs(self, attr, default=UNSET):
        '''get obj.attr for each object in self.'''
        result = dict()
        for k, obj in self.items():
            if default is UNSET:
                result[k] = getattr(obj, attr)
            else:
                result[k] = getattr(obj, attr, default)
        return self._new(result)

    def setattrs(self, attr, value):
        '''set obj.attr = value for each object in self.'''
        for obj in self.values():
            setattr(obj, attr, value)

    def callattrs(self, attr, *args, dos_verbose=False, **kw):
        '''call obj.attr(*args, **kw) for each object in self.
        dos_verbose: bool or number
            whether to print progress updates from DictOfSimilar while looping.
            False or <=0 --> no updates
            True --> updates every 5 seconds
            >=2 and <5 --> updates every 2 seconds
            >=5 --> updates every loop iteration
        '''
        result = dict()
        updater = self._updater(dos_verbose)
        for i, (k, obj) in enumerate(self.items()):
            updater.print(f'Calling {i+1:2d} of {len(self)}: {k!r}')
            result[k] = getattr(obj, attr)(*args, **kw)
        updater.finalize(f'<{type(self).__name__} at {hex(id(self))}>.callattrs({attr!r})', always=False)
        return self._new(result)

    def __call__(self, *args, dos_verbose=True, **kw):
        '''call obj(*args, **kw) for each object in self.
        dos_verbose: bool or number
            whether to print progress updates from DictOfSimilar while looping.
            False or <=0 --> no updates
            True --> updates every 5 seconds
            >=2 and <5 --> updates every 2 seconds
            >=5 --> updates every loop iteration
        '''
        result = dict()
        updater = self._updater(dos_verbose)
        for i, (k, obj) in enumerate(self.items()):
            updater.print(f'Calling {i+1:2d} of {len(self)}: {k!r}')
            result[k] = obj(*args, **kw)
        updater.finalize(f'<{type(self).__name__} at {hex(id(self))}>.__call__', always=False)
        return self._new(result)

    def _updater(self, dos_verbose, *, wait=True):
        '''return ProgressUpdater with print_freq appropriate for dos_verbose.
        dos_verbose: bool or number
            whether to print progress updates from DictOfSimilar while looping.
            False or <=0 --> no updates
            True --> updates every 5 seconds
            >=2 and <5 --> updates every 2 seconds
            >=5 --> updates every loop iteration
        '''
        if (not dos_verbose) or dos_verbose <= 0:
            print_freq = -1
        elif dos_verbose >= 5:
            print_freq = 0
        elif dos_verbose >= 2:
            print_freq = 2
        else:
            print_freq = 5
        return ProgressUpdater(print_freq, wait=wait)

    # # # MISC. CONVENIENCE # # #
    def subset(self, keep=None, *, drop=None):
        '''return DictOfSimilar like self but with only a subset of the keys from self.
        
        keep: None, iterable, or callable
            None --> no restrictions from `keep`
            iterable --> only keep self[k] for k in keep.
            callable --> only keep (k,v) from self.items() if keep(k, v).
        drop: None, iterable, or callable
            None --> no restrictions from `drop`
            iterable --> drop self[k] for k in drop.
            callable --> drop (k,v) from self.items() if drop(k, v).
        If any conflict between drop and keep, drop takes priority.
        (E.g. if 'key1' in keep and in drop, it will be dropped, not kept.)
        '''
        if keep is None:
            keep = list(self.keys())
        elif callable(keep):
            keeping = []  # could do list comprehension, but loop makes debugging easier if crash.
            for k, v in self.items():
                if keep(k, v):
                    keeping.append(k)
            keep = keeping
        result = {k: self[k] for k in keep}
        if drop is None:
            drop = []
        elif callable(drop):
            dropping = []  # could do list comprehension, but loop makes debugging easier if crash.
            for k, v in result.items():
                if drop(k, v):
                    dropping.append(k)
            drop = dropping
        for k in drop:
            result.pop(k, None)
        try:
            _orig_cls_new = self.cls_new
            self.cls_new = None  # e.g., MultiCalculator self -> MultiCalculator result, not DictOfSimilar.
            result = self._new(result)
        finally:
            self.cls_new = _orig_cls_new
        return result

    # # # SIMILAR ATTRS BEHAVIOR # # #
    def __getattr__(self, attr):
        '''self.getattrs(attr) if attr in SIMILAR_ATTRS. Else raise AttributeError.
        (Only invoked when object.__getattr__(self, attr) fails.)
        '''
        if attr in self.SIMILAR_ATTRS:
            return self.getattrs(attr)
        else:
            raise AttributeError(f'{type(self).__name__} object has no attribute {attr!r}')

    def __setattr__(self, attr, value):
        '''self.setattrs(attr, value) if attr in SIMILAR_ATTRS, otherwise super().__setattr__.'''
        if attr in self.SIMILAR_ATTRS:
            return self.setattrs(attr, value)
        else:
            return super().__setattr__(attr, value)

    def __getitem__(self, i):
        '''self[i[0]].getitems(i[1]) if i tuple and i[0] in SIMILAR_ATTRS.
            (e.g. self['snap', 0] returns self['snap'].getitems(0)
        otherwise, try super().__getitem__.
        if that fails, try to return list(self.values())[i]
            (e.g., self[3] will return 3rd object, unless 3 in self.keys())
        '''
        if isinstance(i, tuple) and i[0] in self.SIMILAR_ATTRS:
            return self.getattrs(i[0]).getitems(i[1])
        else:
            try:
                return super().__getitem__(i)
            except KeyError:
                return list(self.values())[i]

    def __setitem__(self, i, value):
        '''self.setitems(i[1], value) if i tuple and i[0] in SIMILAR_ATTRS. otherwise super().__setitem__.'''
        if isinstance(i, tuple) and i[0] in self.SIMILAR_ATTRS:
            return self.getattrs(i[0]).setitems(i[1], value)
        else:
            return super().__setitem__(i, value)

    # # # ARITHMETIC APPLIES ACROSS ALL VALUES # # #
    def _math_op(self, other, op):
        '''apply op to self and other. If other is a dict, apply op to self[k] and other[k] for each k.
        Otherwise, apply op to each value in self and other.
        '''
        if is_dictlike(other):
            return self._new({k: op(self[k], other[k]) for k in self})
        else:
            return self.apply(op, other)

    def __add__(self, other):
        '''self + other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.add)

    def __radd__(self, other):
        '''other + self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y + x)

    def __sub__(self, other):
        '''self - other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.sub)

    def __rsub__(self, other):
        '''other - self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y - x)

    def __mul__(self, other):
        '''self * other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.mul)

    def __rmul__(self, other):
        '''other * self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y * x)

    def __truediv__(self, other):
        '''self / other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.truediv)

    def __rtruediv__(self, other):
        '''other / self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y / x)

    def __floordiv__(self, other):
        '''self // other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.floordiv)

    def __rfloordiv__(self, other):
        '''other // self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y // x)

    def __mod__(self, other):
        '''self % other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.mod)

    def __rmod__(self, other):
        '''other % self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y % x)

    def __pow__(self, other):
        '''self ** other. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, operator.pow)

    def __rpow__(self, other):
        '''other ** self. At each key if other is a dict, else apply to each value in self.'''
        return self._math_op(other, lambda x, y: y ** x)

    def __pos__(self):
        '''+self. Apply to each value in self.'''
        return self.apply(operator.pos)

    def __neg__(self):
        '''-self. Apply to each value in self.'''
        return self.apply(operator.neg)

    # # # DISPLAY # # #
    def __repr__(self):
        MAXLEN = self.REPR_ITEM_MAXLEN
        orig_reprs = {k: repr(v) for k, v in self.items()}
        short_reprs = dict()
        for k, v in orig_reprs.items():
            if len(v) > MAXLEN:
                short_reprs[k] = f'<{v[:MAXLEN]}...>'.replace('\n', '  ')
            else:
                short_reprs[k] = v
        contents = [f'{k!r}: {v}' for k, v in short_reprs.items()]
        return f'{type(self).__name__}({{{", ".join(contents)}}})'

    def __str__(self):
        '''like repr but never abbreviate. Also, use str of objs.'''
        orig = {k: str(v) for k, v in self.items()}
        contents = [f'{k!r}: {v}' for k, v in orig.items()]
        content_str = ",\n".join(contents)
        return f'{type(self).__name__}({{{content_str}}})'
