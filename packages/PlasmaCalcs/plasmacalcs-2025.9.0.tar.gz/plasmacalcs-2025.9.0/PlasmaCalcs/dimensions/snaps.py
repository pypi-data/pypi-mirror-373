"""
File Purpose: Snap, SnapList, SnapDimension, SnapHaver

"snap" is shorthand for "snapshot".
"""
import numpy as np

from .dimension_tools import (
    DimensionValue, DimensionValueList, UniqueDimensionValue,
    DimensionSpecialValueSpecifier,
    Dimension, DimensionHaver,
)
from ..errors import (
    SnapKeyError, SnapValueError, InputError,
    FileContentsConflictError,
    DimensionalityError,
)
from ..tools import (
    elementwise_property,
    xarray_assign,
    format_docstring,
    NO_VALUE, UNSET,
    ArraySelectableChildHaver,
    unique_close, is_integer,
    DictlikeFromKeysAndGetitem,
)
from ..defaults import DEFAULTS


### --------------------- Snap & SnapList --------------------- ###

class Snap(DimensionValue):
    '''snap... the label (str) and index (int) of a snapshot.

    The "index" should only be meaningful in the context of a SnapList.
    The "label" should be the str name for this snapshot
        - unique within context (e.g. there's only one "snapshot 1" in a simulation)
        - easiest to use str int labels (e.g. "snapshot 1" --> label="1")

    s: the label (str) of the snapshot. if None, cannot convert to str.
    i: the "index" (int) of the snapshot (within a SnapList). if None, cannot convert to int.
    t: time at this snapshot ['raw' units]
    '''
    # attrs "defining" this DimensionValue, & which can be provided as kwargs in __init__
    _kw_def = {'s', 'i', 't'}

    def __init__(self, s=None, i=None, *, t=None):
        super().__init__(s, i)
        self.t = t

    def copy_add_t(self, t_add):
        '''create a copy of self but with t increased by t_add.
        Equivalent to self.copy(t=self.t + t_add).
        Provided separately for convenience; shifting t can be quite useful.
        '''
        return self.copy(t=self.t + t_add)

    def __repr__(self):
        contents = [repr(val) for val in [self.s, self.i] if val is not None]
        if self.t is not None:
            contents.append(f't={self.t:.3e}')
        return f'{type(self).__name__}({", ".join(contents)})'

    @classmethod
    def from_dict(self, d, *, ignore_dt=True):
        '''return cls from dict d. d should NOT have 'typename' key.
        Use cls.deserialize(d) instead if d has 'typname' key.

        ignore_dt: bool
            whether to ignore 'dt' key from d.
            This exists for backwards compatibility when reading older files;
            Snap previously accepted 'dt' key but doesn't anymore.
        '''
        d_use = {**d}
        if ignore_dt:
            d_use.pop('dt', None)
        return super().from_dict(d_use)

    def file_snap(self, calculator):
        '''returns the snap used when determining file related to this snap.
        Here, just returns self. Subclasses might override.
        '''
        return self

    def file_s(self, calculator):
        '''returns the str used when determining file related to this snap.
        Here, just return str(self). subclass should override if desired.
        '''
        return str(self)

    def file_path(self, calculator):
        '''returns the abspath to the file associated with this snap for this calculator.
        Here, just return calculator.snap_filepath(self).
        '''
        return calculator.snap_filepath(self)

    def exists_for(self, calculator):
        '''returns whether this snap exists for this calculator.
        Here, just return self is not MISSING_SNAP. subclass should override if desired.
        '''
        return self is not MISSING_SNAP


