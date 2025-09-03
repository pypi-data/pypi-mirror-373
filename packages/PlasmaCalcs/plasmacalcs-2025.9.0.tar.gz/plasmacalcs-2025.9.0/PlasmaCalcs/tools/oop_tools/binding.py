"""
File Purpose: binding functions to already-existing classes

Motivation: it is convenient to be able to add many functions to classes after their creation.
This facilitates a useful design principle:
    - when creating a class, only define a minimal set of behaviors.
    - when adding new behaviors to an existing class, bind new attributes/methods to the class,
        OUTSIDE of the class definition, rather than editing the class defintion directly.


Usually it is sufficient to use this module in the following way:
    from binding_module import Binding
    binding = Binding(locals())

    class MyClass(...):
        # this class could be defined here, or literally anywhere else.
        # e.g. "from module_with_class import MyClass" is fine too.

    with binding.to(MyClass):
        @binding
        def foo1(self, *args, **kw):    # any signature is fine, e.g. foo1(self, x) is fine too.
            # < code for foo1 goes here

        @binding
        def foo2(self, *args, **kw):
            # < code for foo2 goes here

        # ... can define any number of functions using @binding

    print(MyClass.foo1)
    --> (info about the bound method foo1 of MyClass, defined above)
    print(foo1)
    --> (NameError; foo1 is undefined in this namespace after exiting the 'with' block.)

It is also possible to keep a local copy(s) to the defined function(s),
or to bind them as staticmethod or classmethod. See help(Binding) for details.
"""

from ..docs_tools import format_docstring
from ..properties import (
    alias, alias_to_result_of,
)
from ..sentinels import NO_VALUE
from ...errors import BindingError


### --------------------- Lightweight single-use decorator --------------------- ###

def bind_to(*targets):
    '''returns a function decorator which binds f to target.(f.__name__) for target in targets.
    This decorator returns the unbound version of f.
    Example, equivalent to defining foo inside MyClass, and also in the local namespace:
        @bind_to(MyClass)
        def foo(self, args):
            # <code for foo>

    If you want foo to no longer be defined in the local namespace, you can delete it afterwards:
        del foo

    If you want to do this for many functions but don't want to delete each one manually,
    consider using Binding() instead.
    '''
    def bind_then_return_f(f):
        '''binds f to targets, then returns f.'''
        for target in targets:
            setattr(target, f.__name__, f)
        return f
    return bind_then_return_f


### --------------------- the Binding class --------------------- ###

