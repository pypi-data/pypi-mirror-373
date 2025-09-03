"""
File Purpose: tools for simple properties
"""
import contextlib
import weakref

import numpy as np
import xarray as xr

from .docs_tools import format_docstring
from .sentinels import NO_VALUE, UNSET
from ..errors import InputError, InputConflictError

### --------------------- Alias an attribute --------------------- ###

def alias(attribute_name, doc=None):
    '''returns a property which is an alias to attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}'.
    '''
    return property(lambda self: getattr(self, attribute_name),
                    lambda self, value: setattr(self, attribute_name, value),
                    doc=f'''alias to {attribute_name}''' if doc is None else doc)

def alias_to_result_of(attribute_name, doc=None):
    '''returns a property which is an alias to the result of calling attribute_name.
    if doc is None, use doc=f'alias to {attribute_name}()'.
    '''
    return property(lambda self: getattr(self, attribute_name)(),
                    doc=f'''alias to {attribute_name}()''' if doc is None else doc)

def alias_child(child_name, attribute_name, doc=None, *, if_no_child=NO_VALUE, if_special_child=UNSET):
    '''returns a property which is an alias to obj.child_name.attribute_name.
    if doc is None, use doc=f'alias to self.{child_name}.{attribute_name}'.
    includes getter AND setter methods.

    if_no_child: NO_VALUE or any object
        if provided (not NO_VALUE), return this instead if child is None or doesn't exist.
    if_special_child: UNSET or dict
        if provided, dict of {special key: value to return if child == special key}
    '''
    if (if_no_child is NO_VALUE) and (if_special_child is UNSET):
        def getter(self):
            return getattr(getattr(self, child_name), attribute_name)
    elif (if_no_child is not NO_VALUE) and (if_special_child is UNSET):
        def getter(self):
            child = getattr(self, child_name, None)
            return if_no_child if child is None else getattr(child, attribute_name)
    elif (if_no_child is NO_VALUE) and (if_special_child is not UNSET):
        def getter(self):
            child = getattr(self, child_name, None)
            if child in if_special_child:
                return if_special_child[child]
            else:
                return getattr(child, attribute_name)
    elif (if_no_child is not NO_VALUE) and (if_special_child is not UNSET):
        def getter(self):
            child = getattr(self, child_name, None)
            if child is None:
                return if_no_child
            elif child in if_special_child:
                return if_special_child[child]
            else:
                return getattr(child, attribute_name)
    def setter(self, value):
        setattr(getattr(self, child_name), attribute_name, value)
    if doc is None:
        doc = f'''alias to self.{child_name}.{attribute_name}'''
    return property(getter, setter, doc=doc)

def alias_key_of(dict_attribute_name, key, *, default=NO_VALUE, setdefault_value=NO_VALUE, doc=None):
    '''returns a property which is an alias to obj.dict_attribute_name[key].
    if doc is None, use doc=f'alias to self.{dict_attribute_name}[{key!r}]'.
    includes getter, setter, and deleter methods.

    if setting value to UNSET, delete the key from the dict instead.

    default: any object
        if provided (not NO_VALUE), then getter returns self.dict_attribute_name.get(key, default).
    setdefault_value: any object
        if provided (not NO_VALUE), then getter returns self.dict_attribute_name.setdefault(key, setdefault_value).
    '''
    if default is not NO_VALUE and setdefault_value is not NO_VALUE:
        raise InputConflictError('cannot provide both default and setdefault_value.')
    if default is not NO_VALUE:
        def getter(self):
            return getattr(self, dict_attribute_name).get(key, default)
    elif setdefault_value is not NO_VALUE:
        def getter(self):
            return getattr(self, dict_attribute_name).setdefault(key, setdefault_value)
    else:
        def getter(self):
            return getattr(self, dict_attribute_name)[key]
    def deleter(self):
        del getattr(self, dict_attribute_name)[key]
    def setter(self, value):
        if value is UNSET:
            deleter(self)
        else:
            getattr(self, dict_attribute_name)[key] = value
    doc = f'''alias to self.{dict_attribute_name}[{key!r}]''' if doc is None else doc
    return property(getter, setter, deleter, doc=doc)

def alias_in(cls, attr, new_attr):
    '''sets cls.new_attr to be an alias for cls.attr.'''
    setattr(cls, new_attr, alias(attr))


### --------------------- Other properties --------------------- ###

