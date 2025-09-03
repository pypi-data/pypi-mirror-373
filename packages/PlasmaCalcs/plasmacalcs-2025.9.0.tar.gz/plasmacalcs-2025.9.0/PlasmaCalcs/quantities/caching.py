"""
File Purpose: caching quantities

this is non-trivial because they need to be associated with behavior attrs.
E.g., cached value for 'n' may be associated with 'fluid', 'snap', 'units', ...

additionally, note that set_var may cache a different var than the one entered,
if the entered var has a known_setter.
E.g. for eppic, set_var('n', fluid=1) may cache a value for 'den1' instead of 'n'.

[TODO] detect when behavior is a relevant sublist of dimensions of another behavior,
    e.g. quantity with fluid=1 should be incorporated into getting value with fluid=[0,1,2,3].
    and, quantity with fluid=[0,1,2,3] should be incorporated into getting value with fluid=1.
    The main code can then check relevant_sublist, and if one is available,
        load_across_dims() for the dims with relevant sublists in cache.
"""
import collections

from ..dimensions import BehaviorQuantity
from ..errors import CacheNotApplicableError
from ..tools import (
    simple_property, alias,
    format_docstring,
)
from ..defaults import DEFAULTS


@format_docstring(behavior_doc=BehaviorQuantity.__doc__.replace('BehaviorQuantity', 'CachedQuantity'))
class CachedQuantity(BehaviorQuantity):
    '''{behavior_doc}
    time: number, default 0
        amount of time it took to load this quantity originally.
        Not required for any caching behavior, but helpful for knowing if cache is useful.
    '''
    def __init__(self, value, behavior, *, MB=None, ukey=None, time=0, **kw__behavior_quantity):
        super().__init__(value, behavior, ukey=ukey, **kw__behavior_quantity)
        self.time = time
        self.n_used = 0  # counts number of times this value was loaded from cache.
                         # not updated by this class, but see e.g. VarCache.

    def _new_with_dims(self, dims, **kw_init):
        '''return new CachedQuantity like self but with dims instead of self.behavior.dims.'''
        kw_init.setdefault('time', self.time)
        return super()._new_with_dims(dims, **kw_init)

    def _repr_contents(self):
        contents = super()._repr_contents()
        if self.time is not None:
            contents.append(f'time={self.time:.2e}')
        return contents


