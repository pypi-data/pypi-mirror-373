"""
File Purpose: select part of a list-like object based on values.
E.g. index of "closest" value, list of all values greater than some reference value.
"""
import numpy as np

from .docs_tools import format_docstring
from .iterables import is_iterable
from .oop_tools import Binding
from ..errors import InputError
from ..defaults import DEFAULTS

binding = Binding(locals())

_paramdocs = {
    'force_relative': '''force_relative: None, 'before', 'after', 'equal', or 'isclose'
        whether to also force a certain relationship between result and x:
        result <= x  (if 'before),
        result >= x  (if 'after'),
        result == x  (if 'equal'),
        np.isclose(result, x, atol=0)  (if 'isclose').''',
    }

@format_docstring(**_paramdocs)
def select_i_closest(listlike, x, force_relative=None):
    '''returns the index of the value closest to x. If x iterable, [select_i_closest(y) for y in x]
    raise ValueError if that is impossible (e.g. if force_relative='equal' and no value == x).
    {force_relative}
    '''
    if is_iterable(x):
        return [select_i_closest(listlike, x_, force_relative=force_relative) for x_ in x]
    ibest = None
    distbest = None
    if force_relative not in (None, 'before', 'after', 'equal', 'isclose'):
        errmsg = (f'force_relative={force_relative!r} invalid. '
                  'Expected None, "before", "after", "equal", or "isclose".')
        raise InputError(errmsg)
    if force_relative == 'equal':
        for i, x_ in enumerate(listlike):
            if x_ == x:
                ibest = i
                break
    elif force_relative == 'isclose':
        imatches = np.where(np.isclose(listlike, x, atol=0))[0]
        if len(imatches) == 1:
            ibest = imatches[0]
        elif len(imatches) >= 2:
            raise NotImplementedError(f'force_relative={force_relative!r} when multiple matches found.')
    else:
        for i, x_ in enumerate(listlike):
            dist = x_ - x   # negative if 'before', positive if 'after'
            if (force_relative == 'before' and dist >= 0) or \
               (force_relative == 'after' and dist <= 0):
                continue
            absdist = abs(dist)
            if (distbest is None) or (absdist < distbest):
                distbest = absdist
                ibest = i
    if ibest is None:
        raise ValueError(f'no compatible value found! (x={x}, force_relative={force_relative!r})')
    return ibest

@format_docstring(**_paramdocs)
def select_closest(listlike, x, force_relative=None):
    '''returns the value closest to x.
    If x iterable, [select_closest(y) for y in x]
    {force_relative}
    '''
    if is_iterable(x):
        return [select_closest(listlike, x_, force_relative=force_relative) for x_ in x]
    return listlike[select_i_closest(x, force_relative=force_relative)]

def select_i_before(listlike, x):
    '''returns the index of the value closest to x, but not larger than x.
    If x iterable, [select_i_before(y) for y in x]
    '''
    return select_i_closest(listlike, x, force_relative='before')

def select_before(listlike, x):
    '''returns the value closest to x, but not larger than x.
    If x iterable, [select_before(y) for y in x]
    '''
    return select_closest(listlike, x, force_relative='before')

def select_all_before(listlike, x):
    '''returns listlike, sliced until the value closest to x, but not larger than x.'''
    return listlike[:select_i_before(x)+1]

def select_i_after(listlike, x):
    '''returns the index of the value closest to x, but not smaller than x.
    If x iterable, [select_i_after(y) for y in x]
    '''
    return select_i_closest(listlike, x, force_relative='after')

def select_after(listlike, x):
    '''returns the value closest to x, but not smallerthan x.
    If x iterable, [select_after(y) for y in x]
    '''
    return select_closest(listlike, x, force_relative='after')

def select_all_after(listlike, x):
    '''returns listlike, sliced starting from the value closest to x, but not smaller than x.'''
    return listlike[select_i_after(x):]

def select_i_between(listlike, x1, x2):
    '''returns the list of indices for all values x1 <= value <= x2.'''
    return [i for i, value in enumerate(listlike) if x1 <= value <= x2]

def select_between(listlike, x1, x2):
    '''returns the list of values with x1 <= value <= x2.'''
    ii = select_i_between(x1, x2)
    try:
        return ll[ii]
    except TypeError:  # ll doesn't support fancy indexing
        return [ll[i] for i in ii]


class ArraySelectable():
    '''class which adds select_... methods to a listlike object.'''
    select_i_closest = select_i_closest
    select_closest = select_closest

    select_i_before = select_i_before
    select_before = select_before
    select_all_before = select_all_before

    select_i_after = select_i_after
    select_after = select_after
    select_all_after = select_all_after

    select_i_between = select_i_between
    select_between = select_between