def weakref_property_simple(internal_attr, doc=None):
    '''defines a property which behaves like the value it contains, but is actually a weakref.
    stores internally at internal_attr. Also set self.{internal_attr}_is_weakref = True.
    Setting the value actually creates a weakref. Getting the value calls the weakref.
    Note: if failing to create weakref due to TypeError,
        (e.g. "TypeError: cannot create weak reference to 'int' object")
        then just store the value itself. Also set self.{internal_attr}_is_weakref = False.
    '''
    internal_attr_is_weakref = f'{internal_attr}_is_weakref'
    @format_docstring(attr=internal_attr)
    def get_attr(self):
        '''gets self.{attr}(), or just self.{attr} if not self.{attr}_is_weakref.'''
        self_attr = getattr(self, internal_attr)
        if getattr(self, internal_attr_is_weakref):
            return self_attr()
        else:
            return self_attr

    @format_docstring(attr=internal_attr)
    def set_attr(self, val):
        '''sets self.{attr}'''
        try:
            result = weakref.ref(val)
        except TypeError:
            setattr(self, internal_attr_is_weakref, False)
            result = val
        else:
            setattr(self, internal_attr_is_weakref, True)
        setattr(self, internal_attr, result)

    @format_docstring(attr=internal_attr)
    def del_attr(self):
        '''deletes self.{attr}'''
        delattr(self, internal_attr)
    
    return property(get_attr, set_attr, del_attr, doc)

def simple_property(internal_name, *, doc=None,
                    default=NO_VALUE, setdefault=NO_VALUE, setdefaultvia=NO_VALUE,
                    setable=True, delable=True,
                    valid=UNSET, validate_from=UNSET, validate_default=False):
    '''return a property with a setter and getter method for internal_name.

    default: NO_VALUE or any object
        if provided, getter uses this default if this attr has not been set.
    setdefault: NO_VALUE or callable of 0 arguments
        if provided, getter uses setdefault() if this attr has not been set.
        (if internal_name is unset, getter sets self.{internal_name} = setdefault(),
            then returns value at self.{internal_name}. Does not recalculate each time.)
        E.g. setdefault = dict, creates a new dict.
            (using default=dict() would share the dict amongst all instances;
            using setdefault=dict creates a new dict for each instance when needed.)
    setdefaultvia: NO_VALUE or str
        if provided, getter uses self.{setdefaultvia}() if attr has not been set.
        (if internal_name is unset, getter sets self.{internal_name} = self.{setdefaultvia}(),
            then returns value at self.{internal_name}. Does not recalculate each time.)
        E.g. setdefault = '_default_val' --> getter calls & returns self._default_val(),
            and remembers result, saving it to self.{internal_name}.

    setable: bool
        whether to allow this attribute to be set (i.e., define fset.)
    delable: bool
        whether to allow this attribute to be set (i.e., define fdel.)

    valid: UNSET or iterable
        if provided, only allow setting to values in valid.
    validate_from: UNSET or str
        if provided, get list of valid values from getattr(self, validate_from).
    validate_default: bool
        whether to apply validation to the results of setdefault() or setdefaultvia().
        disabled by default, for efficiency.
    '''
    # bookkeeping on inputs
    defaults = dict(default=default, setdefault=setdefault, setdefaultvia=setdefaultvia)
    provided_defaults = {key: val for key, val in defaults.items() if val is not NO_VALUE}
    if len(provided_defaults) > 1:
        raise InputConflictError(f'cannot provide more than 1 default, but got: {provided_defaults}')
    validation = dict(valid=valid, validate_from=validate_from)
    provided_validation = {key: val for key, val in validation.items() if val is not UNSET}
    if len(provided_validation) > 1:
        raise InputConflictError(f'cannot provide more than 1 validation kwarg, but got: {provided_validation}')
    if (not setable) and (provided_validation):
        raise InputConflictError(f'cannot provide validation kwarg if setable=False, but got: {provided_validation}')
    # getter
    if default is NO_VALUE and setdefault is NO_VALUE and setdefaultvia is NO_VALUE:
        def getter(self):
            return getattr(self, internal_name)
    elif default is not NO_VALUE:
        def getter(self):
            return getattr(self, internal_name, default)
    else:  # provided setdefault or setdefaultvia
        def getter(self):
            try:
                return getattr(self, internal_name)
            except AttributeError:
                pass  # handled below, to avoid stacked error message in case setdefault/via fails.
            # get default value:
            if setdefault is not NO_VALUE:
                result = setdefault()
            else:  # provided setdefaultvia
                defaultvia = getattr(self, setdefaultvia)
                result = defaultvia()
            # validate if relevant
            if validate_default and (valid is not UNSET or validate_from is not UNSET):
                allowed = getattr(self, validate_from) if valid is UNSET else valid
                if result not in allowed:
                    raise ValueError(f'setdefault gave {internal_name}={result!r}. Expected one of: {list(allowed)!r}')
            # set & return default value
            setattr(self, internal_name, result)
            return result
    # setter
    if setable:
        if (valid is UNSET and validate_from is UNSET):
            def setter(self, value):
                setattr(self, internal_name, value)
        else:
            def setter(self, value):
                allowed = getattr(self, validate_from) if valid is UNSET else valid
                if value not in allowed:
                    raise InputError(f'{internal_name}={value!r}. Expected one of: {list(allowed)!r}')
                setattr(self, internal_name, value)
    else:
        setter = None
    # deleter
    if delable:
        def deleter(self):
            delattr(self, internal_name)
    else:
        deleter = None
    return property(getter, setter, deleter, doc=doc)

