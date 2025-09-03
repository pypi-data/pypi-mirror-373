"""
File Purpose: tools related to using a supercomputer / computer cluster.
"""
import os
import re
import warnings

from .io_tools import attempt_literal_eval
from .iterables import DictWithAliases
from .os_tools import find_files_re
from .sentinels import RESULT_MISSING
from ..errors import FileContentsConflictError


### --------------------- Finding jobfiles --------------------- ###

def find_jobfiles(dir=os.curdir, *, exclude=[]):
    '''find all jobfiles in this directory and all subdirectories.
    jobfiles are files which end with '.o' or '.oN' where N is an integer with any number of digits.

    exclude: str, or list of strs
        exclude any subdirectories whose name equals one of these strings or re.fullmatch one of these strings.
        E.g. exclude='*[.]io' will exclude all subdirectories whose name ends with '.io';
        exclude='parallel' will exclude all subdirectories whose name equals 'parallel'.

    returns list of abspaths to all jobfiles found.
    '''
    return find_files_re('.*[.]o[0-9]*', dir=dir, exclude=exclude)


### --------------------- Handling slurm files --------------------- ###

def find_slurmfiles(dir=os.curdir, *, exclude=[]):
    '''find all slurmfiles in this directory and all subdirectories.
    slurmfiles are files which end with '.slurm'.

    exclude: str, or list of strs
        exclude any subdirectories whose name equals one of these strings or re.fullmatch one of these strings.
        E.g. exclude='*[.]io' will exclude all subdirectories whose name ends with '.io';
        exclude='parallel' will exclude all subdirectories whose name equals 'parallel'.

    returns list of abspaths to all slurmfiles found.
    '''
    return find_files_re('.*[.]slurm', dir=dir, exclude=exclude)

class SlurmOptionsDict(DictWithAliases):
    '''DictWithAliases of slurm-related options.
    DEFAULT_ALIASES in this class tells all default aliases.
    '''
    DEFAULT_ALIASES = {
        '-J': '--job-name',
        '-o': '--output',
        '-p': '--partition',
        '-N': '--nodes',
        '-n': '--total-tasks',
        '--ntasks-per-node': '--tasks-per-node',
        '-t': '--time',
        '-A': '--account',
    }


def read_slurm_options(filename, *, eval=True):
    '''returns SlurmOptionsDict of all slurm-related options defined in this file.
    options are defined as lines which look like one of the following:
        "#SBATCH -N 4"  --> key='-N', value=4.
        "#SBATCH --time=1:00:00"  --> key='--time', value='1:00:00'

    eval: bool
        whether to attempt ast.literal_eval(value) for each value. (False --> keep all as str.)
    '''
    filename = os.path.abspath(filename)  # <-- makes error messages more verbose, if crash later.
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    pattern = re.compile(r'#SBATCH\s+(-.+?)(?:\s+|=)(.+?)\s*(#.*)?')
    #pattern = re.compile(r'#SBATCH\s+(-.+?\s+.+?|--.+?=.+?)(.+?)\s*(#.*)?')
    matches = [pattern.fullmatch(line) for line in lines]
    matches = [match for match in matches if match is not None]
    options = SlurmOptionsDict()
    for match in matches:
        key, value, comment = match.groups()
        if eval:
            value = attempt_literal_eval(value)
        if key in options:
            warnmsg = (f"multiple definitions of {key!r} in file {filename!r}"
                       "\n(read_slurm_options will keep only the last definition.)")
            warnings.warn(warnmsg)
        options[key] = value
    return options

def slurm_options_here(dir=os.curdir, *, conflicts='crash', only=None, eval=True):
    '''returns SlurmOptionsDict of all slurm-related options in files within this directory.
    searches all slurmfiles within this directory.

    conflicts: 'crash', 'drop'
        tells how to handle conflicts (key with different value or missing in different files).
        'crash' --> raise FileContentsConflictError if any conflicts.
        'drop' --> drop all keys with any sort of conflict.
    only: None, str, or list of str
        if provided, only include these keys in the result
        (and, only check these keys for conflicts!).
    eval: bool
        whether to attempt ast.literal_eval(value) for each value. (False --> keep all as str.)
    '''
    dir = os.path.abspath(dir)
    slurmfiles = find_slurmfiles(dir)
    if len(slurmfiles) == 0:
        raise FileNotFoundError(f'no slurmfiles found in directory {dir!r}')
    if isinstance(only, str):
        only = [only]
    results = []
    for f in slurmfiles:
        options = read_slurm_options(f, eval=eval)
        if only is not None:
            options = SlurmOptionsDict({key: options[key] for key in only if key in options})
        results.append(options)
    if len(results) > 1:
        # need to check for options conflicts.
        for key, val0 in list(results[0].items()):
            for opts in results[1:]:
                conflict = (val0 != opts.get(key, RESULT_MISSING))
                if conflict and conflicts == 'crash':
                    errmsg = (f'found multiple values for key {key!r} in slurmfiles {slurmfiles!r}\n'
                                f'Values found: {[opts.get(key, RESULT_MISSING) for opts in results]}')
                    raise FileContentsConflictError(errmsg)
                elif conflict and conflicts == 'drop':
                    for opts in results:
                        del opts[key]
    return results[0]

def slurm_option_here(key, dir=os.curdir, *, eval=True):
    '''return the value of the slurm-related option with this key, from slurm files within dir.
    searches all slurmfiles within this directory.
    Crashes if key not present with same exact value, in all slurmfiles.

    Recognizes some aliases for some keys; see SlurmOptionsDict.DEFAULT_ALIASES.
        (e.g. '-N' and '--nodes' are aliases of each other)

    key: str
        option or alias to option. Should include leading '-' or '--'.
    eval: bool
        whether to attempt ast.literal_eval(value) for each value. (False --> keep all as str.)

    Equivalent:
        slurm_options_here(dir, only=[key], ...)[key]
    '''
    return slurm_options_here(dir, only=key, conflicts='crash', eval=eval)[key]
