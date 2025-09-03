"""
File Purpose: tools for easily managing attributes
"""

import functools

from ..properties import weakref_property_simple, alias
from ..sentinels import ATTR_UNSET, UNSET
from ...defaults import DEFAULTS


### --------------------- very simple context managers --------------------- ###

class CallInContext():
    '''context manager which calls f with *args and **kw upon entry, and does nothing upon exit.'''
    def __init__(self, f, *args, **kw):
        self.f = f
        self.args = args
        self.kw = kw

    def __enter__(self):
        self.f(*self.args, **self.kw)

    def __exit__(self, exc_type, exc_value, traceback):
        pass


### --------------------- attrs context managers --------------------- ###

# # # HELPERS # # #
def set_or_del_attr(obj, attr, value, unset=ATTR_UNSET, *, unset_fail_ok=True):
    '''usually, setattr(obj, attr, value). However, if `value` is `unset`, delattr(obj, attr) instead.
    (`value` will be compared to `unset` using "is", not "==".)

    unset_fail_ok: bool
        whether to ignore AttributeError when `value` is `unset` but obj.attr is not defined.
    '''
    if value is unset:
        try:
            delattr(obj, attr)
        except AttributeError:
            if not unset_fail_ok:
                raise
    else:
        setattr(obj, attr, value)

# # # SIMPLE CONTEXT MANAGERS & ALIASES # # #
def maintaining_attrs(self, *attrs, **attrs_as_flags):
    '''returns context manager which restores attrs of self to their original values, upon exit.
    E.g. maintaining_attrs(obj, 'attr1', 'attr2', attr3=True, attr4=False)
    --> will restore upon exit, original values of obj.attr1, attr2, and attr3, but not attr4.
    '''
    return MaintainingAttrs(self, *attrs, **attrs_as_flags)

def using_attrs(self, attrs_as_dict=dict(), _unset_sentinel=ATTR_UNSET, **attrs_and_values):
    '''returns context manager which sets attrs of obj upon entry; restores original values upon exit.
    _unset_sentinel: any value, default ATTR_UNSET
        upon entry, delete any attrs with value _unset_sentinel (compared via 'is').
        E.g. using_attrs(obj, _unset_sentinel=None, x=None) --> del obj.x upon entry.
    '''
    return UsingAttrs(self, attrs_as_dict, _unset_sentinel=_unset_sentinel, **attrs_and_values)

