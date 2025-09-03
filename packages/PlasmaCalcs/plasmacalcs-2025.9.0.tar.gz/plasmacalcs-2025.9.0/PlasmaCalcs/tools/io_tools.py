"""
File Purpose: misc tools for input/output to files.

For checking file existence or creating new files, see os_tools instead.
"""

import ast
import os
import re

from ..errors import FileContentsMissingError


### --------------------- attempt to eval string --------------------- ###

def attempt_literal_eval(s):
    '''returns ast.literal_eval(s), or s if the literal_eval fails.'''
    try:
        return ast.literal_eval(s)
    except Exception as err:
        # failed to evaluate. Might be string, or might be int with leading 0s.
        if isinstance(err, SyntaxError):  # <-- occurs if s is an int with leading 0s.
            try:
                return int(s)
            except ValueError:
                # failed to convert to int; return original string.
                pass
        return s


### --------------------- parse params from idl-like file --------------------- ###

def read_idl_params_file(filename, *, eval=True, as_tuples=False):
    '''parse idl file of params into a python dictionary of params.

    filename: string
        file to read from.
    eval: bool, default True
        whether to attempt to evaluate the values,
        using ast.literal_eval (safer but less flexible than eval).
        if True, try to evaluate values but use strings if evaluation fails.
        if False, values will remain as strings.
    as_tuples: bool, default False
        if True, return list of tuples instead of dictionary.
        list of tuples guaranteed to appear in the same order as in the idl file.

    File formatting notes:
        - semicolons (;) are used for comments. (idl format)
        - ignore blank lines & lines that don't assign a variable (missing '=')
        - ignores all leading & trailing whitespace in vars & values.
    '''
    filename = os.path.abspath(filename)  # <-- makes error messages more verbose, if crash later.
    # read the file lines.
    with open(filename, 'r') as file:
        lines = file.readlines()
    # remove comments
    lines = [line.split(";",1)[0] for line in lines]
    # trim whitespace
    lines = [line.strip() for line in lines]
    # remove empty lines, and remove lines without an equal sign.
    lines = [line for line in lines if line!='' and ('=' in line)]
    # split lines into vars & values
    var_value_pairs = [line.split("=",1) for line in lines]
    # cleanup whitespace in vars & values
    var_value_pairs = [(var.strip(), value.strip()) for (var, value) in var_value_pairs]

    if eval:
        var_value_pairs = [(var, attempt_literal_eval(value)) for (var, value) in var_value_pairs]

    return var_value_pairs if as_tuples else dict(var_value_pairs)

def updated_idl_params_file(filename, params, *, dst=None, missing_ok=False):
    '''create updated idl file, like at filename but updating the indicated params.
    returns updated file contents as str if dst is None, else abspath to dst.

    NEVER overwrites any existing file.

    filename: string
        file to read from.
    params: dict of params to update.
        keys are param names.
        values are param values or strings (internally, uses str(val) for each val).
        (if you need a string-valued param within the file, use pattern: '"val"' or "'val'".)
    dst: None or str
        file to write result to.
        None --> return string of updated file contents instead of creating a new file.
    missing_ok: bool
        whether it is okay for one or more of the params to be missing from the file.
        False --> if any params missing, crash.
    '''
    filename = os.path.abspath(filename)  # <-- makes error messages more verbose, if crash later.
    if (dst is not None):
        dst = os.path.abspath(dst)
        if os.path.exists(dst):
            raise FileExistsError(f"dst exists already! dst={dst!r}")
    # read the file lines.
    with open(filename, 'r') as file:
        lines = file.readlines()
    # replace param values with updated ones
    updated = set()
    for i, line in enumerate(lines):   # i is nice to track, for easy debugging later.
        match = re.fullmatch(r'(\s*)(\w+)(\s*)(=)(\s*)(.*?)(\s*;.*)?', line.rstrip('\n'))
        if match:
            s0, varname, s1, _eq_, s2, value, comment = match.groups()
            if varname in params:
                value = str(params[varname])
                lines[i] = f"{s0}{varname}{s1}={s2}{value}{comment or ''}\n"
                updated.add(varname)
    if not missing_ok:
        missing = set(params.keys()) - updated
        if missing:
            raise FileContentsMissingError(f"missing params in file: {missing!r}")
    result = ''.join(lines)   # each line already ends with '\n' by default.
    if dst is not None:
        with open(dst, 'w') as file:
            file.write(result)
        return dst
    else:
        return result


### --------------------- parse params from python-like file --------------------- ###

def read_python_params_file(filename, *, eval=True, as_tuples=False):
    '''parse python file of params into a python dictionary of params.
    (only eval occurs via ast.literal_eval; does not evaluate arbitrary code.)

    filename: string
        file to read from.
    eval: bool, default True
        whether to attempt to evaluate the values,
        using ast.literal_eval (safer but less flexible than eval).
        if True, try to evaluate values but use strings if evaluation fails.
        if False, values will remain as strings.
    as_tuples: bool, default False
        if True, return list of tuples instead of dictionary.
        list of tuples guaranteed to appear in the same order as in the params file.

    File formatting notes:
        - hashtags (#) are used for comments. (python format)
        - ignore blank lines & lines that don't assign a variable (missing '=')
        - ignores all leading & trailing whitespace in vars & values.
    '''
    filename = os.path.abspath(filename)  # <-- makes error messages more verbose, if crash later.
    # read the file lines.
    with open(filename, 'r') as file:
        lines = file.readlines()
    # remove comments
    lines = [line.split("#",1)[0] for line in lines]
    # trim whitespace
    lines = [line.strip() for line in lines]
    # remove empty lines, and remove lines without an equal sign.
    lines = [line for line in lines if line!='' and ('=' in line)]
    # split lines into vars & values
    var_value_pairs = [line.split("=",1) for line in lines]
    # cleanup whitespace in vars & values
    var_value_pairs = [(var.strip(), value.strip()) for (var, value) in var_value_pairs]

    if eval:
        var_value_pairs = [(var, attempt_literal_eval(value)) for (var, value) in var_value_pairs]

    return var_value_pairs if as_tuples else dict(var_value_pairs)
