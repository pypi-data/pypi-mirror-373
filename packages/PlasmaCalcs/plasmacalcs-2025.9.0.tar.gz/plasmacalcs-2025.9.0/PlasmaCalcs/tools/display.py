"""
File Purpose: display / print objects
"""

import pydoc


### --------------------- simple repr --------------------- ###

def repr_simple(obj):
    '''return obj._repr_simple() if possible, else repr(obj)'''
    try:
        obj_repr_simple = obj._repr_simple
    except AttributeError:
        return repr(obj)
    else:
        return obj_repr_simple()


### --------------------- Misc. --------------------- ###

def print_clear(N=80):
    '''clears current printed line of up to N characters, and returns cursor to beginning of the line.
    debugging: make sure to use print(..., end=''), else your print statement will go to the next line.
    '''
    print('\r'+ ' '*N +'\r',end='')

def help_str(f):
    '''gets string from help(f)'''
    return pydoc.render_doc(f, '%s')


### --------------------- Pretty str formatting --------------------- ###

def join_strs_with_max_line_len(strs, sep=', ', max=80, *, key=len):
    '''join strs with sep, with max_line_len characters per line;
    if joining another str in the same line makes line too long, start new line instead.
    if sep ends with space and appears at end of line, rstrip() that line.

    max: int or None, default 80
        maximum length of line. None -> no maximum (equivalent to sep.join(strs)).
    key: callable, default len
        key(str) should return length associated with str.
    '''
    if max is None:
        return sep.join(strs)
    if len(strs)==0:
        return ''
    lines = []
    line = strs[0]  # line currently being built
    L = key(strs[0])  # length of line being built.
    for r in strs[1:]:
        rlen = key(r)
        len_if_added = L + len(sep) + rlen
        if (len_if_added <= max):  # r goes on this line.
            line = f'{line}{sep}{r}'
            L = len_if_added
        else:
            lines.append(f'{line}{sep.rstrip()}')
            line = r
            L = rlen
    # finalize last line
    lines.append(line)
    # join lines
    result = '\n'.join(lines)
    return result
    