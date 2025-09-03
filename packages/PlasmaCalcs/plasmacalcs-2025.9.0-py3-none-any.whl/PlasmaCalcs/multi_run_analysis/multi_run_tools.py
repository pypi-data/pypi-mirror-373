"""
File Purpose: tools related to multi-run analysis
"""
import os

from ..errors import FileContentsError
from ..tools import find_files_re, read_python_params_file


def canon_runs(dir=os.curdir, *, exclude=[], singles=False):
    '''returns dict of "canonical" runs within directory (and subdirectories).
    "canonical" if appearing within 'run' or 'runs' parameter of a _canon.txt file.

    keys are abspaths to directories containing the _canon.txt.
    values are lists of "canonical" runs within that directory.

    run paths within _canon.txt are interpreted from within the _canon.txt's directory.

    dir: str
        directory to search in.
    exclude: str, or list of strs
        exclude any subdirectories whose name equals one of these strings or re.fullmatch one of these strings.
        E.g. exclude='*[.]io' will exclude all subdirectories whose name ends with '.io';
            exclude='parallel' will exclude all subdirectories whose name equals 'parallel'.
    singles: bool
        if True, assert all run lists in result have length 1,
            and replace each runlist with runlist[0].
    '''
    canons = find_files_re('_canon[.]txt', dir=dir, exclude=exclude)
    result = {}
    for canon in canons:
        run_dir = os.path.dirname(canon)
        cparams = read_python_params_file(canon)
        runs = []
        if 'run' in cparams:
            runs.append(cparams['run'])
        if 'runs' in cparams:
            runs.extend(cparams['runs'])
        if len(runs) > 0:
            result.setdefault(run_dir, []).extend(runs)
    if singles:
        too_long = {k: v for k, v in result.items() if len(v) > 1}
        if len(too_long) > 0:
            errmsg = f"singles=True but _canon.txt specifies >1 run in some directories: {too_long}"
            raise FileContentsError(errmsg)
        for k, v in result.items():
            result[k] = v[0]
    # style: sort alphabetically by key
    result = {k: result[k] for k in sorted(result.keys())}
    return result
