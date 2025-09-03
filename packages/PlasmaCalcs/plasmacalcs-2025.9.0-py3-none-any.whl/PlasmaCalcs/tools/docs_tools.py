"""
File Purpose: tools related to documentation, e.g. docstrings
"""
import re
import types

from ..defaults import DEFAULTS

def format_docstring(*args__format, sub_indent=None, sub_ntab=None, **kw__format):
    '''returns a decorator of f which returns f, after updating f.__doc__ via f.__doc__.format(...)
    sub_indent: None or str
        if provided, indent all lines (after the first line) for each multiline string, before formatting.
    sub_ntab: int
        if provided when sub_indent is None, use sub_indent = sub_ntab * DEFAULTS.TAB.
    '''
    if sub_indent is None and sub_ntab is not None:
        sub_indent = DEFAULTS.TAB * sub_ntab
    if sub_indent is not None:
        args__format = [str(arg).replace('\n', '\n'+sub_indent) for arg in args__format]
        kw__format = {key: str(val).replace('\n', '\n'+sub_indent) for key, val in kw__format.items()}
    def return_f_after_formatting_docstring(f):
        f.__doc__ = f.__doc__.format(*args__format, **kw__format)
        return f
    return return_f_after_formatting_docstring

def docstring_but_strip_examples(f, *, strip_returns=True):
    r'''return f.__doc__ but removing all lines after "Examples\n", if present.
    strip_returns: bool
        if True, also remove all lines after "Returns\n", if present.
    '''
    doc = f.__doc__
    if doc is None:
        return doc
    if 'Examples\n' in doc:
        doc = doc.split('Examples\n')[0].rstrip()
    if 'Returns\n' in doc:
        doc = doc.split('Returns\n')[0].rstrip()
    return doc