class SnapList(DimensionValueList,
               ArraySelectableChildHaver, array_selectable_child='t'):
    '''list of snaps'''
    _dimension_key_error = SnapKeyError
    value_type = Snap

    @classmethod
    def from_lists(cls, s, *, t=None):
        '''return SnapList from zipping these lists. (i will be determined automatically.)'''
        try:
            iter(t)
        except TypeError:
            t = [t] * len(s)
        return cls.from_dicts([dict(s=s_, t=t_) for s_, t_, in zip(s, t)])

    @classmethod
    def from_array(cls, array):
        '''return SnapList from 0D or 1D array.
        array values should be Snap objects, strings, or ints.
            Snap objects --> use as-is
            strings --> use Snap(s, i=i) for i in range(len(array))
            ints --> use Snap(i=i) for i in array
        if array is a DataArray with 't' coord and any value is not a Snap,
            use the corresponding t value when creating the Snap objects.
        '''
        # [TODO] use super() instead of repeating code from DimensionValueList.from_array?
        if array.ndim == 0:
            values = [array.item()]
        elif array.ndim == 1:
            values = array.values
        else:
            errmsg = f'{cls.__name__}.from_array expects array.ndim=0 or 1; got ndim={array.ndim}'
            raise DimensionalityError(errmsg)
        t_size_matches = False
        if 't' in array.coords:
            tt = array.coords['t']
            if tt.size == len(values):
                t_size_matches = True
        result = []
        for i, v in enumerate(values):
            if isinstance(v, cls.value_type):
                result.append(v)
            elif isinstance(v, str):
                kw_t = dict(t=tt[i]) if t_size_matches else dict()
                result.append(cls.value_type(v, i=i, **kw_t))
            elif is_integer(v):
                kw_t = dict(t=tt[i]) if t_size_matches else dict()
                result.append(cls.value_type(i=v, **kw_t))
            else:
                errmsg = (f'{cls.__name__}.from_array got unexpected value type at index {i}.\n'
                            f'Expected {cls.value_type.__name__}, str, or int; got value={v!r}.')
                raise InputError(errmsg)
        return cls(result)

    t = elementwise_property('t', as_array=True)

    def copy_add_t(self, t_add):
        '''create a copy of self but with t values for all snaps increased by t_add'''
        new_snaps = [snap.copy_add_t(t_add) for snap in self]
        return type(self)(new_snaps)

    def file_s(self, calculator):
        '''return array of file_s for each snap in self, for this calculator.
        Here, just returns array of [snap.file_s(calculator) for snap in self].
        '''
        return np.array([snap.file_s(calculator) for snap in self])

    def file_snap(self, calculator):
        '''return array of file_snap for each snap in self, for this calculator.
        Here, just returns array of [snap.file_snap(calculator) for snap in self])'''
        return np.array([snap.file_snap(calculator) for snap in self])

    def file_path(self, calculator):
        '''returns array of file_path for each snap in self, for this calculator.
        Here, just returns array of [snap.file_path(calculator) for snap in self].
        '''
        return np.array([snap.file_path(calculator) for snap in self])

    def exists_for(self, calculator):
        '''return array of snap.exists_for(calculator) for each snap in self.'''
        return np.array([snap.exists_for(calculator) for snap in self])

    def existing_snaps(self, calculator):
        '''return list like self but skipping any snaps where snap.file_snap(calculator) is MISSING_SNAP.
        The length of this result might be different from the length of self.
        '''
        exists = self.exists_for(calculator)
        keepsnaps = [s for s, exist in zip(self, exists) if exist]
        return type(self)(keepsnaps)


class UniqueSnap(UniqueDimensionValue, Snap):
    '''unique snap; Sentinel value with Snap type.'''
    def copy_add_t(self, _t_add):
        '''return self, unchanged; self is a Sentinel so there is only 1 instance.'''
        return self


INPUT_SNAP = UniqueSnap('INPUT_SNAP')
MISSING_SNAP = UniqueSnap('MISSING_SNAP')


class SnapSelectorValueSpecifier(DimensionSpecialValueSpecifier):
    '''class to specify SnapDimension values based on a selector.
    E.g. snaps.get(SELECT_BETWEEN(0.1, 0.5)) <-- equivalent --> snaps.select_betwee(0.1, 0.5).
    E.g. (snap_dim.v = SELECT_AFTER(3.7)) <--> (snap_dim.v = snap_dim.values.select_after(3.7))
    
    getter: str
        self specifies to use the value(s): snaps.{getter}(*args_getter, **kw_getter).
        Internally stored at self.init_getter.
    name: str
        name of this object; will only be used in repr.
    args_getter: None or iterable
        args to pass to snap_dim.values.getter
    kw_getter: None or dict-like
        kwargs to pass to snap_dim.values.getter
    '''
    def __init__(self, getter, name=None, *, args_getter=None, kw_getter=None):
        self.init_getter = getter
        self.name = name
        self.args_getter = args_getter
        self.kw_getter = kw_getter

    def _new(self, **kw_init):
        '''make a new SnapSelectorValueSpecifier like self, with same init_getter and maybe same name.'''
        result = type(self)(self.init_getter, **kw_init)
        if result.name is None: result.name = self.name
        return result

    def __repr__(self):
        if self.name is None:
            return f'{type(self).__name__}({self._getter_as_str})'
        else:
            return self.name

    def __call__(self, *args_getter, **kw_getter):
        '''returns a new SnapSelectorValueSetter with updated args and kwargs.'''
        return self._new(args_getter=args_getter, kw_getter=kw_getter)

    def getter(self, dlist):
        '''returns dlist.{getter}(args_getter, kw_getter).
        if self.args_getter or self.kw_getter not provided, crash with InputError.
        '''
        if self.args_getter is None or self.kw_getter is None:
            typestr = type(self).__name__
            errmsg = f"{typestr} requires args_getter or kw_getter to be provided."
            if self.name is not None:
                errmsg += (f"\nMaybe forgot to call {typestr} instance?"
                           f"\nE.g. instead of using {self.name}, use {self.name}(...)")
            raise InputError(errmsg)
        values_getter = getattr(dlist, self.init_getter)
        return values_getter(*self.args_getter, **self.kw_getter)