def maintain_attrs(*attrs):
    '''return decorator which restores attrs of obj after running function.
    It is assumed that obj is the first arg of function.
    '''
    def attr_restorer(f):
        @functools.wraps(f)
        def f_but_maintain_attrs(obj, *args, **kwargs):
            '''f but attrs are maintained.'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            with MaintainingAttrs(obj, *attrs):
                return f(obj, *args, **kwargs)
        return f_but_maintain_attrs
    return attr_restorer

def use_attrs(attrs_as_dict=dict(), **attrs_and_values):
    '''return decorator which sets attrs of object before running function then restores them after.
    It is assumed that obj is the first arg of function.
    '''
    def attr_setter_then_restorer(f):
        @functools.wraps(f)
        def f_but_set_then_restore_attrs(obj, *args, **kwargs):
            '''f but attrs are set beforehand then restored afterward.'''
            __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
            with UsingAttrs(obj, attrs_as_dict, **attrs_and_values):
                return f(obj, *args, **kwargs)
        return f_but_set_then_restore_attrs
    return attr_setter_then_restorer

class MaintainingAttrs():
    '''context manager which restores attrs of obj to their original values, upon exit.
    This includes deleting any of those attrs upon exit which did not exist upon entry.

    kwargs can be provided with key=bool; attr key will be included if True.
        E.g. MaintainingAttrs(obj, 'attr1', 'attr2', attr3=True, attr4=False)
        --> will maintain obj.attr1, obj.attr2, and obj.attr3, but not obj.attr4.
    '''
    _unset_sentinel = ATTR_UNSET   # the sentinel used to indicate an attribute was not set.

    def __init__(self, obj, *attrs, **attrs_as_flags):
        self.obj = obj
        self.attrs = list(attrs)
        self.attrs.extend(attr for attr, flag in attrs_as_flags.items() if flag)

    def obj_current_attrs(self):
        '''return dict of {attr: obj.attr} for current values of attrs.'''
        return {attr: getattr(self.obj, attr, self._unset_sentinel) for attr in self.attrs}

    def enter_handle_attrs(self):
        '''take all steps related to attrs which should occur upon entry.
        Provided separately from self.__enter__ for access to low-level functionality.
        '''
        self.memory = self.obj_current_attrs()
        self._inside_attrs = True

    def exit_handle_attrs(self):
        '''take all steps related to attrs which should occur upon exit.
        Provided separately from self.__exit__ for access to low-level functionality.
        '''
        if DEFAULTS.DEBUG > 10:
            if len(self.memory)>0: print('   > restoring attrs:', self.memory)
        for attr, val in self.memory.items():
            set_or_del_attr(self.obj, attr, val, unset=self._unset_sentinel)
        self._inside_attrs = False

    def inside_attrs(self):
        '''tells whether currently inside attrs handling for self. None if never entered; False if exited.'''
        return getattr(self, '_inside_attrs', None)

    def __enter__(self):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.enter_handle_attrs()

    def __exit__(self, exc_type, exc_value, traceback):
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        self.exit_handle_attrs()

    # # # DISPLAY # # #
    def __repr__(self):
        contents = f'managing attrs {[attr for attr in self.attrs]}; inside_attrs={self.inside_attrs()}'
        return f'{type(self).__name__}({contents})'


class UsingAttrs(MaintainingAttrs):
    '''context manager which sets attrs of obj upon entry; restores original values upon exit.
    This includes deleting any of those attrs upon exit which did not exist upon entry.

    _unset_sentinel: any value, default ATTR_UNSET
        upon entry, delete any attrs with value _unset_sentinel (compared via 'is').
        E.g. UsingAttrs(obj, _unset_sentinel=None, x=None) --> del obj.x upon entry.
    '''
    def __init__(self, obj, attrs_as_dict=dict(), *, _unset_sentinel=ATTR_UNSET, **attrs_and_values):
        self.obj = obj
        self.attrs = {**attrs_as_dict, **attrs_and_values}
        self._unset_sentinel = _unset_sentinel
        if DEFAULTS.DEBUG > 10:
            if len(self.attrs)>0: print('   < setting attrs:', self.attrs)

    def enter_handle_attrs(self):
        '''take all steps related to attrs which should occur upon entry.
        Provided separately from self.__enter__ for access to low-level functionality.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        super().enter_handle_attrs()
        for attr, val in self.attrs.items():
            set_or_del_attr(self.obj, attr, val, unset=self._unset_sentinel)

    # __enter__ and __exit__ inherited from super().


