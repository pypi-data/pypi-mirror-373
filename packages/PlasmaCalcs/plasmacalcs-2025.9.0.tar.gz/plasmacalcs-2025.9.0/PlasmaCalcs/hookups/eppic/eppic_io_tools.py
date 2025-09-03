"""
File Purpose: misc. tools for reading directly from eppic files
"""
import collections
import datetime
import os
import re
import pandas as pd
import xarray as xr

from ...errors import (
    ValueLoadingError,
    FileContentsError, FileContentsConflictError, FileContentsMissingError,
    InputError,
)
from ...tools import (
    attempt_literal_eval, read_idl_params_file,
    InDir, find_jobfiles,
    RESULT_MISSING,
)

### --------------------- read eppic.i file --------------------- ###

def read_eppic_i_file(filename="eppic.i", *, eval=True):
    '''Parse EPPIC input from the file, returning (dict of global vars, dict of dists).
    dict of global vars has {varname: value} for all pairs not inside a distribution.
    dict of dists has {N: {varname: value} for all pairs in dist} for each dist;
        for each varname in a dist, ensure varname ends with str(N) (append it if necessary).
        the N's will all be stored here as ints.

    Arguments:
    filename: string, default 'eppic.i'
        file to read from.
    eval: bool, default True
        whether to attempt to evaluate the values,
        using ast.literal_eval (safer but less flexible than eval).
        if True, try to evaluate values but use strings if evaluation fails.
        if False, values will remain as strings.

    Notes:
    - file formatting:
        - semicolons (;) are used for comments. (idl format)
        - ignore blank lines & lines that don't assign a variable (missing '=')
        - ignores all leading & trailing whitespace in vars & values.
    - special var: "dist{N}", where N is any integer (or empty string).
        - after finding this, start storing lines in result["dist{dist}"]
            - e.g. "dist1=1" --> result["dist1"][var] = value.
                same behavior if "dist=1".
            - additionally, N will be appended to var names if it is not already there,
                e.g. "dist1=1", "var=7" --> result["dist1"]["var1"] = 7
        - if "dist{N}" appears AGAIN, use it as the new dist; store lines in result["dist{N}"]
    - special var: "fndist"
        - if found, stop storing lines in result["dist{dist}"]
    '''
    
    globs = dict()
    dists = dict()
    
    var_value_pairs = read_idl_params_file(filename,
                                           eval=False,  # eval below instead
                                           as_tuples=True)  # maintain order via tuples not dict.

    target = globs  # << this is where we are currently storing values.
    for (var, value) in var_value_pairs:
        # handle special var: "dist{N}"  (N might be the empty string)
        match = re.match(r'dist(\d*)', var)
        if match:
            # get "N"
            N, = match.groups()
            if N == '':
                N = value
            elif int(N) != int(value):
                raise NotImplementedError(f'found "distN = M", but N!=M. N={N!r}, M={value!r}')
            intN = int(N)
            strN = str(N)
            # "dist{N}" is found. Start storing lines in dists[int(N)]
            if intN in dists:
                raise NotImplementedError(f'"dist=N" (or distN=N) appears multiple times. N={N}')
            else:
                target = dict()
                dists[intN] = target
            continue
        # else:
        if eval:
            value = attempt_literal_eval(value)
        # handle special var: "fndist"
        if var == 'fndist':
            target = globs
            target[var] = value
            continue
        # handle other vars
        if eval:
            value = attempt_literal_eval(value)
        if target is not globs:  # if in a dist right now, ensure var ends with N
            if not var.endswith(strN):
                var = f'{var}{strN}'
        if var in target and target[var]!=value:  # Make warning if duplicate value.
            print(f'Warning: {repr(var)} appears in multiple lines, with different values!')
        # <<< actually store a value
        target[var] = value

    return (globs, dists)