class DocstringInfo():
    r'''info about a docstring. Also, helpful methods for converting to sphinx format.

    docstring: str
        the original docstring. Stored at self.docstring, and never changed.
    kind: None, 'sphinx', or 'custom'
        what kind of docstring this is.
        None --> infer from docstring.
                'sphinx' if any line matches the KNOWN_SPHINX_PATTERN, else 'custom'.
                (e.g. if there's a :param...: line, then it's 'sphinx'.)
        'sphinx' --> docstring assumed to already follow all sphinx standards.
        'custom' --> docstring assumed to not follow sphinx standards. (See below)


    "Custom" format is used throughout most of PlasmaCalcs. Details:
        - first line is a description of the object. Never a param or other special line.
        - subsequent lines might continue the description.
        - line breaks are intended to be maintained when generating docs pages.
        - some lines tell params but don't specify :param:. Example:
            word: description with any number of words
        - after a param line, subsequent indented lines are a description of that param,
            until indentation level reverts back to same level as param line. Example:
            myparam1: description of myparam1
                continues description of myparam1

                also part of description of myparam1
            no longer part of description (might be a different param, or something else).
        - param "word" could instead be comma-separated words, but nothing fancier.
            E.g. "x, y: value" is treated as params, but "x space: value" is not.
            "Word" is defined to be a sequence of characters matching regex: \w
            Also, these can never be single-word params (case-insensitive)
                'Example', 'Examples', 'Return', 'Returns', 'Equivalent',

        - currently, no other fancy-formatting is recognized.
            - (this might be updated eventually)
        - some patterns will be replaced:
            * --> \*       # to avoid sphinx interpreting as "emphasis"
            ** --> \*\*    # to avoid sphinx interpreting as "strong emphasis"
            *** --> *      # (use 3 asterisks instead of 1, to emphasize something)
            **** --> **    # (use 4 asterisks instead of 2, to strongly emphasize something)
            |x| --> \|x|   # to avoid sphinx interpreting as "substitution".
            `x` --> ``x``  # to tell sphinx to interpret as "code"
            word_ --> word\_  # avoid sphinx thinking word is a reference to something.
    If you don't like all the details of "custom" format, you can just use sphinx format.
    '''
    KNOWN_SPHINX_PATTERN = r'\s*(:param|:type|:return|:rtype|:raise).*:.*'
    NEVER_PARAMS = ('example', 'examples', 'return', 'returns', 'equivalent')  # case-insensitive
    PARAM_PATTERN = r'\s*((?!(?i)(?:' + '|'.join(NEVER_PARAMS) + r')s?)[\w]+(?:,\s*[\w]+)*)\s*:\s*(.+)'

    def __init__(self, docstring, *, kind=None):
        self.docstring = docstring  # original docstring, will never be changed
        self.lines = docstring.splitlines()
        self.kind = self._infer_kind(kind)
        # remove trailing blank lines.
        for i, l in enumerate(self.lines[::-1]):
            if not self.is_blank_line(l):
                break
        last_nonblank_line = len(self.lines) - i
        self.lines = self.lines[:last_nonblank_line]
        self.base_indent = self._infer_base_indent()

    def _infer_kind(self, kind):
        if kind is not None:
            return kind
        if any(re.fullmatch(self.KNOWN_SPHINX_PATTERN, l) for l in self.lines):
            return 'sphinx'
        else:
            return 'custom'

    def _infer_base_indent(self):
        '''return minimum indent across all lines except the first.
        if only nonblank line is the first line, return 0.
        '''
        result = None
        for l in self.lines[1:]:
            if not self.is_blank_line(l):
                indent = self.get_indent_n(l)
                if (result is None) or (indent < result):
                    result = indent
        if result is None:  # all nonblank lines have 0 indent
            result = 0
        return result

    @classmethod
    def from_obj(cls, obj):
        '''return DocstringInfo(obj.__doc__)'''
        return cls(obj.__doc__)

    @staticmethod
    def is_blank_line(line):
        '''returns whether this line is blank.'''
        return len(line.strip()) == 0

    @staticmethod
    def get_indent_n(line):
        '''returns number of leading spaces in line.'''
        return len(line) - len(line.lstrip())

    def nonblank_line_here_or_next(self, i):
        '''return self.lines[i] if nonblank, else first nonblank line after i.'''
        for j in range(i, len(self.lines)):
            if not self.is_blank_line(self.lines[j]):
                return self.lines[j]
        assert False, f'no nonblank lines at {i} or after'

    def param_ilines(self):
        '''return dict of {i: [iline of all description lines]} for param lines in docstring.
        param lines are those which match self.PARAM_PATTERN,
            AND are not indented underneath an existing param line.
            (also, line 0 is NEVER a param line, no matter what.)

        line number) example line:
        0) Example docstring
        1) param1: is a param line
        2)     description line
        3) param2: is another param line
        4)    description line
        5)        another description line
        6)    param 3: still not a param line (too indented)
        7) param4: param line again
        8) back to non-param line
        9)
        10) param5: param line again
        11)     description line again
        12) going to talk about a subset of parameters now:
        13)     subparam1: param line
        14)         description line
        15)     subparam2: param line
        16) 
        17) still non-paramline

        --> result would be:
            {1: [2], 3: [4, 5, 6], 7: [], 10: [11], 13: [14], 15: []}
        '''
        result = {}
        current_indent_n = None
        current_iparam = None
        for i, l in enumerate(self.lines):
            if i == 0:
                continue
            # check if sub-indented below a param_line.
            if current_indent_n is None:
                maybe_param_line = True
            else:  # currently considering maybe description lines.
                nonblank_l = self.nonblank_line_here_or_next(i)
                indent_n = self.get_indent_n(nonblank_l)
                if indent_n > current_indent_n:  # description line
                    maybe_param_line = False
                    result[current_iparam].append(i)
                else:  # no longer a description line
                    current_indent_n = None
                    current_iparam = None
                    maybe_param_line = True
            if maybe_param_line and re.fullmatch(self.PARAM_PATTERN, l):
                current_indent_n = self.get_indent_n(l)
                current_iparam = i
                result[i] = []
        return result

    def line_infos(self):
        '''return (i, linetype, indent_n, line_post_indent) for each line in docstring.

        i is line index.
        linetype is 'text', 'empty', 'param', or 'pdesc'.
            'text' --> misc text (not associated with a param)
            'empty' --> empty line
            'param' --> param line
            'pdesc' --> description line for param
        indent_n is number of spaces before text in line,
            used for prepending '| ' to ensure manual line breaks are respected in sphinx format.
            For blank lines, this is the indent_n of the next nonblank line.
            For text lines, this is the minimum indent across all lines (except the first line).
            For pdesc lines, this is the sub-indent level of the first desc line;
                subsequent desc lines have the same indent_n.
                (This makes the sphinx docs maintain the sub-indentation level as well!)
        line is all the text in the line after removing `indent_n` spaces.
        '''
        result = []
        param_ilines = self.param_ilines()
        current_indent_n = None
        i = 0
        result.append((i, 'text', 0, self.lines[i]))
        i = 1
        while i < len(self.lines):
            l = self.lines[i]
            if self.is_blank_line(l):
                nonblank_l = self.nonblank_line_here_or_next(i)
                indent_n = self.get_indent_n(nonblank_l)
                result.append((i, 'empty', indent_n, ''))
                i = i + 1
            elif i in param_ilines:
                current_indent_n = self.get_indent_n(l)
                result.append((i, 'param', current_indent_n, l[current_indent_n:]))
                if len(param_ilines[i]) >= 1:
                    desc0 = param_ilines[i][0]
                    desc0_nonblank = self.nonblank_line_here_or_next(desc0)
                    subindent_n = self.get_indent_n(desc0_nonblank)
                    for j in param_ilines[i]:
                        linej = self.lines[j]
                        if self.is_blank_line(linej):
                            result.append((j, 'pdesc', subindent_n, ''))
                        else:
                            result.append((j, 'pdesc', subindent_n, linej[subindent_n:]))
                    i = i + len(param_ilines[i])
                i = i + 1
            else:
                result.append((i, 'text', self.base_indent, l[self.base_indent:]))
                i = i + 1
        return result

    def _reconstruct(self):
        '''reconstruct docstring from self.line_infos().
        Mainly for debugging purposes.
        [TODO] result has extra (or not enough?) whitespace compared to docstring,
            but only differs in blank lines, so not a big deal.
        '''
        result = []
        for i, linetype, indent_n, line in self.line_infos():
            if linetype == 'empty':
                result.append('')
            elif linetype == 'text':
                result.append(' '*indent_n + line)
            elif linetype == 'param':
                result.append(' '*indent_n + line)
            elif linetype == 'pdesc':
                result.append(' '*indent_n + line)
            else:
                raise ValueError(f'unknown linetype: {linetype}')
        return '\n'.join(result)

    def to_sphinx(self):
        r'''returns self.docstring, converted to sphinx format.
        See help(type(self)) for more details.

        Equivalent: '\n'.join(self.to_sphinx_lines())
        '''
        return '\n'.join(self.to_sphinx_lines())
        
    def to_sphinx_lines(self):
        r'''returns lines of self.docstring, converted to sphinx format.
        See help(type(self)) for more details.

        Equivalent: self.to_sphinx().split('\n')
        '''
        if self.kind == 'sphinx':
            return self.lines
        elif self.kind == 'custom':
            return self._custom_to_sphinx_lines()
        else:
            raise ValueError(f'unknown kind: {self.kind}')

    def _custom_to_sphinx_lines(self):
        '''convert custom docstring to sphinx format.
        assumes but does not check self.kind=='custom'.
        '''
        result = []
        prev_linetype = None
        first_text_block = True
        for i, linetype, indent_n, line in self.line_infos():
            ## GENERIC SPHINX RULES ##
            # avoid sphinx being confused about asterisks in docstrings, e.g. *args or **kwargs:
            # * --> \*
            line = re.sub(r'(?<![*])[*](?![*])', r'\\*', line)
            # ** --> \*\*
            line = re.sub(r'(?<![*])[*]{2}(?![*])', r'\\*\\*', line)
            # *** --> *
            line = re.sub(r'[*]{3}', '*', line)
            # **** --> **
            line = re.sub(r'[*]{4}', '**', line)
            # avoid sphinx interpreting line as "substitution"
            # |x| --> \|x|
            line = re.sub(r'[|]([^|]+)[|]', r'\|\g<1>|', line)
            # tell sphinx to interpret `x` as "code" (i.e. ``x``)
            # `x` --> ``x``
            line = re.sub(r'`([^`]+)`', r'``\g<1>``', line)
            # tell sphinx that trailing underscores aren't intended to be references.
            # word_ --> word\_
            line = re.sub(r'\b(\w+)_\b', r'\1\\_', line)
            ## HANDLING INDENTATIONS AND LINETYPES ##
            if linetype == 'empty':
                result.append('')
            elif linetype == 'text':
                if first_text_block and prev_linetype in (None, 'empty'):  # first text line ever
                    result.append(line)
                elif first_text_block:  # next text lines
                    result.append('')  # need an extra blank line between first and second lines,
                    # (if second line is text continuation of first. This tells sphinx to respect our newlines,
                    #  while also allowing it to recognize the first line as the one-line summary.)
                    result.append(' '*indent_n + '| ' + line)
                    first_text_block = False   # resume "normal" line processing.
                elif prev_linetype in ('param', 'pdesc'):  # text lines after describing param(s).
                    result.append('')  # sphinx needs an extra blank line.
                    # (prevents "WARNING: Block quote ends without a blank line; unexpected unindent.")
                    result.append(' '*indent_n + '| ' + line)
                else:  # any other text lines
                    result.append(' '*indent_n + '| ' + line)
            elif linetype == 'param':
                # sphinx sometimes needs extra blank line between text & param
                # to render param appropriately.
                # (noticed this issue in particular when param indent > text indent.)
                if prev_linetype in ('text', 'pdesc'):
                    result.append('')
                result.append(' '*indent_n + line)
                first_text_block = False
            elif linetype == 'pdesc':
                result.append(' '*indent_n + '| ' + line)
                first_text_block = False
            else:
                raise ValueError(f'unknown linetype: {linetype}')
            prev_linetype = linetype
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        l = self.nonblank_line_here_or_next(0)  # first nonblank line
        if len(self.lines) > 1:
            l = l + '...'
        if len(l) > 60:
            l = l[:60] + '...'
        return f'{type(self).__name__}({l})'