# # # LESS-SIMPLE CONTEXT MANAGERS # # #
class UsingAttrsSignaled(UsingAttrs):
    '''context manager which (enter) sets attrs of obj; (exit) restores original values; (both) sends signals (e.g. to obj).

    signals are sent at entry and exit, using whichever of the following are provided:
        signal_enter: None or str
            immediately BEFORE setting attrs, obj.signal_enter(current, new) during ENTRY
        signal_exit: None or str
            immediately BEFORE setting attrs, obj.signal_exit(current, new) during EXIT
        signal_context_shift: None or str
            immediately BEFORE setting attrs, obj.signal_context_shift(current, new) during ENTRY and EXIT.

        signal_entered: None or str
            immediately AFTER setting attrs, obj.signal_entered(current, new) during ENTRY
        signal_exited: None or str
            immediately AFTER setting attrs, obj.signal_exited(current, new) during EXIT
        signal_context_shifted: None or str
            immediately AFTER setting attrs, obj.signal_context_shifted(current, new) during ENTRY and EXIT.

        where (current, new) are dicts for the attrs (or a single value if len(self.attrs)==1; see `squeeze`):
            current = dict of {attr: obj.attr} for values before setting attrs.
            new = dict of {attr: obj.attr} for values after setting attrs.

    _unset_sentinel: any value, default ATTR_UNSET
        used to indiate an attribute does not exist.
        values in the dicts passed to signals will be _unset_sentinel if the attribute does not exist.
        upon entry, delete any attrs with value _unset_sentinel (compared via 'is').
        E.g. UsingAttrsSignaled(obj, _unset_sentinel=None, x=None) --> del obj.x upon entry.
    squeeze: bool, default True
        if True, and len(self.attrs)==1, then current and new will be single values, not dicts.
    signal_target: None or object
        if provided, use this object instead of self.obj, for sending signals.

    --- EXAMPLES ---
        # starting with obj.depth==0:
        with UsingAttrsSignaled(obj.depth=1, signal_context_shifted='_on_set_depth'):
            # during entry, obj._on_set_depth(0, 1), immediately after setting obj.depth=1.
            # during exit, obj._on_set_depth(depth_pre_exit, 0), immediately after setting obj.depth=0,
            #   where depth_pre_exit = obj.depth just before exiting.

        # starting with obj.depth==0:
        with UsingAttrsSignaled(obj.depth=1, signal_context_enter='_on_increment_depth', squeeze=False):
            # during entry, obj._on_increment_depth({depth: 0}, {depth: 1}), immediately before setting obj.depth=1.

        # starting with obj.depth==0, obj.x==3
        with UsingAttrsSignaled(obj.depth=1, x=7, signal_context_exit='_on_exit_depth_and_x'):
            # during exit, first obj._on_exit_depth_and_x({depth: obj.depth, x: obj.x}, {depth: 0, x: 3}),
            #   immediately before setting obj.depth=0 and obj.x=3
    '''
    def __init__(self, obj, attrs_as_dict=dict(),
                 signal_enter=None, signal_exit=None, signal_context_shift=None,
                 signal_entered=None, signal_exited=None, signal_context_shifted=None,
                 _unset_sentinel=ATTR_UNSET, squeeze=True, signal_target=None,
                  **attrs_and_values):
        super().__init__(obj, attrs_as_dict, _unset_sentinel=_unset_sentinel, **attrs_and_values)
        self.signal_enter = signal_enter
        self.signal_exit = signal_exit
        self.signal_context_shift = signal_context_shift
        self.signal_entered = signal_entered
        self.signal_exited = signal_exited
        self.signal_context_shifted = signal_context_shifted
        self.squeeze = squeeze
        self.signal_target = signal_target

    def obj_maybe_signal(self, name, current, new):
        '''possibly send signal to obj, based on mode and signal_* attributes.
        name: str, one of ('enter', 'exit', 'context_shift', 'entered', 'exited', 'context_shifted')
        current: dict
            dict of {attr: obj.attr} for values before setting attrs due to shifting context.
        new: dict
            dict of {attr: obj.attr} for values after setting attrs due to shifting context.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        signal = getattr(self, f'signal_{name}')
        if signal is not None:
            target = self.obj if self.signal_target is None else self.signal_target
            current = next(iter(current.values())) if self.squeeze and len(current)==1 else current
            new     = next(iter(new.values()))     if self.squeeze and len(new)==1     else new
            fsignal = getattr(target, signal)
            return fsignal(current, new)

    def __enter__(self):
        current = self.obj_current_attrs()
        new = self.attrs.copy()
        self.obj_maybe_signal('enter', current, new)
        self.obj_maybe_signal('context_shift', current, new)
        super().__enter__()
        self.obj_maybe_signal('entered', current, new)
        self.obj_maybe_signal('context_shifted', current, new)
    
    def __exit__(self, exc_type, exc_value, traceback):
        current = self.obj_current_attrs()
        new = self.memory.copy()
        self.obj_maybe_signal('exit', current, new)
        self.obj_maybe_signal('context_shift', current, new)
        super().__exit__(exc_type, exc_value, traceback)
        self.obj_maybe_signal('exited', current, new)
        self.obj_maybe_signal('context_shifted', current, new)

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return list of contents to go in repr of self.'''
        contents = []
        contents.append(f'attrs.keys()={list(self.attrs.keys())}')
        for key in ('enter', 'exit', 'context_shift', 'entered', 'exited', 'context_shifted'):
            if getattr(self, f'signal_{key}') is not None:
                contents.append(f'signal_{key}={getattr(self, f"signal_{key}")!r}')
        contents.append(f'_unset_sentinel={self._unset_sentinel!r}')
        contents.append(f'squeeze={self.squeeze!r}')
        if self.signal_target is not None:
            contents.append(f'signal_target={self.signal_target!r}')

    def __repr__(self):
        return f'{type(self).__name__}({", ".join(self._repr_contents())})'