SELECT_CLOSEST = SnapSelectorValueSpecifier('select_closest', 'SELECT_CLOSEST')
SELECT_BEFORE = SnapSelectorValueSpecifier('select_before', 'SELECT_BEFORE')
SELECT_AFTER = SnapSelectorValueSpecifier('select_after', 'SELECT_AFTER')
SELECT_ALL_BEFORE = SnapSelectorValueSpecifier('select_all_before', 'SELECT_ALL_BEFORE')
SELECT_ALL_AFTER = SnapSelectorValueSpecifier('select_all_after', 'SELECT_ALL_AFTER')
SELECT_BETWEEN = SnapSelectorValueSpecifier('select_between', 'SELECT_BETWEEN')


### --------------------- SnapDimension, SnapHaver --------------------- ###

@format_docstring(dimdoc=Dimension.__doc__)
class SnapDimension(Dimension, name='snap', plural='snaps',
                    value_error_type=SnapValueError, key_error_type=SnapKeyError):
    '''snap dimension, representing current value AND list of all possible values.
    Also has various helpful methods for working with this Dimension.

    here, defines custom assign_coord & assign_coord_along,
    because snap is associated with 't' coord.

    u: None or UnitsManager
        used by assign_coord to determine units for t coord.
        if None, will not assign t coord.

    See help(Dimension) for more details.

    --- Dimension.__doc__ copied below: ---
    {dimdoc}
    '''
    NAN = np.nan  # value to use for data when snap is MISSING_SNAP

    def __init__(self, *, u=None, **kw_super):
        super().__init__(**kw_super)
        self.u = u

    def assign_coord(self, array, value=NO_VALUE, **kw_xarray_assign):
        '''returns array.assign_coords(...), assigning 'snap' AND 't' coords.

        value: NO_VALUE, int, str, or Snap
            if not NO_VALUE, assign snap coord as if self.snap = value.
            (set self.snap=value, assign_snap_coord, then restore original self.snap)

        requires not self.snap_is_iterable(), else raises SnapValueError.

        if self.snap.t does not exist,
            raise SnapValueError if DEFAULTS.DEBUG, else do not assign 't' coord.
            if 't' coord is unexpectedly not being assigned, investigate via DEFAULTS.DEBUG = True.

        Note: 't' represents physical time, while 'snap' includes snap name information.

        units for 't' will be self.u('t', alt='coords') units when this method is called.
            assumes snap.t is in 'raw' units; will use:
            t = snap.t * self.u('t', alt='coords')
        '''
        if value is not NO_VALUE:
            with self.using(v=value):
                return self.assign_coord(array, **kw_xarray_assign)
        if self.is_iterable():
            raise self.dimension_value_error("SnapDimension.assign_coord requires non-iterable self.v")
        # else, actually assign the coord.
        snap = self.v
        t_raw = getattr(snap, 't', None)
        u = getattr(self, 'u', None)
        if u is None or t_raw is None:  # don't assign t coord.
            if DEFAULTS.DEBUG and t_raw is None:
                raise self.dimension_value_error(f"SnapDimension.assign_coord requires snap.t to exist. snap={snap}")
            if DEFAULTS.DEBUG and u is None:
                raise self.dimension_value_error(f"SnapDimension.assign_coord requires self.u to exist. self={self}")
            return xarray_assign(array, coords={'snap': snap}, **kw_xarray_assign)
        # else, t and u are both provided. So, assign t coord t, too.
        t = t_raw * u('t', alt='coords')  # time in [u 'coords' units system]
        return xarray_assign(array, coords={'snap': snap, 't': t}, **kw_xarray_assign)

    def assign_coord_along(self, array, dim, value=NO_VALUE, **kw_assign_coords):
        '''returns array.assign_coords(...), assigning 'snap' AND 't' coords.

        value: NO_VALUE, None, or iterable indicating which snaps to use.
            if not NO_VALUE, assign snap coord as if self.snap = value.
            (set self.snap=value, assign_snap_coord, then restore original self.snap)

        requires self.snap_is_iterable(), else raises SnapValueError.

        if self.snap.t does not exist,
            raise SnapValueError if DEFAULTS.DEBUG, else do not assign 't' coord.
            if 't' coord is unexpectedly not being assigned, investigate via DEFAULTS.DEBUG.

        Note: 't' represents physical time, while 'snap' includes snap name information.

        units for 't' will be self.units when this method is called.
            assumes snap.t is in 'raw' units; will use:
            t = snap.t * self.u('t', self.units, convert_from='raw')
        '''
        # [TODO] encapsulate repeated code from previous method.
        if value is not NO_VALUE:
            with self.using(v=value):
                return self.assign_coord_along(array, dim)
        if not self.is_iterable():
            raise self.dimension_value_error("SnapDimension.assign_coord_along requires iterable self.v")
        # else, actually assign the coord.
        snap = self.v
        u = getattr(self, 'u', None)
        t_raw = getattr(snap, 't', None)
        if t_raw is None:  # maybe snap is an iterable of Snap objects
            t_raw = []
            for s in snap:
                st = getattr(s, 't', None)
                if st is None:
                    t_raw = None
                    break
                t_raw.append(st)
            else:  # didn't break
                t_raw = np.array(t_raw)
        if u is None or t_raw is None:  # don't assign t coord.
            if DEFAULTS.DEBUG and t_raw is None:
                raise self.dimension_value_error(f"SnapDimension.assign_coord requires snap.t to exist. snap={snap}")
            if DEFAULTS.DEBUG and u is None:
                raise self.dimension_value_error(f"SnapDimension.assign_coord requires self.u to exist. self={self}")
            return array.assign_coords({'snap': (dim, snap)}, **kw_assign_coords)
        # else, t and u are both provided. So, assign t coord t, too.
        t = t_raw * u('t')  # time in [self.u units system]
        return array.assign_coords({'snap': (dim, snap), 't': (dim, t)}, **kw_assign_coords)

    def join_along(self, arrays, *, coords=['t'], **kw_super):
        '''return arrays joined along the snap dimension.
        by default, joins 't' coords as well.

        coords: str or list of str
            names of coords to join along with snap.
            default = ['t'] --> join 't' coords as well.
            str --> rule, e.g. 'different' or 'minimal'; see help(xr.concat) for details.
        '''
        if not isinstance(coords, str):
            if len(coords)==1 and coords[0]=='t':
                if not all('t' in array.coords for array in arrays):
                    coords = UNSET
        cdict = dict() if coords is UNSET else dict(coords=coords)
        return super().join_along(arrays, **cdict, **kw_super)

    def n_existing_for(self, calculator):
        '''return number of snaps which exist for this calculator.
        Equivalent to (self.values.exists_for(calculator)).sum()
        '''
        return self.values.exists_for(calculator).sum()

    def current_n_existing_for(self, calculator):
        '''return number of existing snaps, out of all snaps at self.v.
        Equivalent to self.v.exists_for(calculator).
        '''
        # note, self.v might not be a SnapList.
        result = 0
        for snap in self.iter():  # iter through v, not values.
            if snap.exists_for(calculator):
                result += 1
        return result


