"""
File Purpose: tools whose main purpose is to work with implementation details of Python.

E.g. manipulate function docstrings
"""
import inspect
import string
import textwrap
import pydoc
import IPython  # for display

from .docs_tools import format_docstring


def printsource(obj, *, module=True, as_str=False):
    '''prints source code for object (e.g. call this on a function or class).
    module: bool
        whether to also tell module & type info about this object.
    as_str: bool
        if True, return result as a string instead of printing it.
    '''
    result = ''
    if module:
        if inspect.ismodule(obj):
            topline = f'module {obj.__name__}'
        else:
            mod = inspect.getmodule(obj)
            if mod is None:
                raise TypeError(f'inspect.getmodule(obj) is None, for obj with type={type(obj)}')
            else:
                mod = mod.__name__
            topline = f'{type(obj).__name__} {obj.__name__!r} from module {mod}'
        buffer = '-' * len(topline)  # line like "--------" of length len(topline)
        result += '# ' + topline + '\n'
        result += '# ' + buffer + '\n'
    result += str(inspect.getsource(obj))
    if as_str:
        return result
    else:
        print(result)

def displaysource(obj, *, module=True):
    '''display sourcecode for obj, including syntax highlighting. See also: printsource.
    module: bool
        whether to also tell module & type info about this object.
    '''
    source = printsource(obj, module=module, as_str=True)
    IPython.display.display(IPython.display.Code(source, language='python'))

def is_iterable(obj):
    '''returns whether obj is iterable. For super fast code, copy-paste instead of calling this function.'''
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True

def inputs_as_dict(callable_, *args, **kw):
    '''returns dict of all inputs to callable_ based on its signature and args & kwargs.
    raises TypeError if inputs would be invalid for callable_.
    Example:
        def foo(a, b=2, c=3, * d=4, e=5): pass
        inputs_as_dict(foo, 9, d=7, c=8) gives {'a':9, 'b':2, 'c':8, 'd':7, 'e':5}
        inputs_as_dict(foo, z=6) raises TypeError since foo doesn't accept kwarg 'z'.
    '''
    _iad_for_callable = _inputs_as_dict__maker(callable_)
    return _iad_for_callable(*args, **kw)

def _inputs_as_dict__maker(callable_):
    '''returns a function which returns dict of all inputs all inputs to callable_.'''
    f_signature = inspect.signature(callable_)
    def _inputs_as_dict(*args, **kw):
        '''returns dict of inputs as they would be named inside callable_'s namespace.
        includes params not input directly here, but defined by default for callable_.
        '''
        bound_args = f_signature.bind(*args, **kw)  # << will raise TypeError if inputs invalid for f.
        bound_args.apply_defaults()  # << include defaults
        params_now = bound_args.arguments  # << dict of {input name: value}.
        return params_now
    return _inputs_as_dict

def value_from_aliases(*aliaslist, **aliasdict):
    '''returns the single provided value from aliases.
    raises InputMissingError if all values are None.
    raises InputConflictError if values are not None and not the same (compared via 'is').
    '''
    found = False
    aliases = [*aliaslist, *aliasdict.values()]
    for a in aliases:
        if a is not None:
            if found and (value is not a):
                errmsg = f'Found multiple non-None values: args={aliaslist}, kwargs={aliasdict}'
                raise InputConflictError(errmsg)
            else:
                found = True
                value = a
    if not found:
        errmsg = f'Found no non-None values: args={aliaslist}, kwargs={aliasdict}'
        raise InputMissingError(errmsg)
    return value


_help_str_paramdocs = {
    'module': '''module: bool
        whether to include line with module name in help string.
        e.g. "function help_str in module PlasmaCalcs.tools.pytools"''',
    'blankline': '''blankline: bool
        whether to include blank line between module and signature.
        only considered if module=True AND signature=True.''',
    'signature': '''signature: bool
        whether to include line with signature in help string.
        e.g. "help_str(f, *, module=True, signature=True, indent=None)"''',
    'doc': '''doc: bool
        whether to include lines with docstring in help string.
        e.g. "return str for help(f)." ... and all the other docs in here.''',
    'indent': '''indent: str
        indent all lines in the result by this string.
        equivalent to textwrap.indent(result, indent).''',
}