class ArraySelectableChildHaver():
    '''class which provides select_... methods for a child object.

    indicate the attribute name of the child object via 'array_selectable_child' kwarg at subclass creation.
        E.g., class SnapList(..., array_selectable_child='x')
            --> self.select_i_closest(5) will return i such that self.x[i] is closest to 5.

    selections which return values (e.g. select_closest, but not select_i_closest)
        will always return the values from self, not the child.
        E.g. self.select_closest(5) returns self[i] such that self.x[i] is closest to 5.

    Implemented using __init_subclass__ to make pretty docstrings.
    '''
    def __init_subclass__(cls, *, array_selectable_child=None, **kw_super):
        '''called when subclassing ArraySelectableChildHaver; sets cls.select_... methods.
        array_selectable_child: None or str
            attribute name of child object which will be used for select_... methods.
            if None, no select_... methods will be added.

        the select_... methods are:
            select_i_closest, select_closest,
            select_i_before, select_before, select_all_before,
            select_i_after, select_after, select_all_after,
            select_i_between, select_between

        also sets self.array_selectable_child = array_selectable_child, for bookkeeping reasons.
        '''
        super().__init_subclass__(**kw_super)
        if array_selectable_child is None:
            return

        # else, array_selectable_child was provided!
        cls.array_selectable_child = array_selectable_child

        selector = format_docstring(child=array_selectable_child, **_paramdocs, sub_indent=DEFAULTS.TAB*3)

        with binding.to(cls):
            @binding
            @selector
            def select_i_closest(self, x, force_relative=None):
                '''returns the index of the value in self.{child} which is closest to x.
                If x is iterable, [self.select_i_closest(y) for y in x].
                {force_relative}
                '''
                child = getattr(self, self.array_selectable_child)
                return ArraySelectable.select_i_closest(child, x, force_relative=force_relative)

            @binding
            @selector
            def select_closest(self, x, force_relative=None):
                '''returns self[i] such that self.{child}[i] is closest to x.
                If x is iterable, [self.select_closest(y) for y in x].
                    If self supports fancy indexing, will use self[indices],
                    otherwise use type(self)[self[i] for i in indices].
                {force_relative}
                '''
                idx = self.select_i_closest(x, force_relative=force_relative)
                try:
                    return self[idx]
                except TypeError:  # self doesn't support fancy indexing
                    return type(self)(self[i] for i in idx)

            @binding
            @selector
            def select_i_before(self, x):
                '''returns the index of the value in self.{child} closest to x, but not larger than x.
                If x is iterable, [self.select_i_before(y) for y in x].
                '''
                return self.select_i_closest(x, force_relative='before')

            @binding
            @selector
            def select_before(self, x):
                '''returns self[i] such that self.{child}[i] is closest to x, but not larger than x.
                If x is iterable, [self.select_before(y) for y in x].
                    If self supports fancy indexing, will use self[indices],
                    otherwise use type(self)[self[i] for i in indices].
                '''
                return self.select_closest(x, force_relative='before')

            @binding
            @selector
            def select_all_before(self, x):
                '''returns self[:i] such that self.{child}[j] < x, for all j < i.'''
                return self[:self.select_i_before(x)+1]

            @binding
            @selector
            def select_i_after(self, x):
                '''returns the index of the value in self.{child} closest to x, but not smaller than x.
                If x is iterable, [self.select_i_after(y) for y in x].
                '''
                return self.select_i_closest(x, force_relative='after')

            @binding
            @selector
            def select_after(self, x):
                '''returns self[i] such that self.{child}[i] is closest to x, but not smaller than x.
                If x is iterable, [self.select_after(y) for y in x].
                    If self supports fancy indexing, will use self[indices],
                    otherwise use type(self)[self[i] for i in indices].
                '''
                return self.select_closest(x, force_relative='after')

            @binding
            @selector
            def select_all_after(self, x):
                '''returns self[i:] such that self.{child}[j] > x, for all j >= i.'''
                return self[self.select_i_after(x):]

            @binding
            @selector
            def select_i_between(self, x1, x2):
                '''returns the list of indices for all values in self.{child} with x1 <= value <= x2.'''
                child = getattr(self, self.array_selectable_child)
                return ArraySelectable.select_i_between(child, x1, x2)

            @binding
            @selector
            def select_between(self, x1, x2):
                '''returns the list of self[i] such that x1 <= self.{child}[i] <= x2.'''
                ii = self.select_i_between(x1, x2)
                try:
                    return self[ii]
                except TypeError:  # self doesn't support fancy indexing
                    return [self[i] for i in ii]
