"""
File Purpose: Sentinel values (like None, but not built-in to Python)
"""
import sys

class Sentinel():
    '''Unique sentinel values. adapted from PEP 661.

    name: str
        str defining this sentinel. e.g. 'UNSET'
    repr: None or str
        str defining repr for this sentinel. None --> use name.
    module_name: None or str
        name of module where this sentinel was defined. None --> infer it.
    unique_includes_module: bool, default False
        whether to include module name in "uniqueness" of this sentinel.
        True --> calling Sentinel(name0) in module1 is a different object than Sentinel(name0) called in module2.
        False --> Sentinel(name0) produces the same object regardless of where it was called from.
        default False --> can access any sentinel value from any module, by providing its string.
            e.g. Sentinel('UNSET') is UNSET, always.

    will crash if name is already associated to a Sentinel which is not an instance cls. Example:
        class Subclass1(Sentinel): pass
        class Subclass2(Sentinel): pass
        A = Sentinel('SENTINEL_A')
        Subclass1('SENTINEL_A')  # crashes; A is not an instance of Subclass1.
        A is Sentinel('SENTINEL_A')  # True, and no crash.
        B = Subclass1('SENTINEL_B')
        B is Sentinel('SENTINEL_B')  # True; B is an instance of Sentinel, because Subclass1 is a subclass of Sentinel
        Subclass2('SENTINEL_B')  # crashes; B is not an instance of Subclass2.
    '''
    _registry = {}  # registry of ALL Sentinel objects. (key: module_name-name, value: sentinel)
                    # editing this dictionary directly might have unexpected consequences.

    def __new__(cls, name, repr=None, module_name=None, unique_includes_module=False):
        '''return new Sentinel object.'''
        # note, would've liked to use '*' before module_name here,
        #    but not sure how to handle keyword-only arguments in __reduce__.
        name = str(name)
        repr = str(repr) if repr else name
        if module_name is None:
            try:
                module_name = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                module_name = __name__

        if unique_includes_module:
            registry_key = f'{module_name}-{name}'
        else:
            registry_key = name

        sentinel = cls._registry.get(registry_key, None)
        if sentinel is not None:
            if isinstance(sentinel, cls):
                return sentinel
            else:
                errmsg = (f'Sentinel with name={name!r} already exists, but is not an instance of cls={cls}.'
                          f'\nThe existing sentinel is: {sentinel!r}, an object with type={type(sentinel)}.')
                raise TypeError(errmsg)

        sentinel = super().__new__(cls)
        sentinel.name = name
        sentinel.repr = repr
        sentinel.module_name = module_name
        sentinel.unique_includes_module = unique_includes_module

        return cls._registry.setdefault(registry_key, sentinel)

    def __repr__(self):
        return self.repr

    def __reduce__(self):
        return (
            self.__class__,
            (
                self.name,
                self.repr,
                self.module_name,
                self.unique_includes_module,
            ),
        )

UNSET = Sentinel('UNSET')
NO_VALUE = Sentinel('NO_VALUE')
ATTR_UNSET = Sentinel('ATTR_UNSET')
RESULT_MISSING = Sentinel('RESULT_MISSING')