def sphinx_docstring(f):
    '''return sphinx docstring for this object.
    None if f.__doc__ is None or doesn't exist.
    Else, DocstringInfo(f.__doc__).to_sphinx()
    '''
    if getattr(f, '__doc__', None) is None:
        return None
    else:
        return DocstringInfo(f.__doc__).to_sphinx()

def list_objs(root, types_=(types.ModuleType, types.FunctionType, types.MethodType, type),
              *, recurse_on=(types.ModuleType, type), module_root=None, _seen=None):
    '''return list of all objects in root that are instances of any of types.

    root: where to start the search.
        result will only contain objects defined in root or sub-modules.
        (e.g. don't list numpy objects just because numpy was imported...)
    types_: tuple of types to check
        only list objects which are instances of any of these types.
        (trailing underscore avoids ambiguity with the `types` module.)
        All types here must have __module__ telling module name where they were defined,
            or __name__ if subclass of types.ModuleType.
    recurse_on: type of types
        for every obj which is an instance of recurse_on, also list_objs from that obj.
    module_root: None, str, or module
        only list objects defined in this module or sub-modules. E.g., 'PlasmaCalcs.tools'.
        None --> use root.__name__ (if root is module, else root.__module__
    _seen: internal parameter used for recursion;
        tracks which object ids have already been seen,
        to ensure each obj appears in result at most 1 time.

    Examples:
        import PlasmaCalcs as pc
        # list all modules, functions, methods, and classes in PlasmaCalcs
        ll = pc.list_objs(pc)
        # check that to_sphinx() works properly for all such objs in PlasmaCalcs
        for obj in ll:
            if obj.__doc__ is not None:
                pc.DocstringInfo(obj.__doc__).to_sphinx()
    '''
    seen = {} if _seen is None else _seen
    if module_root is None:
        module_root = root.__name__ if isinstance(root, types.ModuleType) else root.__module__
    for name in dir(root):
        obj = getattr(root, name, None)
        if id(obj) in seen:
            continue
        if isinstance(obj, types_):
            module_name = obj.__name__ if isinstance(obj, types.ModuleType) else obj.__module__
            if not module_name.startswith(module_root):
                continue
            seen[id(obj)] = obj
        if isinstance(obj, recurse_on):
            _list_here = list_objs(obj, types_=types_, recurse_on=recurse_on, # noqa: F841  #<comment for linter
                                    module_root=module_root, _seen=seen)
            # ^^ seen already tracks the result! _list_here saved for debugging purposes.
    return list(seen.values())
