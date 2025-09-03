"""
File Purpose: logging, recording info about state of code, etc.

For reproducibility in the future.
E.g., with results, also save git hash for current version of the code.
"""

import datetime
import os
import subprocess

from .sentinels import UNSET


### --------------------- git_hash --------------------- ###

def git_hash_local(*, default=UNSET):
    '''returns the git commit hash for current git HEAD within the local directory

    default: any object
        if not UNSET, and can't get hash (but filepath does exist),
        return default & print message, instead of crashing if can't get hash.
    '''
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except subprocess.CalledProcessError:
        if default is not UNSET:
            print(f'(failed to get git hash; returning default. At dir={repr(os.getcwd())})')
            return default
        raise

def git_hash(module_or_path='.', *, default=UNSET):
    '''returns the git commit hash for current git HEAD at the provided module or path.
    if string, treat it as a path; if module object, use path to module.__file__.
    module_or_path: string or module object, default '.'
        place to get git hash from.
        string --> path=module_or_path. If not a directory, also try os.path.dirname(path)
        module --> module=module_or_path. path=os.path.dirname(module.__file__)
    default: any object
        if provided, and can't get hash, return default & print message.
    '''
    try:
        if isinstance(module_or_path, str):
            path = module_or_path
        else:
            module = module_or_path
            path = module.__file__
        if not os.path.isdir(path):
            path = os.path.abspath(path)
            dirpath = os.path.dirname(path)
            if not os.path.isdir(dirpath):
                raise FileNotFoundError(f'{repr(path)} (not an existing directory). (\nalso {repr(dirpath)})')
            path = dirpath
        try:
            cwd0 = os.getcwd()
            os.chdir(path)
            return git_hash_local(default=default)
        finally:
            os.chdir(cwd0)
    except Exception:
        if default is not UNSET:
            print(f'(failed to get git hash; returning default. For input={repr(module_or_path)})')
            return default
        raise

def git_hash_here(globals_):
    '''returns git commit hash for the __file__ in the namespace where this function is called.'''
    return git_hash(globals_['__file__'])

def git_hash_PlasmaCalcs():
    '''returns the git commit hash for current git HEAD in PlasmaCalcs'''
    return git_hash_here(globals())


### --------------------- PlasmaCalcs version --------------------- ###

def _PlasmaCalcs_version():
    '''returns the current version of PlasmaCalcs, if available. Else, return None.'''
    try:
        from .. import __version__
    except ImportError:
        return None
    else:
        return __version__


### --------------------- datetime --------------------- ###

def datetime_now():
    '''current datetime as string according to user's computer. Include timezone.
    Uses "isoformat", with "_" separator: YYYY-MM-DD_HH:MM:SS.ssssss+HH:MM
    Original datetime object can be recovered via `datetime.datetime.fromisoformat(str)`
    '''
    return datetime.datetime.now().astimezone().isoformat(sep='_')


### --------------------- PlasmaCalcs version --------------------- ###

def code_snapshot_info():
    '''returns dict including info about right now, and the version of the code being used.

    Includes as many of the following as possible (uses None if info unavailable due to crash):
        'pc__version__': PlasmaCalcs version
        'pc__commit_hash': git hash for PlasmaCalcs
        'datetime': current datetime, in isoformat
    '''
    result = {}
    try:
        pc_version = _PlasmaCalcs_version()
    except Exception:
        pc_version = None
    result['pc__version__'] = pc_version
    try:
        pc_hash = git_hash_PlasmaCalcs()
    except Exception:
        pc_hash = None
    result['pc__commit_hash'] = pc_hash
    try:
        datetime = datetime_now()
    except Exception:
        datetime = None
    result['datetime'] = datetime
    return result