def infer_eppic_dist_names(filename="eppic.i", *, missing_ok=True):
    '''return dict of {distnumber: name} for all dists in eppic.i file.
    name will be None if failed to infer the name.
    name is inferred from comment lines above the lines like dist=N.

    if not missing_ok, name must be inferred for all dists, otherwise crash.

    Comments with names have a few different possible formats:
    1) "; [anything] distribution: name".
        Possibly using ' ' or '-' instead of ':', and possibly using 'dist' instead of distribution.
        Also, possibly have another comment afterwards, e.g. "; [anything] dist - name  ; [anything]".
    2) "; [anything] --- name --- [anything]",
        with at least 3 '-' on either side, and nonzero whitespace between the '-' and the name.
    '''
    # read the file lines.
    with open(filename,"r") as file:
        lines = file.read().splitlines()
    # remove leading whitespace on all lines
    lines = [line.lstrip() for line in lines]
    # find location of lines like dist = N; capture dist number. (line might look like distN = N, instead)
    dist_lines = dict()  # {dist number: line number}
    for i, line in enumerate(lines):
        match = re.fullmatch(r'\s*dist(\d+)?\s*=\s*(\d+).*', line)
        if match:
            _, distN_as_str = match.groups()
            distN = int(distN_as_str)
            dist_lines[distN] = i
    # find location of earliest comment above dist line but after any other assignment line,
    #    and with less than 2 fully empty lines between it and the dist line.
    name_lines = dict()   # {dist number: line number of line with name}
    for distN, i in dist_lines.items():
        k = None
        nempty = 0
        for isub in range(1, i):
            j = i - isub
            if lines[j].startswith(';'):
                k = j
                nempty = 0
            elif '=' in lines[j]:
                break  # found a line with an equal sign; don't look for any higher-up comment lines.
            elif lines[j] == '':
                nempty += 1
                if nempty >= 2:
                    break  # found 2 empty lines in a row; don't look for any higher-up comment lines
        name_lines[distN] = k   # will be None if no name line found.
        if not missing_ok and k is None:
            raise ValueLoadingError(f'failed to find comment which might have name for dist {distN}')
    # infer names from comments. see docstring for details.
    dist_names = {i: None for i in dist_lines.keys()}  # {dist number: name}.  if name not found, use None.
    for i in name_lines:
        if name_lines[i] is not None:
            line = lines[name_lines[i]]
            # check if match format 1
            match = re.fullmatch(r';.*dist(ribution)?\s*[:-]?\s*([^;]+);?.*', line)
            if match:
                _, name = match.groups()
                dist_names[i] = name.strip()
                continue
            # check if match format 2
            match = re.fullmatch(r';.*---+\s+([^;]+)\s+---+.*', line)
            if match:
                name, = match.groups()
                dist_names[i] = name.strip()
                continue
            # no match
            if not missing_ok:
                errmsg = (f'failed to match name_lines[{i}] to any name-comment-line format;\n'
                          '(Acceptable formats include: "; --- name ---" and also "; [anything] dist[ribution] - name")\n'
                          f'at line {name_lines[i]} in file {os.path.abspath(filename)!r};\n'
                          f'line = {repr(line)}')
                raise ValueLoadingError(errmsg)
    return dist_names

### --------------------- update eppic.i file --------------------- ###
# i.e., make a new one based on the existing one, possibly with some parameters changed.