@SnapDimension.setup_haver
class SnapHaver(DimensionHaver, dimension='snap', dim_plural='snaps'):
    '''class which "has" a SnapDimension. (SnapDimension instance will be at self.snap_dim)
    self.snap stores the current snap (possibly multiple). If None, use self.snaps instead.
    self.snaps stores "all possible snaps" for the SnapHaver.
    Additionally, has various helpful methods for working with the SnapDimension,
        e.g. current_n_snap, iter_snaps, take_snap.
        See SnapDimension.setup_haver for details.

    Also, indexing self will set self.snap, then return self.
        see help(self.__getitem__) for more details.
    '''
    def __init__(self, *, snap=None, snaps=None, **kw):
        super().__init__(**kw)
        if snaps is not None: self.snaps = snaps
        self.snap = snap
        self.snap_dim.u = self.u

    def __getitem__(self, snapi):
        '''sets self.snap, then returns self.
        Examples:
            self[4] --> self.snap = 4
            self[:5] --> self.snap = slice(0, 5)
            self[-1] --> self.snap = -1
            self['2'] --> self.snap = '2'
            self[self.snaps[7]] --> self.snap = self.snaps[7]
            self[[0,4,7,3]] --> self.snap = [0,4,7,3]
        Note this is 'smart' in the same way that setting self.snap is 'smart';
            will attempt self.snaps.get(snapi).
            See help(self.snaps.get) for more details.

        This enables "shorthand" syntax, e.g. self[3]('n') gets 'n' at self.snap=3.
        '''
        self.snap = snapi
        return self

    def __iter__(self):
        '''equivalent to self.iter_snaps()'''
        return self.iter_snaps()

    def __len__(self):
        '''equivalent to len(self.snaps)'''
        return len(self.snaps)

    def n_existing_snaps(self):
        '''returns number of existing snaps. Equivalent to self.snap_dim.n_existing_for(self).'''
        return self.snap_dim.n_existing_for(self)

    def current_n_existing_snaps(self):
        '''returns number of existing snaps, out of all snaps at self.snap.
        Equivalent to self.snap_dim.current_n_existing_for(self).
        '''
        return self.snap_dim.current_n_existing_for(self)

    def existing_snaps(self):
        '''return list of existing snaps. Equivalent to self.snaps.existing_snaps(self).'''
        return self.snaps.existing_snaps(self)

    # # # FILE MANAGEMENT -- SUBCLASS SHOULD IMPLEMENT # # #
    @property
    def snapdir(self):
        '''directory containing the snapshot files. Subclass should implement.'''
        raise NotImplementedError(f'{type(self).__name__}.snapdir property')

    def snap_filepath(self, snap=None):
        '''convert snap to full file path for this snap. Subclass should implement.

        snap: None, str, in, or Snap
            the snapshot to load. if None, use self.snap.
        '''
        raise NotImplementedError(f'{type(self).__name__}.snap_filepath()')