class Binding():
    '''context manager for binding environment.
    provides these function decorators:
        @self (or @self.bind()) --> bind function or class to each target from self.default_targets.
        @self.binder(*targets) --> bind function or class to each target from targets.
    bindings at the corresponding attribute name e.g. target.(func.__name__) = func.
    Upon exiting, restore original state for names in self.namespace of any objects
        decorated via @self, @self.bind(), or @self.bind_to().

    To bind, but ALSO keep the function in the local namespace (i.e. don't remove it upon exiting),
        use keep_local=True. Either in 'self.bind(keep_local=True)'
        or 'with binding.to(*targets, keep_local=True)'.
    To bind a special method type (e.g., staticmethod, classmethod), use the methodtype parameter,
        e.g. methodtype=staticmethod. Either in 'self.bind(methodtype=staticmethod)'
        or 'with binding.to(..., methodtype=staticmethod)'
    Also, upon exiting context, (i.e., after 'with' block),
        restore self.keep_local and self.methodtype to their original values
        (or their values just before the most recent call to self.to(...),
        if context hasn't been exited since last call to self.to.)

    EXAMPLE:
    # originally, foo1, Foo3, foo4, foo5 undefined, but foo2 defined as foo2_original.
    binding = Binding(locals())
    with binding.to(MyClass):
        @binding
        def foo1(self, args):          # binds MyClass.foo1 = foo1
            # <code for foo1>

        @binding.binder(MySecondClass)
        def foo2(self, args):          # binds MySecondClass.foo2 = foo2
            # <code for foo2>

        @binding.bind()  # equivalent to @binding
        class Foo3(self, args):        # binds MyClass.Foo3 = Foo3
            # <code for Foo3>

        @binding.binder(MySecondClass, MyThirdClass)
        def foo4(self, args):          # binds MySecondClass.foo4 = foo4; MyThirdClass.foo4 = foo4
            # <code for foo4>

        @binding.bind(keep_local=True)
        def foo5(self, args):          # MyClass.foo5 = foo5
            # <code for foo5>

        @binding.bind(methodtype=staticmethod)
        def foo6(args):                # MyClass.foo6 = staticmethod(foo6)
            # <code for foo6>

    # upon exiting, alter the local namespace: delete foo1, Foo3, foo4; set foo2 = foo2_original.
    # (do not delete foo5 from the namespace since keep_local=True was used for foo5.)

    ARGS:
        namespace: dict
            the namespace to clean up upon exiting the context.
            This class was designed with the intention that:
                namespace=locals().
        *default_targets: classes
            the targets to which objects decorated with @self.bind() will be bound
            If this list is empty, trying to use self.bind() will raise a ValueError.
            To enter custom targets, use self.bind_to instead.
        keep_local: bool, default False
            default value for whether to keep local copies of the bound functions.
            E.g. if self.keep_local=True, then by default we will keep local copies.
    '''
    # # # CREATION # # #
    def __init__(self, namespace, *default_targets, keep_local=False, methodtype=None):
        self.namespace = namespace
        self.default_targets = default_targets
        self.keep_local = keep_local
        self.methodtype = methodtype
        self._remember_settings = dict()  # << restore values then clear upon exiting 'with' block.
        self._reset_flagged()

    # # # CONTEXT MANAGER # # #
    def _reset_flagged(self):
        '''resets/creates flagged trackers in self.'''
        self.flagged_for_restoration = dict()
        self.flagged_for_deletion = set()
        
    def __enter__(self):
        memory = self._remember_settings
        if 'keep_local' not in memory:
            memory['keep_local'] = self.keep_local
        if 'methodtype' not in memory:
            memory['methodtype'] = self.methodtype

    def __exit__(self, *_unused_args):
        self.cleanup()
        for attr, value in self._remember_settings.items():
            setattr(self, attr, value)
        self._remember_settings.clear()

    def cleanup(self):
        '''cleans up self.namespace appropriately, following these rules:
        1) previously-defined names in self.namespace (defined first without using self)
            which were overwritten to point at an object wrapped by self
            will be restored to their original values.
        2) previously undefined objects in self.namespace
            which were written to point at an object wrapped by self
            will be removed from self.namespace.
        '''
        for name in self.flagged_for_deletion:
            del self.namespace[name]
        for fname, forig in self.flagged_for_restoration.items():
            self.namespace[fname] = forig
        self._reset_flagged()

    # # # BINDING # # #
    _bind_kwarg_docs = \
        '''keep_local: bool or None, default None
            if None, use self.keep_local instead. (self.keep_local=False by default)
            if True, instead don't flag for cleanup, and return the original function.
            else (default), flag for cleanup, and return a BindingError object
                    (which is only relevant if attempting to access the function before cleanup).
        methodtype: None, staticmethod, or classmethod
            if None, use self.methodtype instead. (self.methodtype=None by default)
            if still not None, bind methodtype(f) instead of f.'''

    @format_docstring(_bind_kwarg_docs=_bind_kwarg_docs)
    def bind(self, *, keep_local=None, methodtype=None):
        '''returns decorator; decorator(f) binds f to target.(f.__name__) for target in self.default_targets,
        and also flags f appropriately for cleanup later when exiting the Binding context.

        kwargs determine the behavior for the resulting decorator:
        {_bind_kwarg_docs}
        '''
        if keep_local is None: keep_local = self.keep_local
        if len(self.default_targets) == 0:
            raise ValueError('self.bind() uses self.default_targets, but self.default_targets is empty!')
        return self.binder(*self.default_targets, keep_local=keep_local, methodtype=methodtype)

    @format_docstring(_bind_kwarg_docs=_bind_kwarg_docs)
    def binder(self, *targets, keep_local=None, methodtype=None):
        '''returns decorator(f); decorator(f) binds f to target.(f.__name__) for target in targets,
        and also flags f appropriately for cleanup later when exiting the Binding context.

        if keep_local and methodtype determine behavior for the resulting decorator_maker:
        {_bind_kwarg_docs}
        '''
        if keep_local is None:
            keep_local = self.keep_local
        if methodtype is None:
            methodtype = self.methodtype
        kw = dict(keep_local=keep_local, methodtype=methodtype)
        # Could define the result with 'if' statements inside it,
        #   but it's easier to debug anything going wrong if there are
        #   different function names, based on keep_local and methodtype.
        # use_result is shorthand so we don't need to write all the function names twice.
        result = dict()   # easier for me to understand than 'nonlocal' or 'global'
        def use_result(decorator):
            result['val'] = decorator
            return decorator
        # loop through all combinations of keep_local and methodtype.
        if methodtype is None:
            if keep_local:
                @use_result
                def bind_and_keep_f(f): return self.direct_bind(f, *targets, **kw)
            else:
                @use_result
                def bind_f(f): return self.direct_bind(f, *targets, **kw)
        elif methodtype is staticmethod:
            if keep_local:
                @use_result
                def bind_staticmethod_and_keep_f(f): return self.direct_bind(f, *targets, **kw)
            else:
                @use_result
                def bind_staticmethod_f(f): return self.direct_bind(f, *targets, **kw)
        elif methodtype is classmethod:
            if keep_local:
                @use_result
                def bind_classmethod_and_keep_f(f): return self.direct_bind(f, *targets, **kw)
            else:
                @use_result
                def bind_classmethod_f(f): return self.direct_bind(f, *targets, **kw)
        else:
            if keep_local:
                @use_result
                def bind_specialmethod_and_keep_f(f): return self.direct_bind(f, *targets, **kw)
            else:
                @use_result
                def bind_specialmethod_f(f): return self.direct_bind(f, *targets, **kw)
        return result['val']

    @format_docstring(_bind_kwarg_docs=_bind_kwarg_docs)
    def direct_bind(self, f, *targets, keep_local=None, methodtype=None):
        '''binds f to target.(f.__name__) for target in targets, then flags f appropriately for cleanup.
        named "direct" bind because this is not a function decorator.

        {_bind_kwarg_docs}
        '''
        if keep_local is None:
            keep_local = self.keep_local
        if methodtype is None:
            methodtype = self.methodtype
        fname = f.__name__
        # bind to targets
        fbind = f if (methodtype is None) else methodtype(f)
        for target in targets:
            setattr(target, fname, fbind)
        # handle flagging appropriately for cleanup later.
        if not keep_local:
            restore = self.flagged_for_restoration
            delete = self.flagged_for_deletion
            if (fname in restore) or (fname in delete):
                return   # already flagged; don't flag again.
            if fname in self.namespace:
                restore[fname] = self.namespace[fname]
            else:
                self.flagged_for_deletion = delete.union((fname,))
        # return result
        return f if keep_local else BindingError(f)

    @format_docstring(_bind_kwarg_docs=_bind_kwarg_docs)
    def bind_to(self, cls, f, *, keep_local=None, methodtype=None):
        '''bind f to cls. Equivalent to self.direct_bind(self, f, cls, **kw) with same kw as provided here.

        {_bind_kwarg_docs}
        '''
        return self.direct_bind(f, cls, keep_local=keep_local, methodtype=methodtype)

    # # # FREQUENTLY USED CONVENIENCE # # #
    def to(self, *targets, keep_local=NO_VALUE, methodtype=NO_VALUE):
        '''sets targets in self then returns self.
        convenient for writing context entry like this:
        binding = Binding(locals())
        with binding.to(MyClass1):
            @binding
            def foo1(args):
                #...

        if keep_local and/or methodtype are provided,
            set those attributes in self, but ALSO provide the instruction to self
            to return those attributes to their previous state upon next exiting context.
        '''
        self.default_targets = targets
        memory = self._remember_settings
        if keep_local is not NO_VALUE:
            memory['keep_local'] = self.keep_local
            self.keep_local = keep_local
        if methodtype is not NO_VALUE:
            memory['methodtype'] = self.methodtype
            self.methodtype = methodtype
        return self

    targetting = alias('to')

    __call__ = alias_to_result_of('bind',
        doc='''alias to result of self.bind().
        this means you can write @self instead of @self.bind(). E.g:
        binding = Binding(locals())
        with binding.to(MyClass1):
            @binding
            def foo1(args):
                #...
        ''')

    # # # LESS-OFTEN USED CONVENIENCE # # #
    def with_targets(self, *targets):
        '''return Binding object with same namespace as self, but using the provided targets instead.'''
        return Binding(self.namespace, *targets)

    with_target = alias('with_targets')

    target = property(lambda self: self.get_target(),
            lambda self, value: self.set_target(value),
            doc='''@self.bind() binds objects to target.(object.__name__).
            When len(self.default_targets)==0, roughly an alias to self.default_targets.
            Otherwise irrelevant; see self.default_targets instead.''')

    def get_target(self):
        '''gets binding target of self. makes ValueError if self has not precisely 1 target.'''
        if len(self.default_targets) == 1:
            return self.default_targets[0]
        else:
            raise ValueError(f'zero or multiple targets detected: {self.default_targets}')

    def set_target(self, target):
        '''sets binding target of self to target. (used in self.bind)'''
        self.default_targets = [target]