def update_eppic_i_file(src="eppic.i", dst="eppic_updated.i", values=dict(), *,
                        exists_ok=False, missing_values_ok=True, comment='previously={old}'):
    '''update eppic.i file from src, writing to dst.
    values: dict
        {varname: value} for all pairs to update.
        Can also provide {dist number: dict of {varname: value} pairs to update for this dist}
            (inside of dist number dicts, varname can end with dist number or not;
            assume it does end with dist number in the file itself though)
    exists_ok: bool, default False
        whether it is okay for dst to already exist.
    missing_values_ok: bool
        whether it is okay for some of the varnames in values to not exist in eppic.i
    comment: None or str
        if not None, append comment as a comment to all updated lines.
            (actually appends: '  ; {comment}'.)
        Only appends if line doesn't already end with comment.
        Also, this comment will be hit by .format(old=old value)

    Note: this routine isn't smart enough to add new varnames to eppic.i;
        it's only smart enough to update the values at existing varnames.

    return abspath to dst.
    '''
    # check that dst doesn't exist already
    if not exists_ok and os.path.exists(dst):
        errmsg = (f'dst file {dst!r} already exists!\n(abspath: {os.path.abspath(dst)!r})\n'
                  'Set exists_ok=True to enable overwriting existing file.')
        raise FileExistsError(errmsg)
    # get string to use for eppic.i file updated with values:
    updated_eppic_i_str = get_updated_eppic_i_str(src, values, missing_values_ok=missing_values_ok, comment=comment)
    # update values; using write mode such that previous file will be overwritten.
    with open(dst, 'w') as file:
        file.write(updated_eppic_i_str)
    # return abspath to dst
    return os.path.abspath(dst)

def get_updated_eppic_i_str(src="eppic.i", values=dict(), *, missing_values_ok=True, comment='previously={old}'):
    '''get str to use for updated eppic.i file from src, updated with these values.
    See help(update_eppic_i_file) for more details.
    '''
    # read lines from eppic.i file
    with open(src, 'r') as file:
        lines = file.read().splitlines()
    # get values to plug directly into eppic.i file (flatten any distribution dicts in values)
    # (note: pop values from values_flat after using them; crash if any remain unpopped but not missing_values_ok.)
    values_flat = _get_update_eppic_i_values_flat(values)
    # update lines, retaining all formatting and comments.
    # uses re to do smart matching, handling the fact that some value-setting lines might have comments;
    # lines look like:
    #    varname = value   ; possibly with a comment
    # Additionally, append comment as a comment (with leading ';') to end of lines with changed values.
    comment = '' if comment is None else f'  ; {comment}'
    for i, line in enumerate(lines):
        match = re.fullmatch(r'(\s*)(\w+)(\s*)(=)(\s*)(.*?)(\s*;.*)?', line)
        if match:
            s0, varname0, s1, _eq_, s2, value0, comment0 = match.groups()
            if varname0 in values_flat:
                new_value = str(values_flat.pop(varname0))
                if comment0 is None:
                    comment0 = ''
                lines[i] = f'{s0}{varname0}{s1}{_eq_}{s2}{new_value}{comment0}'
                # add comment if line doesn't end with it already, AND value was changed.
                value_same = (str(value0) == str(new_value))
                if not value_same:  # strs are unequal; maybe represent same number though.
                    value_same = (attempt_literal_eval(value0) == attempt_literal_eval(new_value))
                if not value_same:
                    comment_add = comment.format(old=value0)
                    if not line.rstrip().endswith(comment_add.rstrip()):
                        lines[i] = f'{lines[i]}{comment_add}'
    # check that all values were used
    if not missing_values_ok and len(values_flat) > 0:
        errmsg = (f'Some values were not used; key(s) not found: {list(values_flat.keys())}'
                    f'\nabspath to src = {os.path.abspath(src)!r}')
        raise ValueError(errmsg)
    return '\n'.join(lines)

def _get_update_eppic_i_values_flat(values=dict()):
    '''return "flat" dict of values to use for updating eppic.i file.
    This is a dict of {varname: value} for all pairs to update, in the original file.
    in result, varname for vars in dists will end with dist number.

    values: dict
        {varname: value} for all pairs to update.
        Can also provide {dist number: dict of {varname: value} pairs to update for this dist}
            (inside of dist number dicts, varname can end with dist number or not;
            assume it does end with dist number in the file itself though)
    '''
    result = dict()
    for varname, value in values.items():
        if isinstance(value, dict):
            N = str(varname)   # dist number.
            assert N.isdigit(), f'Expected dist key to look like a number, but got {varname!r}.'
            for varname2, value2 in value.items():
                # append dist number to varname2, if it doesn't end with it already:
                if not varname2.endswith(N):
                    varname2 = f'{varname2}{N}'
                result[varname2] = value2
        else:
            result[varname] = value
    return result


