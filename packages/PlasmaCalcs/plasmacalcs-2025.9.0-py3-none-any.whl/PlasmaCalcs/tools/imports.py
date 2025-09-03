"""
File Purpose: reload, ImportFailed
"""

import importlib
import inspect
import sys
import warnings

from ..errors import ImportFailedError, InputMissingError
from ..defaults import DEFAULTS


### --------------------- reloading --------------------- ###

def enable_reload(package='PlasmaCalcs'):
    '''smashes the import cache for the provided package.
    All modules starting with this name will be removed from sys.modules.
    This does not actually reload any modules.
    However, it means the next time import is called for those modules, they will be reloaded.
    returns tuple listing of all names of affected modules.

    package: str or module
        the package for which to enable reload. if module, use package.__name__.
    '''
    if inspect.ismodule(package):
        package = package.__name__
    l = tuple(key for key in sys.modules.keys() if key.startswith(package))
    for key in l:
        del sys.modules[key]
    return l

def reload(package='PlasmaCalcs', *, return_affected=False, maintain_defaults=True):
    '''reloads the provided package.
    Similar to enable_reload(package); import package.

    maintain_defaults: bool, default True
        if True, update DEFAULTS in the reloaded package with any DEFAULTS set before reloading.
        Does nothing if the original package does not have a 'DEFAULTS' attribute.
        e.g. pc.reload() stores defaults0=pc.DEFAULTS, then reloads, then pc.DEFAULTS.update(defaults0).

    returns the reloaded package.
    if return_affected also return a list of all affected package names.

    NOTE: this reloads package but doesn't do it "in-place" (i.e. doesn't change the package variable).
    For example:
        import PlasmaCalcs as pc
        import mypackage as myp0
        myp1 = pc.reload(myp0)
        myp1 is myp0 --> False, because myp0 points to the pre-reload version of the package.

    Thus, to use this method, you should instead assign the package to the result, for example:
        import PlasmaCalcs as pc
        pc = pc.reload()

        # or, to reload a different package
        import mypackage as myp
        myp = pc.reload(myp)

    package: str or module
        the package to reload. if module, use package.__name__.
    '''
    if inspect.ismodule(package):
        package = package.__name__
    module = importlib.import_module(package)
    defaults0 = module.DEFAULTS if (maintain_defaults and 'DEFAULTS' in module.__dict__) else None
    affected = enable_reload(package)
    result = importlib.import_module(package)
    if defaults0 is not None:
        result.DEFAULTS.update(defaults0)
    return (result, affected) if return_affected else result


### --------------------- relative loading inside package --------------------- ###

def import_relative(name, globals):
    '''import a module relative to the caller's package; caller must provide globals().
    Examples: inside SymSolver.tools.arrays,
        import_relative('.numbers', globals()) <- equivalent -> import SymSolver.tools.numbers
        import_relative('..errors', globals()) <- equivalent -> import SymSolver.errors
    '''
    package = globals['__package__']
    return importlib.import_module(name, package=package)


### --------------------- import failure handling --------------------- ###

class ImportFailed():
    '''set modules which fail to import to be instances of this class;
    initialize with modulename, additional_error_message.
    when attempting to call or access any attribute of the ImportFailed object,
        raises ImportFailedError('. '.join(modulename, additional_error_message)).
    Also, if DEFAULTS.IMPORT_FAILURE_WARNINGS, make warning immediately when initialized.

    err: None, Exception, or str
        if provided, include str(err) when raising ImportFailedError
    locals: None or dict
        if provided, set locals['__pdoc__'][modulename] = False
        if abbrv provided, use abbrv instead of modulename.
        Use this to tell pdoc to skip the ImportFailed instance when creating docs pages.
    abbrv: None or str
        if provided, set locals['__pdoc__'][abbrv] = False

    Example:
        try:
            import h5netcdf
        except ImportError as err:
            h5netcdf = ImportFailed('h5netcdf', 'This module is required for compressing data.', err=err)

        h5netcdf.load(...)   # << attempt to use h5netcdf
        # if h5netcdf was imported successfully, it will work fine.
        # if h5netcdf failed to import, this error will be raised:
            ImportFailedError: h5netcdf. This module is required for compressing data.
            The original ImportError error was: No module named 'h5netcdf'
    '''
    def __init__(self, modulename, additional_error_message='', *, err=None, locals=None, abbrv=None):
        self.modulename = modulename
        self.additional_error_message = additional_error_message
        self.err = err
        if DEFAULTS.IMPORT_FAILURE_WARNINGS:
            warnings.warn(f'Failed to import module {self.error_message()}')
        # handle __pdoc__
        if (abbrv is not None) and (locals is None):
            raise InputMissingError('if providing abbrv, must also provide locals.')
        if locals is not None:
            key = modulename if abbrv is None else abbrv
            locals.setdefault('__pdoc__', {})[key] = False

    def error_message(self):
        str_add = str(self.additional_error_message)
        if len(str_add) > 0:
            str_add = '. ' + str_add
        result = self.modulename + str_add
        if self.err is not None:
            result += f'\nThe original ImportError was: {self.err}'
        return result

    def __getattr__(self, attr):
        '''tells how to do self.attr when it would otherwise fail.
        Here, raise ImportFailedError.
        '''
        raise ImportFailedError(self.error_message())

    def __call__(self, *args__None, **kw__None):
        '''tells how to call self, e.g. self(...). Here, raise ImportFailedError.'''
        raise ImportFailedError(self.error_message())

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.modulename)})'
