"""
File Purpose: Miscellaneous quality-of-life functions for Object Oriented Programming tasks.
"""

from ...defaults import DEFAULTS


### --------------------- Apply if attribute exists --------------------- ###

def apply(x, fstr, *args, **kwargs):
    '''return x.fstr(*args, **kwargs), or x if x doesn't have an 'fstr' attribute.'''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    # pop default if it was provided.
    doing_default = 'default' in kwargs
    if doing_default:
        default = kwargs.pop('default')
    # call x.fstr(*args, **kwargs)   # (kwargs with 'default' popped.)
    if hasattr(x, fstr):
        return getattr(x, fstr)(*args, **kwargs)
    elif doing_default:
        return default
    else:
        return x


### --------------------- Metaclasses --------------------- ###

class MetaClsRepr(type):
    '''metaclass which affects repr for classes.
    classes can use metaclass=MetaClsRepr and define classmethod __cls_repr__ method,
        to define their own repr.
    '''
    def __repr__(cls):
        if hasattr(cls, '__cls_repr__'):
            return cls.__cls_repr__()
        else:
            return super().__repr__()