### --------------------- ProxySnap --------------------- ###

_proxy_id_registry = dict()  # {proxy_id: calculator} pairs

class ProxySnap(Snap):
    '''snap which is a proxy for one point in time but possibly different snap indices for different runs.
    proxies: dict or None
        {proxy_id(calculator): snap} pairs indicating the snap for each calculator.
        if None, make an empty dict.
    additional args & kwargs are passed to super().__init__.
    '''
    _dimension_value_error = SnapValueError

    def __init__(self, s=UNSET, i=None, *, proxies=None, **kw_super):
        self.proxies = dict() if proxies is None else proxies
        super().__init__(s=s, i=i, **kw_super)

    @property
    def s(self):
        '''s associated with this ProxySnap. if UNSET, infer from self.proxies.values().
        if all proxies values have the same s, use it. Else, use None.
        '''
        if self._s is UNSET:
            return self._s_from_proxies()
        else:
            return self._s
    @s.setter
    def s(self, value):
        self._s = value
    @s.deleter
    def s(self):
        self._s = UNSET

    def _s_from_proxies(self):
        '''return common s from proxies, if any. Else, return None.'''
        s = None
        for snap in self.proxies.values():
            if s is None:
                s = snap.s
            elif s != snap.s:
                s = None
                break
        return s

    def file_snap(self, calculator):
        '''returns the snap which self.proxies points at for this calculator.
        equivalent to self.proxies[self.proxy_id(calculator)].
        '''
        return self.proxies[self.proxy_id(calculator)]

    def file_s(self, calculator):
        '''returns the str used when determining file related to this snap.
        equivalent to self.proxies[self.proxy_id(calculator)].s
        '''
        snap = self.file_snap(calculator)
        return snap.s

    def exists_for(self, calculator):
        '''returns whether this snap exists for this calculator.
        equivalent to self.proxies[self.proxy_id(calculator)].exists_for(calculator).
        '''
        snap = self.file_snap(calculator)
        return snap.exists_for(calculator)

    @classmethod
    def proxy_id(cls, calculator):
        '''return the unique id used to identify this calculator in a ProxySnap.
        unique id guaranteed to be hashable.
        '''
        try:
            return calculator._proxy_id  # this calculator already has a unique id.
        except AttributeError:
            pass  # handled below
        cls._assign_proxy_id(calculator)  # assign proxy id then return it.
        return calculator._proxy_id

    @classmethod
    def _assign_proxy_id(cls, calculator):
        '''assign unique calculator._proxy_id.'''
        assert not hasattr(calculator, '_proxy_id'), f"calculator already has a _proxy_id: {calculator._proxy_id}"
        pid = cls._get_next_proxy_id()
        calculator._proxy_id = pid
        _proxy_id_registry[pid] = calculator  # id registry is saved outside of cls to avoid circular dependencies.
    
    @classmethod
    def _get_next_proxy_id(cls):
        '''return the next unique proxy_id.'''
        try:
            result = cls._next_proxy_id
        except AttributeError:
            result = 0
        cls._next_proxy_id = result + 1
        return result

    @staticmethod
    def registry():
        '''returns dict of all defined {proxy_id: calculator} pairs.
        (To avoid circular dependencies, this dict is stored outside of the ProxySnap class,
            but can be looked up here when requested.)
        '''
        return _proxy_id_registry

    @classmethod
    def from_calculators(cls, calculators, t, *, mode='isclose', missing_ok=False, **kw_init):
        '''return ProxySnap with proxies for each calculator at time t.
        t: number
            time, same units as snaps from calculators.
        mode: 'isclose' or 'exact'
            how to determine which snap to use, if any.
            'isclose' --> np.isclose(snap.t, t). 'exact' --> snap.t == t.
        missing_ok: bool
            if any snap matches are not found, tells whether to raise error or use MISSING_SNAP.
            True --> raise SnapValueError. False --> use MISSING_SNAP for any missing snaps.
        '''
        proxies = {}
        force_relative = {'isclose': 'isclose', 'exact': 'equal'}[mode]
        for calculator in calculators:
            snaps = calculator.snaps
            try:
                snap = snaps.select_closest(t, force_relative=force_relative)
            except ValueError:
                if missing_ok:
                    snap = MISSING_SNAP
                else:
                    raise
            # avoid using multiple layers of proxy, if unnecessary.
            if isinstance(snap, ProxySnap) and cls.proxy_id(calculator) in snap.proxies:
                snap = snap.proxies[cls.proxy_id(calculator)]
            # set proxy for this calculator:
            proxies[cls.proxy_id(calculator)] = snap
        return cls(proxies=proxies, t=t, **kw_init)