### --------------------- read eppic snaps info --------------------- ###

def read_eppic_snaps_info(dir=os.curdir, *, dt=None, snaps_from='parallel', read_mode=2):
    '''returns (snapnames, times).

    Gets snapnames from files in 'parallel' directory.
        E.g. parallel000073.h5 --> snapname '73'.
    If no 'parallel' directory, returns ([], []).

    dir: string (default '.')
        directory of 'eppic.i' file.
    dt: None or value
        the simulation time step; each snap's time is equal to dt * (snap name)
        if None, attempt to read 'dt' from eppic.i file.
    snaps_from: 'parallel' or 'timers'
        where to get snapnames from.
        parallel --> get from parallel directory.
        timers --> get from timers.dat file.
    '''
    if snaps_from == 'parallel':
        with InDir(dir):  # temporarily cd to dir; restore original dir after.
            # get dt
            if dt is None:
                globs, _dists = read_eppic_i_file()
                dt = globs['dt']
            # get snaps
            snapnums = []
            if not os.path.isdir('parallel'):
                return ([], [])
            for filename in os.listdir('parallel'):  # directory named 'parallel'
                if read_mode == 2 or read_mode == 3:
                    match = re.match(r'parallel(\d+)\.h5', filename)
                elif read_mode == 4:
                    match = re.match(r'parallel(\d+)\.bp', filename)
                if match:
                    snapname, = match.groups()
                    snapnums.append(int(snapname))
    elif snaps_from == 'timers':
        timers = read_timers_dat(dir, fix_snaps=False)  # don't fix snaps i.e. don't get snaps from parallel.
        snapnums = timers['it'].data
    else:
        raise InputError(f'Expected snaps_from="parallel" or "timers", but got {snaps_from!r}.')
    snapnums = sorted(snapnums)
    snapnames, times = [], []
    for snapnum in snapnums:
        snapnames.append(str(snapnum))
        times.append(dt * snapnum)
    return (snapnames, times)


### --------------------- read moments.out files --------------------- ###

def read_moments_out_files(dir=os.curdir):
    """
    Read moments*.out files.
    dir: string (default '.')
        directory of 'eppic.i' file.
        momentsN.out files should be located inside dir/domain000
            or might be dir/domain0000, for "newer" versions of EPPIC.

    returns a 3D dictionary {dist: {moment: {time: value}}}
    """

    dists = {}
    moments_dir = os.path.join(dir, 'domain0000')
    if not os.path.isdir(moments_dir):
        moments_dir = os.path.join(dir, 'domain000')
        if not os.path.isdir(moments_dir):
            raise FileNotFoundError(f'{moments_dir!r} (or similar but ending with domain0000).')

    # GET FILE NAMES AND CORRESPONDING DISTRIBUTION NUMBERS
    with InDir(moments_dir): # temporarily cd to dir; restore original dir after.
        # make a dictionary of moments*.out files with *'s as keys i.e. {0: "moments0.out", 1: "moments1.out", etc.}
        moments_out_files = {}
        for filename in sorted(os.listdir()):
            match = re.fullmatch(r'moments(\d+)\.out',filename)
            if match:
                dist_num, = match.groups()
                moments_out_files[dist_num] = match.string

        # SPECIFY NEW COLUMN NAMES
        column_names = ['Snap', 'Vx_Mean', 'Vx_Variance', 'Vx_Moment3', 'Vx_Moment4', 'Vy_Mean', 'Vy_Variance',
                        'Vy_Moment3', 'Vy_Moment4', 'Vz_Mean', 'Vz_Variance', 'Vz_Moment3', 'Vz_Moment4']

        # LOOP THROUGH FILES
        for distribution_number in moments_out_files:
            filename = moments_out_files[distribution_number]
            # LOAD DATA (WITH NEW COLUMN NAMES)
            data = pd.read_csv(filename, sep=r'\s+', skiprows=1, names=column_names, index_col=0)
            # CONVERT DATA TO DICTIONARY
            data_dict = data.to_dict()
            # APPEND DICTIONARY TO DICTIONARY
            dists[distribution_number] = data_dict

    return dists