@format_docstring(**_help_str_paramdocs)
def help_str(f, *, module=True, blankline=True, signature=True, doc=True, indent=''):
    '''return str for help(f).
    {module}
    {blankline}
    {signature}
    {doc}
    {indent}
    '''
    help0 = pydoc.render_doc(f, '%s', renderer=pydoc.plaintext)  # matches help(f)
    if module and blankline and signature and doc:  # including all parts of help0; no need to parse.
        return textwrap.indent(help0, indent)
    # otherwise, we need to parse help0 and remove some lines.
    lines = help0.splitlines()
    mod_lines = lines[0:1]  # line 0 is module name; line 1 is blank
    sig_lines = lines[2:3]  # line 2 is signature
    doc_lines = lines[3:]   # all remaining lines
    result_lines = []
    if module: result_lines.extend(mod_lines)
    if blankline and module and signature: result_lines.append('')
    if signature: result_lines.extend(sig_lines)
    if doc: result_lines.extend(doc_lines)
    result = '\n'.join(result_lines)
    result = textwrap.indent(result, indent)
    return result

def print_help_str(f, **kw_help_str):
    '''print help_str(f, **kw_help_str).'''
    print(help_str(f, **kw_help_str))

def indent_doclines(s, indent=' '*4):
    '''return string s, prepending all lines except line 0 with indent'''
    lines = s.splitlines()
    lines[1:] = [indent + line for line in lines[1:]]
    return '\n'.join(lines)

def indent_paramdocs(d, indent=' '*4):
    '''return dict but with indent_doclines called on all the values.'''
    return {key: indent_doclines(value, indent) for key, value in d.items()}


### --------------------- String formatting --------------------- ###

def pad_missing_format_keys(s, keys):
    '''return s (a format string) with all missing keys padded with extra {}.
    E.g. ('{present} and {missing}', ['present']) --> '{present} and {{missing}}'

    keys: iterable of keys. (dict is also acceptable.)
    '''
    formatter = string.Formatter()
    result = ''
    for literal_text, field_name, format_spec, conversion in formatter.parse(s):
        result += literal_text
        if field_name is not None:
            field_content = '{' + field_name
            if conversion is not None:
                field_content += '!' + conversion
            if format_spec is not None:
                field_content += ':' + format_spec
            field_content += '}'
            if field_name not in keys:
                field_content = '{' + field_content + '}'
            result += field_content
    return result

def format_except_missing(s, **kw):
    '''return s.format(**kw) but ignoring any missing keys.'''
    s = pad_missing_format_keys(s, kw.keys())
    return s.format(**kw)

def replace_missing_format_keys(s, keys, replacement):
    '''return s (a format string) with all missing keys replaced by replacement.
    E.g. ('{present} and {missing}', ['present'], 'MISSING') --> 'present and MISSING'

    keys: iterable of keys. (dict is also acceptable.)
    '''
    formatter = string.Formatter()
    result = ''
    for literal_text, field_name, format_spec, conversion in formatter.parse(s):
        result += literal_text
        if field_name is not None:
            field_content = '{' + field_name
            if conversion is not None:
                field_content += '!' + conversion
            if format_spec is not None:
                field_content += ':' + format_spec
            field_content += '}'
            if field_name not in keys:
                field_content = replacement
            result += field_content
    return result

def format_replace_missing(s, replacement, **kw):
    '''return s.format(**kw) but replace any missing keys with replacement.
    E.g. ('{present} and {missing}', 'MISSING', present='yes') --> 'yes and MISSING'
    '''
    s = replace_missing_format_keys(s, kw.keys(), replacement)
    return s.format(**kw)