class ProxySnapList(SnapList):
    '''list of ProxySnaps'''
    value_type = ProxySnap

    @classmethod
    def from_calculators(cls, calculators, *, mode='isclose', join='inner', **kw_init):
        '''return ProxySnapList of all snaps relevant when considering all calculators.
        In case of different snap lists, behavior is determined by kwargs.

        mode: 'isclose' or 'exact'
            how to determine snap matching.
            'isclose' --> np.isclose(snap.t, t). 'exact' --> snap.t == t.
        join: 'inner' or 'outer'. [TODO] implement other join options?
            how to determine which snaps to keep.
            'inner' --> keep only snaps with matching t.
            'outer' --> keep all snaps (use MISSING_SNAP as needed to fill gaps).
        '''
        if len(calculators)==0:
            return cls()
        if join == 'inner':
            # start with the shortest list of snaps; attempt to get ProxySnap for each t.
            snap_lists = [calculator.snaps for calculator in calculators]
            snaps = min(snap_lists, key=len)
            times = snaps.t
            result = []
            i = 0
            for t in times:
                try:
                    proxy = ProxySnap.from_calculators(calculators, t, mode=mode, i=i)
                except ValueError:  # snap match is missing from one of the calculators.
                    continue
                else:
                    result.append(proxy)
                    i += 1
        elif join == 'outer':
            # get list of all times from all calculators. Use MISSING_SNAP where necessary.
            times = np.unique(np.concatenate([calculator.snaps.t for calculator in calculators]))
            # account for "close" values up to floating point errors (except for at 0. Use atol=0.)
            times = unique_close(times, atol=0)
            times = np.sort(times)
            result = []
            for i, t in enumerate(times):
                proxy = ProxySnap.from_calculators(calculators, t, mode=mode, i=i, missing_ok=True)
                result.append(proxy)
        else:
            raise ValueError(f"join={join!r} not supported.")
        return cls(result, **kw_init)

    def set_in_calculators(self, calculators, *, reset_current_snap=True):
        '''sets calculator.snaps = self for each calculator in calculators.
        Note this sets snaps, not snap. So, the list of "all possible values" is changed.

        reset_current_snap: bool
            whether to set c.snap = 0 or None, for c in calculators.
            if False, c.snap will remain unchanged.
            Default to using None, but if c.snap == 0, use 0 instead.
        '''
        for c in calculators:
            c.snaps = self
            if reset_current_snap:
                if c.snap == 0:
                    c.snap = 0  # set it to the NEW 0 (from self), not the old 0 (from old snaps)
                else:
                    c.snap = None  # equivalent to c.snap = c.snaps