### --------------------- get number of processors used --------------------- ###

def _eppic_mpi_processors_from_jobfile(f):
    '''return number of mpi processors used to run eppic based on this jobfile.
    f: str, path to file containing a line like: "MPI STARTING N PROCESSORS" with N an integer.
    '''
    with open(f, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    pattern = re.compile(r'MPI STARTING (\d+) PROCESSORS')
    matches = [pattern.fullmatch(line) for line in lines]
    matches = [match for match in matches if match is not None]
    Ns = [int(match.group(1)) for match in matches]
    if len(Ns) == 0:
        errmsg = f'failed to find any lines like "MPI STARTING N PROCESSORS" in file {f!r}'
        raise FileContentsMissingError(errmsg)
    if len(set(Ns)) > 1:
        errmsg = f'found multiple lines like "MPI STARTING N PROCESSORS" in file {f!r}\ngiving different N={Ns}'
        raise FileContentsConflictError(errmsg)
    return Ns[0]

def n_mpi_processors(dir=os.curdir):
    '''return number of mpi processors used to run the run at this directory.
    searches all jobfiles (see find_jobfiles) to determine number of processors,
        from line like "MPI STARTING N PROCESSORS" with N an integer.
    if result is ambiguous (different N from multiple places), raise a FileContentsConflictError.
    if no jobfiles found, raise FileNotFoundError.
    if some jobfiles found but none tell us how many processors were used, raise FileContentsMissingError.
    '''
    dir = os.path.abspath(dir)
    jobfiles = find_jobfiles(dir)
    if len(jobfiles) == 0:
        raise FileNotFoundError(f'no jobfiles found in directory {dir!r}')
    Ns = []
    for f in jobfiles:
        try:
            N = _eppic_mpi_processors_from_jobfile(f)
        except FileContentsMissingError:
            continue  # skip this jobfile, doesn't contain any mpi processor info.
        else:
            Ns.append(N)
    if len(Ns) == 0:
        raise FileContentsMissingError(f'no jobfiles found in directory {dir!r} which contain mpi processor info.')
    if len(set(Ns)) > 1:   # -- note, the len=0 case is handled by _eppic_mpi_processors_from_jobfile.
        errmsg = (f'found multiple lines like "MPI STARTING N PROCESSORS" in jobfiles {jobfiles!r}\n'
                    f'giving different N={Ns}')
        raise FileContentsConflictError(errmsg)
    return Ns[0]


### --------------------- get wall clock time from jobfile --------------------- ###

def eppic_clock_times_from_jobfile(f):
    '''return clock times from jobfile.
    result can have keys 'start', 'stepstart', 'end':
        start: datetime telling when the run started. From line like:
            "EPPIC Starting at: Friday 02/28/25 12:32:47"
        stepstart: datetime telling when the iterations started. From line like:
            "; --- iterations starting at time: Friday 02/28/25 12:33:31"
        end: datetime telling when the run ended. Various possibilities.
            (1) run ended normally. Two options:
                (a) (this one is tested first): eppic message. Line looks like:
                    "EPPIC ending normally at: Thursday 02/27/25 13:38:20
                (b): slurm file printout. Line looks like:
                    "job total time: NNN seconds"
            (2) timeout due to hitting time limit. Line like ('...' can be any characters):
                "slurmstepd: error: ... CANCELLED AT 2025-02-28T13:32:14 DUE TO TIME LIMIT ***"
            (3) eppic crashed. Line looks like:
                "job total time: NNN seconds"

    result can also have keys 'init_seconds', 'steps_seconds', 'total_seconds':
        init_seconds: (stepstart - start) [seconds]
        steps_seconds: (end - stepstart), [seconds]
        total_seconds: (end - start), [seconds]
    '''
    result = {}
    with open(f, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    # start
    pattern = r'EPPIC Starting at: (.+)'
    matches = [re.fullmatch(pattern, line) for line in lines]
    matches = [match for match in matches if match is not None]
    if len(matches) > 1:
        raise FileContentsError(f'multiple lines like {pattern!r} in file {f!r}')
    elif len(matches) == 1:
        tt, = matches[0].groups()
        result['start'] = datetime.datetime.strptime(tt, '%A %m/%d/%y %H:%M:%S')
    # stepstart
    pattern = r'; --- iterations starting at time: (.+)'
    matches = [re.fullmatch(pattern, line) for line in lines]
    matches = [match for match in matches if match is not None]
    if len(matches) > 1:
        raise FileContentsError(f'multiple lines like {pattern!r} in file {f!r}')
    elif len(matches) == 1:
        tt, = matches[0].groups()
        result['stepstart'] = datetime.datetime.strptime(tt, '%A %m/%d/%y %H:%M:%S')
    # end (1)(a)
    pattern = 'EPPIC ending normally at: (.+)'
    matches = [re.fullmatch(pattern, line) for line in lines]
    matches = [match for match in matches if match is not None]
    if len(matches) > 1:
        raise FileContentsError(f'multiple lines like {pattern!r} in file {f!r}')
    elif len(matches) == 1:
        tt, = matches[0].groups()
        result['end'] = datetime.datetime.strptime(tt, '%A %m/%d/%y %H:%M:%S')
    # end (2)
    if 'end' not in result:
        pattern = r'(?:.*)CANCELLED AT (.+) DUE TO TIME LIMIT(?:.*)'
        matches = [re.fullmatch(pattern, line) for line in lines]
        matches = [match for match in matches if match is not None]
        if len(matches) > 1:
            raise FileContentsError(f'multiple lines like {pattern!r} in file {f!r}')
        elif len(matches) == 1:
            tt, = matches[0].groups()
            result['end'] = datetime.datetime.strptime(tt, '%Y-%m-%dT%H:%M:%S')
    # end (3), and (1)(b)
    if 'end' not in result:
        pattern = r'job total time: (\d+) seconds'
        matches = [re.fullmatch(pattern, line) for line in lines]
        matches = [match for match in matches if match is not None]
        if len(matches) > 1:
            raise FileContentsError(f'multiple lines like {pattern!r} in file {f!r}')
        elif len(matches) == 1:
            tt, = matches[0].groups()
            result['end'] = result['start'] + datetime.timedelta(seconds=int(tt))
    # durations
    if 'start' in result and 'stepstart' in result:
        result['init_seconds'] = (result['stepstart'] - result['start']).total_seconds()
    if 'stepstart' in result and 'end' in result:
        result['steps_seconds'] = (result['end'] - result['stepstart']).total_seconds()
    if 'start' in result and 'end' in result:
        result['total_seconds'] = (result['end'] - result['start']).total_seconds()
    return result

def eppic_clock_times_here(dir=os.curdir):
    '''return clock times from jobfile(s) within this directory.
    Crash if multiple jobfiles within this directory tell conflicting times.

    result can have keys 'start', 'stepstart', 'end':
        start: datetime telling when the run started.
        stepstart: datetime telling when the iterations started.
        end: datetime telling when the run ended.

    result can also have keys 'init_seconds', 'steps_seconds', 'total_seconds':
        init_seconds: (stepstart - start) [seconds]
        steps_seconds: (end - stepstart), [seconds]
        total_seconds: (end - start), [seconds]
    '''
    dir = os.path.abspath(dir)
    jobfiles = find_jobfiles(dir)
    if len(jobfiles) == 0:
        raise FileNotFoundError(f'no jobfiles found in directory {dir!r}')
    results = []
    for f in jobfiles:
        results.append(eppic_clock_times_from_jobfile(f))
    # check for conflicts, and combine results into one place
    result = {}
    allkeys = ['start', 'stepstart', 'end', 'init_seconds', 'steps_seconds', 'total_seconds']
    for key in allkeys:
        values = [r[key] for r in results if key in r]
        if len(values) > 1:
            if any(v != values[0] for v in values[1:]):
                errmsg = (f'conflicting values for {key!r} from jobfiles {jobfiles!r}:\n'
                            f'{values}')
                raise FileContentsConflictError(errmsg)
        if len(values) > 0:
            result[key] = values[0]
    return result


### --------------------- get timers.dat info --------------------- ###

def read_timers_dat(dir=os.curdir, filename='domain0000/timers.dat', *, fix_snaps=True, as_array=False):
    '''read timers.dat info into an xarray.Dataset.
    The "iter #" will be used as the time coordinate, but renamed to "it".
    
    filename: str
        path to timers.dat file.
        if can't find it, but it has 'domain000' or 'domain0000', check the other one.
            E.g. 'domain0000/timers.dat' doesn't exist --> check if 'domain000/timers.dat' exists.
    fix_snaps: bool
        whether to fill NaNs if the last snap is missing from timers.dat, but in parallel folder,
        which can occur if run crashes after saving snap but before writing to timers.dat.
    as_array: bool
        whether to use xarray.Dataset.to_array() to return a DataArray instead of Dataset.
        if True, vars from Dataset will be concatenated along the new dimension named 'timer'.
    '''
    filename = os.path.abspath(os.path.join(dir, filename))
    if not os.path.exists(filename):
        filename_orig = filename
        if 'domain0000' in filename_orig:
            filename = filename_orig.replace('domain0000', 'domain000')
        elif 'domain000' in filename_orig:
            filename = filename_orig.replace('domain000', 'domain0000')
        if not os.path.exists(filename):
            raise FileNotFoundError(f'neither exists: {filename_orig!r},\n{filename!r}')
    ## determine any lines to skip
    # skip any reprinted header (due to continuing run from rst files).
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line.lstrip() for line in lines]
    its, otherstuff = zip(*[line.split(maxsplit=1) for line in lines])   # 'iter #', remaining part of line.
    iheaders = [i for i, it in enumerate(its) if not it.isdigit()]
    # skip any repeated its (due to continuing run from rst files).
    #   (e.g., it 0, 100, 200, save rst, 300, stop. restart --> it 300, 400, ....
    #    Note that it 300 appeared twice. Keep only the last appearance of it,
    #    since the last appearance corresponds to values actually saved to a snapshot.)
    it_counts = collections.Counter(its)
    irepeats = []
    for i, it in enumerate(its):
        if it_counts[it] > 1:
            it_counts[it] -= 1
            irepeats.append(i)
        else:
            del it_counts[it]
    # all lines to skip:
    iskip = set(iheaders).union(set(irepeats)) - set([0])  # don't skip row 0 which has the header.
    ## pandas dataframe from file data:
    # use sep=\s\s+ because separation between cols is at least 2 spaces,
    #   while some column header names contain single spaces in them.
    df = pd.read_csv(filename, sep=r'\s\s+', engine='python', skiprows=iskip)  # engine='python' to use regex matching.
    ## fix snaps (if any snap got saved but missing from timers.dat)
    if fix_snaps:
        snapnames, _times = read_eppic_snaps_info(dir)
        isnaps = [int(snapname) for snapname in snapnames]
        if len(df) != len(snapnames):
            if len(df) == len(snapnames) - 1:  # last snap didn't get written to timers.dat.
                df.loc[len(df), 'iter #'] = isnaps[-1]  # new row of NaN values with the correct snap number.
    # convert to xarray.Dataset
    result = xr.Dataset.from_dataframe(df)
    result = result.assign_coords({'it': ('index', result['iter #'].data)})  
    result = result.swap_dims({'index': 'it'}).drop_vars(['index', 'iter #'])
    # if as_array, convert to xarray.DataArray
    if as_array:
        result = result.to_array(dim='timer')
    return result