### --------------------- other attr management --------------------- ###

class IncrementableAttrManager():
    '''an incrementable attribute, and methods to manage other attributes when it is incremented or decremented.'''
    _unset_sentinel = ATTR_UNSET   # the sentinel used to indicate an attribute was not set.

    def __init__(self, obj, default=0, *, step=1):
        self.obj = obj
        self.default = default
        self.step = step
        if step <= 0:
            raise NotImplementedError(f'nonpositive step, inside IncrementableAttrManager. Got step={step}.')

        self.value = default

        # {value: list of (context, remove_after_decrementing_to) pairs}
        #   use all contexts in list when incrementing or decrementing self.value to value.
        #   when decrementing to remove_after_decrementing_to, remove the context from the list.
        self._using_at = dict()

    obj = weakref_property_simple('_obj')  # behaves like obj but is weakref, to avoid circular references.

    incrementable_attr_manager_value = alias('value')   # useful for more verbose debugging

    def __int__(self):
        '''return int(self.value)'''
        return int(self.value)

    def clear(self):
        '''set self.value to self.default, and empty self._using_at.'''
        self.value = self.default
        self._using_at.clear()

    def increment(self):
        '''context manager which increments self.value upon entry, and restores old value upon exit.
        CAUTION: this is a context manager; it will not increment self.value until entered,
            via "with" statement, e.g. "with self.increment(): ...".
        '''
        old = self.value
        new = old + self.step
        return UsingAttrsSignaled(self,
                  incrementable_attr_manager_value=new,  # equivalent to value=new, but more verbose in debugging.
                  signal_entered='_on_incremented',
                  signal_exited='_on_decremented')

    def use_obj_attrs_at(self, value, *, remove_after_decrementing_to=UNSET, **attrs_and_values):
        '''tell self to set attrs of obj when self.value == value.
        More precisely:
            - when self incremented OR decremented to value,
                UsingAttrs(self.obj, attrs_and_values).enter_handle_attrs()
            - when self incremented beyond value OR decremented beyond value,
                UsingAttrs(...).exit_handle_attrs()

        remove_after_decrementing_to: UNSET, None, or int
            - when self decremented to remove_after_decrementing_to,
                also remove these "use_obj_attrs_at" commands.
            Note: this should always be < value, otherwise will raise ValueError.
            UNSET --> use self.default.
            None --> never remove these commands as a result of decrementing.
            int --> remove these commands as soon as value is decremented to this value.

        Note: to decrease chances of mistakes / ambiguity,
            raise ValueError if value <= self.value, or if value <= remove_after_decrementing_to
            value <= self.value, OR
            value <= remove_after_decrementing_to.

        (This method is only responsible for putting these attrs and values into self._using_at;
            the "real work" happens in self.incremented, _on_incremented, and _on_decremented.)
        '''
        rmv = remove_after_decrementing_to
        rmv = self.default if rmv is UNSET else rmv
        if (value <= self.value): #or ((rmv is not None) and (value < rmv)):
            errmsg = (f'Cannot tell self to use obj attrs at value, when value <= self.value.'
                        f' Got value={value}, self.value={self.value}.')
            raise ValueError(errmsg)
        elif (rmv is not None) and (value <= rmv):
            errmsg = (f'Cannot tell self to use obj attrs at value, when value <= remove_after_decrementing_to.'
                        f' Got value={value}, remove_after_decrementing_to={rmv}.')
            raise ValueError(errmsg)
        context = UsingAttrs(self.obj, attrs_and_values)
        self._using_at.setdefault(value, []).append((context, rmv))

    def _on_incremented(self, prev, new):
        '''called when self.value is incremented, i.e. when entering the 'incremented' context.'''
        for context, _rmv in self._using_at.get(prev, []):
            context.exit_handle_attrs()
        for context, _rmv in self._using_at.get(new, []):
            context.enter_handle_attrs()

    def _on_decremented(self, prev, new):
        '''called when self.value is decremented, i.e. when exiting the 'incremented' context.'''
        for context, _rmv in self._using_at.get(prev, []):
            context.exit_handle_attrs()
        for context, _rmv in self._using_at.get(new, []):
            context.enter_handle_attrs()

        self._remove_commands_after_decrementing_to(new)

    def _remove_commands_after_decrementing_to(self, value):
        '''remove commands from self.using_at after decrementing self to value.
        Removes any (context, rmv) pair for which rmv==value.
        If any of these contexts have not been exited, raise AssertionError.
        '''
        for _value, commands in tuple(self._using_at.items()):
            to_remove = [i for i, (context, rmv) in enumerate(commands) if rmv == value]
            for i in to_remove:  # crash with error message if any to_remove contexts have not been exited.
                context, rmv = commands[i]
                if context.inside_attrs():
                    errmsg = (f'context {context} has not been exited, but is being removed from self._using_at.'
                              '\nCrashing, then clearing self._using_at to avoid further errors.')
                    self._using_at.clear()
                    raise AssertionError(errmsg)
            if len(to_remove) == len(commands):  # remove all commands for this value
                del self._using_at[_value]
            else:  # only remove some commands for this value.
                for i in reversed(to_remove):
                    del commands[i]

    def use_obj_attrs_at_next(self, **attrs_and_values):
        '''tell self to set attrs of obj when self.increment() is next entered.
        Equivalent to self.use_obj_attrs_at(self.value + self.step, **attrs_and_values),
            with remove_after_decrementing_to = self.value.
        '''
        self.use_obj_attrs_at(self.value + self.step, remove_after_decrementing_to=self.value, **attrs_and_values)

    # # # CONTEXT MANAGERS # # #
    def using_obj_attrs_at(self, value, **attrs_and_values):
        '''context manager which tells self to set attrs of obj when self.value == value.
        Equivalent to calling self.use_obj_attrs_at(...) upon entry (and doing nothing upon exit).
        '''
        return CallInContext(self.use_obj_attrs_at, value, **attrs_and_values)

    def using_obj_attrs_at_next(self, **attrs_and_values):
        '''context manager which tells self to set attrs of obj when self.increment() is next entered.
        Equivalent to calling self.use_obj_attrs_at_next(...) upon entry (and doing nothing upon exit).
        '''
        return CallInContext(self.use_obj_attrs_at_next, **attrs_and_values)

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(value={self.value})'

    # # # PICKLING # # #
    def __getstate__(self):
        '''return state for pickling. (pickle can't handle weakrefs. pickling is required by multiprocessing.)'''
        state = self.__dict__.copy()
        # follow weakrefs. state['_obj'] might be a weakref;
        #   self.obj would be the result of following this weakref (see weakref_property_simple).
        state['_obj'] = self.obj
        return state

    def __setstate__(self, state):
        '''set state from pickling. (pickle can't handle weakrefs. pickling is required by multiprocessing.)'''
        self.__dict__.update(state)
        # set up weakrefs. state['_obj'] might be a obj but should be a weakref instead;
        #   setting self.obj = state['_obj'] internally stores the value as a weakref.
        self.obj = state['_obj']