### --------------------- ParamsSnap --------------------- ###

class ParamsSnap(DictlikeFromKeysAndGetitem, Snap):
    '''single snapshot with associated parameters, saved in self.params;
    self also behaves like a dict with params keys & values.
    (Useful if each snapshot has a possibly-different set of parameters.)

    s: the label (str) of the snapshot. if None, cannot convert to str.
    i: the "index" (int) of the snapshot (within a SnapList). if None, cannot convert to int.
    t: time at this snapshot ['raw' units]
    params: dict of parameters at this snapshot. if None, make empty dict.

    The "index" should only be meaningful in the context of a SnapList
    The "label" should be the str name for this snapshot
        - unique within context (e.g. there's only one "snapshot 1" in a simulation)
        - easiest to use str int labels (e.g. "snapshot 1" --> label="1")
    '''
    def __init__(self, s=None, i=None, *, t=None, params=None):
        params = dict() if params is None else params
        super().__init__(s=s, i=i, t=t)
        self.params = params

    # # # GETTING VALUES / ITERATING # # #
    def __getitem__(self, key):
        '''equivalent to self.params[key]'''
        return self.params[key]

    def keys(self):
        '''return tuple of keys of self.params'''
        return tuple(self.params.keys())


class ParamsSnapList(SnapList):
    '''list of ParamsSnap objects. Also provides helpful methods:

    keys(): list of keys appearing in any snap
    params(): dict of {key: [list of values of key from all snaps])
    params_global(): dict of {key: value} for all keys which have the same value in all snaps.
    params_varied(): dict of {key: [list of values of key from all snaps]),
                        for all keys in keys() but not in params_global().
    iter_param_values(key): iterating across all values of key from all snaps,
                        but only yield value once if key is in params_global().
    '''
    value_type = ParamsSnap

    # # # GETTING KEYS & PARAMS # # #
    def keys(self, *, missing_ok=True, recalc=False):
        '''return list of all keys from snaps. Maintains order in which keys appear.

        missing_ok: bool or None
            whether it is okay for snaps to have different keys.
            False --> not okay. If any snap has any different keys, raise FileContentsConflictError.
            True --> okay. If any snap has different keys, add to list of keys.
        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc:
            if hasattr(self, '_keys_same'):  # result of self.keys(missing_ok=False)
                # if this result exists, then missing_ok doesn't matter either way;
                # because it didn't crash we know all the snaps have the same keys.
                return self._keys_same
            elif missing_ok and hasattr(self, '_keys_join'):  # result of self.keys(missing_ok=True)
                return self._keys_join
        # computing result
        result = []
        if len(self) == 0:
            return result
        result = list(self[0].keys())
        result_set = set(result)
        for snap in self[1:]:
            if missing_ok:
                for key in snap.keys():
                    if key not in result:
                        result.append(key)
            else:
                # ensure key set here matches key set in result, else crash.
                snap_key_set = set(snap.keys())
                if snap_key_set != result_set:
                    missing_here = result_set - snap_key_set
                    missing_zero = snap_key_set - result_set
                    errmsg = (f'Some snaps have different keys. '
                              f'Keys in this snap but not snap 0: {missing_here}. '
                              f'Keys in snap 0 but not this snap: {missing_zero}. '
                              f'This snap = {snap}')
                    raise FileContentsConflictError(errmsg)
        # caching
        if missing_ok:
            self._keys_join = result
        else:
            self._keys_same = result
        return result

    def params(self, *, missing_ok=True, recalc=False):
        '''return dict of {key: [list of values of key from all snaps])
        
        missing_ok: bool
            whether it is okay for snaps to have different keys.
            False --> not okay. If any snap has any different keys, raise FileContentsConflictError.
            True --> okay. When key is missing from a snap, use NO_VALUE instead.
        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc:
            if hasattr(self, '_params_same'):  # result of self.params(missing_ok=False)
                # if this result exists, then missing_ok doesn't matter either way;
                # because it didn't crash we know all the snaps have the same keys.
                return self._params_same
            elif hasattr(self, '_params_join') and missing_ok:  # result of self.params(missing_ok=True)
                return self._params_join
        # computing result
        keys = self.keys(missing_ok=missing_ok, recalc=recalc)
        result = dict()
        if missing_ok:
            for key in keys:
                result[key] = [snap.get(key, NO_VALUE) for snap in self]
        else:
            for key in keys:
                result[key] = [snap[key] for snap in self]
        # caching
        if missing_ok:
            self._params_join = result
        else:
            self._params_same = result
        return result

    def keys_shared(self, *, recalc=False):
        '''return list of keys which appear in all snaps. Maintains order in which keys appear.

        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc and hasattr(self, '_keys_shared'):
            return self._keys_shared
        # computing result
        result = []
        if len(self) == 0:
            return result
        result = list(self[0].keys())
        result_set = set(result)
        for snap in self[1:]:
            snap_key_set = set(snap.keys())
            extras_here = result_set - snap_key_set
            for extra in extras_here:
                result.remove(extra)
                result_set.remove(extra)
        # caching
        self._keys_shared = result
        return result

    def params_global(self, *, recalc=False):
        '''return dict of {key: value} for all keys which have the same value in all snaps.

        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc and hasattr(self, '_params_global'):
            return self._params_global
        # computing result
        if len(self) == 0:
            return dict()
        elif len(self) == 1:
            return self[0].params.copy()
        # else len(self) > 1
        keys = self.keys_shared(recalc=recalc)
        keys = list(keys)  # make a copy to avoid directly editing possibly cached result.
        result = {key: self[0][key] for key in keys}
        for snap in self[1:]:
            for key in keys:
                if snap[key] != result[key]:
                    del result[key]
                    keys.remove(key)
        # caching
        self._params_global = result
        return result

    def keys_global(self, *, recalc=False):
        '''return list of keys whose value is the same in all snaps. Maintains order in which keys appear.

        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc and hasattr(self, '_keys_global'):
            return self._keys_global
        # computing result
        keys = self.keys_shared(recalc=recalc)
        keys = list(keys)  # make a copy to avoid directly editing possibly cached result.
        params_global = self.params_global(recalc=recalc)
        keys_shared_set = set(keys)
        keys_global_set = set(params_global.keys())
        keys_remove_set = keys_shared_set - keys_global_set
        for key in keys_remove_set:
            keys.remove(key)
        # caching
        self._keys_global = keys
        return keys

    def keys_varied(self, *, recalc=False):
        '''return list of keys whose value is different in any snap. Maintains order in which keys appear.

        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc and hasattr(self, '_keys_varied'):
            return self._keys_varied
        # computing result
        keys_all = self.keys(missing_ok=True, recalc=recalc)
        keys_global = self.keys_global(recalc=recalc)
        keys_varied = [key for key in keys_all if key not in keys_global]
        # caching
        self._keys_varied = keys_varied
        return keys_varied

    def params_varied(self, *, recalc=False):
        '''return dict of {key: [values from all snaps]) for all params with different values in any snap.
        If any snaps are missing any keys, use NO_VALUE as the value.

        recalc: bool
            whether to, if possible, return cached value (not a copy -- CAUTION: don't edit directly!)
        '''
        # caching
        if not recalc and hasattr(self, '_params_varied'):
            return self._params_varied
        # computing result
        keys = self.keys_varied(recalc=recalc)
        result = dict()
        for key in keys:  # looping like this makes debugging easier than list comprehension.
            result[key] = [snap.get(key, NO_VALUE) for snap in self]
        # caching
        self._params_varied = result
        return result

    def iter_param_values(self, key, default=UNSET):
        '''iterate over all values of this param from all snaps.
        If value is the same in all snaps, just yield it once then stop.
        If value is missing from all snaps, yield default if provided else crash.

        default: UNSET or any object
            for snaps missing key, yield default if provided else crash.
        '''
        params_global = self.params_global()
        if key in params_global:
            yield params_global[key]
        else:  # key not global
            keys = self.keys()
            if key in keys:  # key exists in at least 1 snap
                for snap in self:
                    if key in snap.keys():
                        yield snap[key]
                    elif default is UNSET:
                        raise FileContentsConflictError(f'key {key!r} missing from snap {snap}')
                    else:
                        yield default
            else:  # key not in any snaps
                if default is UNSET:
                    raise FileContentsConflictError(f'key {key!r} missing from all snaps.')
                else:
                    yield default

    def list_param_values(self, key, default=UNSET):
        '''list all values of this param from all snaps.
        If value is the same in all snaps, return [value]
        If value is missing from all snaps, return [default] if provided else crash.

        default: UNSET or any object
            for snaps missing key, use default if provided else crash.
        '''
        return list(self.iter_param_values(key, default=default))