class VarCache():
    '''cache of vars. {var: {id: CachedQuantity}.
    id is quant.id for CachedQuantity quant;
        it helps when determining which cached quantity to pop, if cache size is limited.

    Use self.append_cq(var, CachedQuantity) to add a CachedQuantity to this cache.
    Use self.append(var, value, behavior) to create a CachedQuantity and add it to this cache.

    Tracks self.order_entered (updated only when entering a new var),
        and self.order_used (updated when entering OR loading a var).
        Each of these is an OrderedDict with keys (var, qid) tuples; values None.
        The 'latest' entry is at the end.

    MBmax: None or number
        maximum size in MB of this cache. None --> no maximum.
        if provided along with nmax, the more restrictive one will be used.
    nmax: None or number
        maximum number of entries in this cache. None --> no maximum.
        if provided along with MBmax, the more restrictive one will be used.
    remove_strategy: 'used' or 'entered'
        whether to remove the oldest entries based on order_used or order_entered.
        Only applies when cache size exceeds max (determined by MBmax and nmax).
    '''
    def __init__(self, *, MBmax=None, nmax=None, remove_strategy='used'):
        self.cache = dict()
        self.MBmax = MBmax
        self.nmax = nmax
        self.remove_strategy = remove_strategy
        self.order_entered = collections.OrderedDict()
        self.order_used = collections.OrderedDict()
        super().__init__()

    # # # DICT-LIKE BEHAVIOR IN CACHE # # #
    def keys(self):
        '''return keys of self.cache.'''
        return self.cache.keys()

    def values(self):
        '''return values of self.cache.'''
        return self.cache.values()

    def items(self):
        '''return items of self.cache.'''
        return self.cache.items()

    def __getitem__(self, key):
        '''return self.cache[key].'''
        return self.cache[key]

    def __iter__(self):
        '''iterate over self.cache.'''
        return iter(self.cache)

    def __contains__(self, var):
        '''return whether at least one cached value for var exists in cache.'''
        return var in self.cache

    def __len__(self):
        '''return len of cache. This is the number of vars each with at least 1 cached value.'''
        return len(self.cache)

    def clear(self):
        '''empties the cache of all cached values.'''
        while len(self) > 0:
            self.pop()

    # # # ITERATION # # #
    def iter_quantities(self):
        '''iterate over all quantities in this cache.'''
        for qdict in self.values():
            for quant in qdict.values():
                yield quant

    # # # ADDING / REMOVING QUANTITIES # # #
    def append_cq(self, var, cached_quantity):
        '''add cached_quantity to this cache.
        if self.nmax or self.MBmax is provided, remove entries until size is below max.
        if cached_quantity is compatible with any existing cached quantity for var,
            delete the pre-existing one(s) before adding the new one.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self._remove_entries_if_too_large(cached_quantity)
        varcache = self.cache.setdefault(var, {})
        if len(varcache) > 0:  # first, remove any compatible values already in varcache.
            for qid, quant in tuple(varcache.items()):
                if quant.matches_behavior(cached_quantity.behavior):
                    self.pop((var, qid), _clear_empty_var=False)
        varcache[cached_quantity.id] = cached_quantity
        self.order_entered[(var, cached_quantity.id)] = None
        self.order_used[(var, cached_quantity.id)] = None
        return cached_quantity

    def append(self, var, value, behavior, ukey=None, **kw):
        '''create CachedQuantity(value, behavior, ukey=ukey, **kw), and append it to this cache.
        var: str
        value: any
        behavior: dict or Behavior
            (if dict, internally convert to Behavior.)
        ukey: None or str
            if provided, pop 'units' from behavior, and ukey is the string to use
                for getting the conversion factor for value to another units system.
            See help(self) for details.
        '''
        return self.append_cq(var, CachedQuantity(value, behavior, ukey=ukey, **kw))

    @property
    def size(self):
        '''number of entries in this cache.'''
        return sum(len(d) for d in self.values())

    @property
    def size_MB(self):
        '''total size of this cache, in MB.'''
        # [TODO][EFF] keep a running total instead of recalculating.
        #   (probably not worthwhile to implement though; probably won't save much time.)
        return sum(quant.MB for quant in self.iter_quantities())

    MB = alias('size_MB')

    def _remove_entries_if_too_large(self, new_cached_quantity=None):
        '''remove entries from this cache until size WILL be below max AFTER adding new_cached_quantity.
        This method doesn't add new_cached_quantity, but pretends it will be added.
        if new_cached_quantity is None, clean up this cache without adding anything.

        returns (total number of entries removed due to nmax, number removed due to MBmax).
            Note - always attempts removals due to nmax first.
        '''
        nmax_remove = self._remove_entries_if_too_large_nmax(new_cached_quantity)
        MBmax_remove = self._remove_entries_if_too_large_MBmax(new_cached_quantity)
        return nmax_remove, MBmax_remove

    def _remove_entries_if_too_large_nmax(self, new_cached_quantity=None):
        '''remove entries from this cache until size is below nmax.
        if self.nmax is not provided, do nothing.
        if new_cached_quantity is provided, treat self.size as if it is 1 bigger.
        returns total number of entries removed.
        '''
        nmax = self.nmax
        if nmax is None:
            return
        account_for_new = 0 if new_cached_quantity is None else 1
        counter = 0
        while (self.size + account_for_new) > nmax:
            self.pop()
            counter += 1
        return counter

    def _remove_entries_if_too_large_MBmax(self, new_cached_quantity=None):
        '''remove entries from this cache until size is below MBmax.
        if self.MBmax is not provided, do nothing.
        if new_cached_quantity is provided, treat self.size_MB as if it is new_cached_quantity.MB bigger.
        returns total number of entries removed.
        '''
        MBmax = self.MBmax
        if MBmax is None:
            return
        account_for_new = 0 if new_cached_quantity is None else new_cached_quantity.MB
        counter = 0
        while (self.size_MB + account_for_new) > MBmax:
            self.pop()
            counter += 1
        return counter

    def pop(self, itemkey=None, *, strategy=None, _clear_empty_var=True):
        '''remove and return an entry from this cache.
        When called with no arguments, e.g. self.pop(), removes the oldest entry.

        itemkey: None or (var, cached_quantity.id) tuple
            if provided, pop THIS entry from the cache. (self.cache[var][cached_quantity.id])
            else, pop oldest entry.
        strategy: None, 'used', or 'entered'
            determines meaning of 'oldest'. If None, use self.remove_strategy.
        _clear_empty_var: bool
            whether to delete self.cache[var] if it becomes empty due to popping this item.
        '''
        if itemkey is None:
            itemkey = self._get_oldest_itemkey(strategy=strategy)
        # actually remove the item
        del self.order_used[itemkey]
        del self.order_entered[itemkey]
        var, qid = itemkey
        cached_quantity = self.cache[var].pop(qid)
        if _clear_empty_var and len(self.cache[var]) == 0:
            del self.cache[var]
        return cached_quantity

    def pop_used(self):
        '''remove and return the oldest entry from this cache, based on self.order_used.'''
        self.pop(strategy='used')

    def pop_entered(self):
        '''remove and return the oldest entry from this cache, based on self.order_entered.'''
        self.pop(strategy='entered')

    def _get_oldest_itemkey(self, strategy=None):
        '''return (var, cached_quantity.id) for the oldest item in this cache.
        strategy: None, 'used', or 'entered'
            determines meaning of 'oldest'. If None, use self.remove_strategy.
        '''
        if strategy is None: strategy = self.remove_strategy
        if strategy == 'used':
            ordering = self.order_used
        elif strategy == 'entered':
            ordering = self.order_entered
        else:
            raise ValueError(f'invalid remove_strategy {strategy!r}.')
        return next(iter(ordering))

    def mark_used(self, var, quant):
        '''mark (var, quant) as having just been used.
        This affects bookkeeping, as well as pop order for strategy='used', if cache gets too large.
        '''
        self.order_used.move_to_end((var, quant.id))
        quant.n_used += 1
        self.n_used += 1
        self.time_saved += quant.time

    def remove(self, var, behavior, *, missing_ok=False, **kw):
        '''remove all quantities for which behavior.compatible(quantity.behavior, lenient=True), for var.
        i.e., quantities where behavior[k]==quantity[k] for all k in [*behavior.keys(), *behavior.dims.keys()].

        missing_ok: bool
            if not missing_ok, raise CacheNotApplicableError if there are no relevant quantities.
        additional kwargs are passed to behavior.compatible(..., **kw). E.g. could use lenient=False instead.
        returns list of all removed quantities.
        '''
        kw.setdefault('lenient', True)
        kw.setdefault('subdims', True)
        quants_to_remove = self.inverse_lookup(var, behavior, **kw)
        if (not missing_ok) and (len(quants_to_remove) == 0):
            errmsg = f'no cached quantity with behavior.compatible(quantity.behavior), for var {var!r}.'
            raise CacheNotApplicableError(errmsg)
        result = []
        for quant in quants_to_remove:
            popped = self.pop((var, quant.id))
            result.append(popped)
        return result

    # # # TIMING STATS (to learn how useful the cache is being) # # #
    time_saved = simple_property('_time_saved', setdefault=lambda: 0,
                    doc='''total time saved by using this cache, in seconds.''')

    n_used = simple_property('_n_used', setdefault=lambda: 0,
                    doc='''total number of times a value was loaded from this cache.''')

    @property
    def time_saved_here(self):
        '''total time saved by quantities which are currently in the cache.'''
        return sum(quant.time * quant.n_used for quant in self.iter_quantities())

    @property
    def n_used_here(self):
        '''total number of times loaded quantities currently in the cache.'''
        return sum(quant.n_used for quant in self.iter_quantities())

    def timing(self):
        '''return dict of timing stats.'''
        return dict(time_saved=self.time_saved, n_used=self.n_used,
                    time_saved_here=self.time_saved_here, n_used_here=self.n_used_here)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = []
        contents.append(f'size={self.size}')
        if self.nmax is not None:
            contents.append(f'nmax={self.nmax}')
        contents.append(f'MB={self.MB:.2e}')
        if self.MBmax is not None:
            contents.append(f'MBmax={self.MBmax}')
        contents.append(f'keys={list(self.keys())}')
        contents_str = ', '.join(contents)
        return f"{type(self).__name__}({contents_str})"

    # # # RETRIEVING QUANTITIES # # #
    def lookup(self, var, behavior):
        '''returns (relevance, quant) for cached quantity for var, with quantity.relevant(behavior).
        returns (False, None) if no quantity.relevant(behavior).
        else, returns (True, quant) if exact match, or (subdims, quant) if subdim match.
        
        subdim match occurs when dim from cached quantity is a value within dim from behavior
            e.g. fluid=0 in cached quantity, fluid=[0,1,2] in behavior.
        '''
        try:
            qdict = self.cache[var]
        except KeyError:
            return (False, None)
        for quant in qdict.values():
            relevance = quant.relevant(behavior)
            if relevance:
                return (relevance, quant)
        return (False, None)

    def inverse_lookup(self, var, behavior, *, lenient=True, subdims=True, **kw_compatible):
        '''returns list of quantities from self.cache[var] for which behavior.compatible(quantity.behavior)'''
        result = []
        try:
            qdict = self.cache[var]
        except KeyError:
            return result  # cache[var] does not exist.
        for quant in qdict.values():
            if quant.compatible(behavior, lenient=lenient, subdims=subdims, **kw_compatible):
                result.append(quant)
        return result

    def get(self, var, behavior):
        '''return cached value from CachedQuantity with matching behavior, if possible,
        else raise CacheNotApplicableError.

        behavior is matching if CachedQuantity.matches_behavior(behavior),
            i.e. if CachedQuantity.behavior.compatible(behavior, lenient=True).
        '''
        try:
            qdict = self.cache[var]
        except KeyError:
            raise CacheNotApplicableError(f'var {var!r} not in cache.')
        for quant in qdict.values():
            if quant.matches_behavior(behavior):
                # found relevant quant! do some bookkeeping, then return it.
                self.mark_used(var, quant)
                return quant.value
        errmsg = f'no quantity matching behavior, for var {var!r} in cache.'
        raise CacheNotApplicableError(errmsg)


@format_docstring(varcache_doc=VarCache.__doc__)
class VarCacheSingles(VarCache):
    '''cache of vars, where each cached quantity represents a single point (in dimension space).
    "single point" refers to having at most one value for each of the dimensions,
        but not maindims. E.g., one snap, fluid, component. Any number of x,y,z.

    When appending a CachedQuantity which is not a single point (in dimension space),
        separate it into multiple quantities, and append each of those instead.

    VarCache documentation:
    -----------------------
    {varcache_doc}
    '''
    def append_cq(self, var, cached_quantity):
        '''add cached_quantity to this cache.
        If cached_quantity is not a single point (in dimension space), first separate, then append each.

        if self.nmax or self.MBmax is provided, remove entries until size is below max.
        if cached_quantity is compatible with any existing cached quantity for var,
            delete the pre-existing one(s) before adding the new one.

        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        quant_at_points = cached_quantity.list_points()
        for quant in quant_at_points:
            super().append_cq(var, quant)
        return quant_at_points