def simple_tuple_property(*internal_names, doc=None, default=NO_VALUE):
    '''return a property which refers to a tuple of internal names.
    if 'default' provided (i.e., not NO_VALUE):
        - getter will have this default, if attr has not been set.
        - setter will do nothing if value is default.
        This applies to each name in internal_names, individually.
    '''
    if default is NO_VALUE:
        def getter(self):
            return tuple(getattr(self, name) for name in internal_names)
        def setter(self, value):
            for name, val in zip(internal_names, value):
                setattr(self, name, val)
    else:
        def getter(self):
            return tuple(getattr(self, name, default) for name in internal_names)
        def setter(self, value):
            for name, val in zip(internal_names, value):
                if val is not default:
                    setattr(self, name, val)
    def deleter(self):
        for name in internal_names:
            delattr(self, name)
    return property(getter, setter, deleter, doc=doc)

def elementwise_property(attr, *, as_array=True, array_dim=None, doc=None, default=NO_VALUE):
    '''return property which returns tuple(element.attr for element in self).

    as_array: bool or 'xarray', default True
        return np.array of result instead of list.
    array_dim: None or str
        if provided and as_array=True, return xarray.DataArray instead,
            with this dimension name, and coord = elements from self.
    doc: None or str
        the docstring for this property
    default: any value, default NO_VALUE
        if provided, use this for any element missing the 'attr' attribute, instead of crashing.

    The property also supports setting values, e.g.:
        self.attr = ['a', 'b', 'c', 'd'] sets self[0].attr='a', self[1].attr='b', etc.
        self.attr = 'common_val' sets self[0].attr='common_val', self[1].attr='common_val', etc.
    NOTE: to avoid ambiguity, the only non-"common" values are lists and tuples;
        all other types will be treated as "common" (hence, set the same value for each element).

    This property does not support deleting values.
    '''
    def getter(self):
        if default is NO_VALUE:
            result = tuple(getattr(el, attr) for el in self)
        else:
            result = tuple(getattr(el, attr, default) for el in self)
        if as_array:
            if array_dim is None:
                result = np.array(result)
            else:
                result = xr.DataArray(list(result), dims=[array_dim], coords={array_dim: self})
        return result
    def setter(self, value):
        if isinstance(value, (list, tuple)):
            for el, val in zip(self, value):
                setattr(el, attr, val)
        else:
            for el in self:
                setattr(el, attr, value)
    return property(getter, setter, doc=doc)


### --------------------- Helpful to use with properties --------------------- ###

def dict_with_defaults_property(internal_name, *, key_aliases, doc=None):
    '''return a property which gives a dictionary, and gives key_aliases a chance to edit the dict.
    internal_name: str
        the name where this property is stored internally for obj.
    key_aliases: str or iterable of strs.
        the attributes of obj which are alias_key_of this property.
        str --> use obj.key_aliases.
    doc: None or str
        the docstring for this property
        if None, use f'dict with defaults determined by self.{key_aliases}'.

    Example:
        class Foo():
            special = dict_with_defaults_property('_special', key_aliases='_special_key_aliases')
            _special_key_aliases = ['special_key1', 'special_key2']
            special_key1 = alias_key_of('_special', 'key1', setdefault_value=5)
            special_key2 = alias_key_of('_special', 'key2')
        foo = Foo()
        # every time getting the dict from foo, use all the setdefault values as appropriate:
        foo.special  # --> dict(key1=5)
        foo.special = dict(key1=100)
        foo.special  # --> dict(key1=100)
        foo.special = dict(key3=30)
        foo.special  # --> dict(key3=30, key1=5)
        foo.special_key1 = 70
        foo.special  # --> dict(key3=30, key1=70)
        del foo.special['key1']
        foo.special  # --> dict(key3=30, key1=5)  # key1 was missing, so its setdefault value is used.

        # note that the dict itself is a normal dict; the magic happens when doing foo.special:
        foo.special = dict(key3=10, key1=80)
        special = foo.special
        special  # --> dict(key3=10, key1=80)
        del special['key1']
        special  # --> dict(key3=10)
        foo.special  # --> dict(key3=10, key1=5)  # key1 was missing, so its setdefault value is used.
        special  # --> dict(key3=10, key1=5)  # a new dict isn't created; foo.special is special.
    '''
    # [TODO] there's probably a cleaner way to achieve this behavior, e.g. make a subclass of dict.
    def apply_key_aliases(self, dict_):
        '''returns dict_ after applying all key_aliases to it.'''
        if isinstance(key_aliases, str):
            aliases = getattr(self, key_aliases)
        else:
            aliases = key_aliases
        for key_alias in aliases:
            with contextlib.suppress(KeyError):
                getattr(self, key_alias)
    def getter(self):
        try:
            result = getattr(self, internal_name)
        except AttributeError:
            result = dict()
            setattr(self, internal_name, result)
        apply_key_aliases(self, result)
        return result
    def setter(self, value):
        setattr(self, internal_name, value)
        apply_key_aliases(self, value)
    def deleter(self):
        delattr(self, internal_name)
    if doc is None:
        doc = f'dict with defaults determined by self.{key_aliases}'
    return property(getter, setter, deleter, doc=doc)
