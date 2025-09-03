"""
File Purpose: QuantityLoader.help()

defines QuantityLoader.help() which helps with loading quantities,
particularly with learning which quantities are available to be loaded.
"""
import builtins
import textwrap

from .quantity_loader import QuantityLoader
from .quantity_tools import Pattern
from ..defaults import DEFAULTS
from ..errors import FormulaMissingError, InputError
from ..tools import (
    format_docstring, indent_paramdocs,
    help_str, _help_str_paramdocs,
    UNSET,
    Binding,
)
binding = Binding(locals())


with binding.to(QuantityLoader):
    QuantityLoader.__doc__ += '''\n    For help with loading quantities, see QuantityLoader.help()\n'''

    _help_quants_str_paramdocs = {
        **indent_paramdocs(_help_str_paramdocs),
        'qstr': '''None or str
            None --> tells info about this class & how to use this function.
                    in particular, tells that quants are stored cls.KNOWN_VARS and cls.KNOWN_PATTERNS,
                    and describes behavior of calling help with a string.
            str --> return str for help with all quants related to str.
                    use empty str to get help for all quants.''',
        'only': '''None or str
            If provided, only get help for a subset of relevant quantities.
            None --> get help with all quantities related to qstr.
            'VARS' --> only get help with KNOWN_VARS.
            'PATTERNS' --> only get help with KNOWN_PATTERNS.
            'TREE' --> only get help with quantities in cls.cls_var_tree(str).
            'EXACT' --> only get help for the KNOWN_VAR exactly matching qstr.
            if provided when qstr is None, treat qstr as '' instead.''',
        'dense': '''bool
            Whether to reduce whitespace in result.
            E.g. True --> no newlines between functions. False --> one newline between functions.''',
        'modules': '''bool
            Whether to include modules in result.
            If True, result will be grouped into sections with modules written at top.''',
        'tree': '''None or bool
            How much help to give for quantities in cls.cls_var_tree(qstr).
            False --> don't even check cls.cls_var_tree(qstr).
            True --> help for all quantities in cls.cls_var_tree.
            None --> help for quantities in cls.cls_var_tree(qstr).flat_branches_until_vars()
                    i.e. patterns & vars in tree but ignore any nodes with LoadableVar ancestors.
                    e.g. qstr='mean_mod_beta' --> help with 'mean_(.+)', 'mod_(.+)', and 'beta',
                        but no help with dependencies of 'beta' ('q', 'mod_B', 'm').''',
        'print': '''bool
            whether to print the result. If False, return the result instead of printing.''',
    }
    QuantityLoader._help_quants_str_paramdocs = _help_quants_str_paramdocs

    @binding.bind(methodtype=classmethod)
    def _help_matches(cls, qstr, k, v):
        '''returns whether qstr matches k or v, and thus should be displayed during self.help(qstr).

        qstr: str
            the str to match; from self.help(qstr)
        k: varname
            the varname to test for matches.
            key from self.KNOWN_VARS.keys(), or key.str from self.KNOWN_PATTERNS.keys().
        v: LoadableQuantity
            the LoadableQuantity to test for matches.
            value from self.KNOWN_VARS.values() or self.KNOWN_PATTERNS.values().

        matches if any of these are true:
            qstr == ''
            qstr in k.split('_')         # size limitation and split('_') because, e.g. during help('n'),
            len(qstr)>=3 and qstr in k   #    want vars related to number density, not all vars with the letter 'n'.
            qstr in module.split('.')   (where, module == v.get_f_module(cls))
            '.' in qstr and qstr in module
            len(qstr)>=3 and qstr in value from module.split('.')
            len(qstr)>=3 and qstr in v.fname
            re.fullmatch(k, qstr)  # if k is a Pattern
        otherwise, does not match.
        '''
        if qstr == '': return True
        if qstr in k.split('_'): return True
        if len(qstr)>=3 and qstr in k: return True
        module = v.get_f_module(cls)
        if qstr in module.split('.'): return True
        if '.' in qstr and qstr in module: return True
        if len(qstr)>=3 and any(qstr in val for val in module.split('.')): return True
        if len(qstr)>=3 and qstr in v.fname: return True
        if isinstance(k, Pattern) and k.fullmatch(qstr): return True
        return False

    @binding.bind(methodtype=classmethod)
    @format_docstring(**_help_quants_str_paramdocs)
    def help_quants_str(cls, qstr=None, only=None, *, tree=None, modules=True, signature=False, doc=True, dense=False,
                        _instance=None):
        '''returns str for help with quants.

        qstr: {qstr}
        only: {only}
        tree: {tree}
        modules: {modules}
        signature: {signature}
        doc: {doc}
        dense: {dense}
        _instance: None or QuantityLoader instance
            if provided, use _instance.match_var_tree() instead of cls.cls_var_tree().
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        TAB = ' '*4
        if only is not None:
            only = only.upper()  # case-insensitive
            if only not in ('VARS', 'PATTERNS', 'TREE', 'EXACT'):
                raise InputError(f'only={only!r} not recognized; expected "VARS", "PATTERNS", or "TREE".')
            if qstr is None:
                qstr = ''   # treat qstr as '' when qstr=None but only is not None.
        if qstr is None:
            helpstr = f'''\
            - obj('qname') or obj.get('qname') --> get the value of quantity qname.

            - obj.help(str) shows help for all related quantities:
                - obj.help('') --> help with all available quantities.
                - obj.help(str) --> get help with all quantities related to that str:
                    - quantities containing str
                    - quantities from module with name matching str

                - obj.help(str, 'VARS') --> help with only KNOWN_VARS.
                - obj.help(str, 'PATTERNS') --> help with only KNOWN_PATTERNS.
                - obj.help(str, 'TREE') --> only show help for quantities in match_var_tree(str).
                - obj.help(str, ..., tree=True) --> include help for ALL quantities in match_var_tree(str),
                    instead of ignoring tree nodes which have any LoadableVar ancestors.

                - obj.help(str, ..., modules=True) --> include module info in the output;
                    this helps with understanding where the code for each quantity is defined.

            - {cls.__name__}.cls_help(str) works similarly, but:
                - doesn't require creating an instance of {cls.__name__} to get help.
                - will fail for quants which depend on present values of a {cls.__name__} instance.
                    e.g. {cls.__name__}.cls_help('nusj') fails if collision type depends on obj.fluid.

            - {cls.__name__}.KNOWN_VARS and .KNOWN_PATTERNS store all available quantities.
            - obj.behavior tells all attributes of {cls.__name__} which may affect results.
            - obj.help_call_options() tells all optional kw during obj('qname', **kw).

            - obj.match_var_tree('qname') shows how quantity qname will actually be loaded,
                including any quantities which qname depends on, and any which those depend on, etc.'''
            return textwrap.dedent(helpstr)
        # else:  qstr is a str. find matches
        tree_flag = tree
        if (only in (None, 'TREE')) and (tree_flag or (tree_flag is None)):
            try:
                if _instance is None:
                    tree = cls.cls_var_tree(qstr)
                else:
                    tree = _instance.match_var_tree(qstr)
            except FormulaMissingError:
                tree_loadables = []
            else:
                if tree_flag:
                    tree_loadables = [leaf.obj.loadable for leaf in tree.flat(include_self=True)]
                else:
                    tree_loadables = [leaf.obj.loadable for leaf in tree.flat_branches_until_vars(include_self=True)]
        else:
            tree_loadables = []

        vars_match = {}
        if only in (None, 'VARS'):  # add any VARS matches
            vars_match = {k:v for k,v in cls.KNOWN_VARS.items() if cls._help_matches(qstr, k, v)}
        if only in (None, 'TREE'):  # add any TREE matches
            vars_match = {**vars_match, **{k:v for k,v in cls.KNOWN_VARS.items() if v in tree_loadables}}
        if only == 'EXACT':
            vars_match = {k:v for k,v in cls.KNOWN_VARS.items() if (k == qstr)}

        pats_match = {}
        if only in (None, 'PATTERNS'):  # add any PATTERNS matches
            pats_match = {k:v for k,v in cls.KNOWN_PATTERNS.items() if cls._help_matches(qstr, k.str, v)}
        if only in (None, 'TREE'):  # add any TREE matches
            pats_match = {**pats_match, **{k:v for k,v in cls.KNOWN_PATTERNS.items() if v in tree_loadables}}

        if len(vars_match) == 0 and len(pats_match) == 0:
            return f'No quantities containing string: {qstr!r}'
        multiple_vars_match = (len(vars_match) > 1)
        multiple_pats_match = (len(pats_match) > 1)
        showing_vars_and_pats = (len(vars_match) > 0) and (len(pats_match) > 0)

        # include summary of all matches at top
        result = ''
        if showing_vars_and_pats or multiple_vars_match:
            result += f'Showing help for related KNOWN_VARS: {list(vars_match.keys())}\n'
            if not dense: result += '\n'
        if showing_vars_and_pats or multiple_pats_match:
            result += f'Showing help for related KNOWN_PATTERNS: {[key.str for key in pats_match.keys()]}\n'
            if not dense: result += '\n'

        # group vars & pattern matches by module
        if modules:
            vars_match_by_mod = dict()
            pats_match_by_mod = dict()
            for k, v in vars_match.items():
                mod = v.get_f_module(cls)
                vars_match_by_mod.setdefault(mod, dict())[k] = v
            for k, v in pats_match.items():
                mod = v.get_f_module(cls)
                pats_match_by_mod.setdefault(mod, dict())[k] = v
        else:
            vars_match_by_mod = {0: vars_match}
            pats_match_by_mod = {0: pats_match}

        # KNOWN_VARS
        if len(vars_match) > 0:
            if showing_vars_and_pats: result += f'\nKNOWN_VARS:\n'
            result_vars = ''
            for mod, vars_match in vars_match_by_mod.items():
                if modules:
                    if not dense: result_vars += '\n'
                    result_vars += f'in module {mod}:\n'
                result_mod = ''
                for k, v in vars_match.items():
                    if signature:   # put "key  : signature" as first line.
                        result_mod += f'{k!r:7s}: '
                    elif doc:       # put "key:" as first line. (don't put doc info on first line.)
                        result_mod += f'{k!r}:\n'
                    if signature or doc:
                        result_mod += help_str(v.get_f(cls), module=False, signature=signature, doc=doc)
                        result_mod += '\n'
                        if not dense and not modules: result_mod += '\n'
                    else:  # no signature & no doc. Just a list of vars.
                        result_mod += f'{k!r}, '
                if modules:
                    result_mod = textwrap.indent(result_mod, TAB)
                    if (not signature) and (not doc): result_mod += '\n'
                result_vars += result_mod
            if showing_vars_and_pats: result_vars = textwrap.indent(result_vars, TAB)
            result += result_vars
            if showing_vars_and_pats and modules and not dense: result += '\n'

        # KNOWN_PATTERNS
        if len(pats_match) > 0:
            if showing_vars_and_pats: result += f'\nKNOWN_PATTERNS:\n'
            result_pats = ''
            for mod, pats_match in pats_match_by_mod.items():
                if modules:
                    if not dense: result_pats += '\n'
                    result_pats += f'in module {mod}:\n'
                result_mod = ''
                for k, v in pats_match.items():
                    if signature:   # put "key  : signature" as first line.
                        result_mod += f'{k.str!r:25s}: '
                    elif doc:       # put "key:" as first line. (don't put doc info on first line.)
                        result_mod += f'{k.str!r}:\n'
                    if signature or doc:
                        result_mod += help_str(v.get_f(cls), module=False, signature=signature, doc=doc)
                        result_mod += '\n'
                        if not dense and not modules: result_mod += '\n'
                    else:   # no signature & no doc. Just a list of patterns.
                        result_mod += f'{k.str!r}, '
                if modules:
                    result_mod = textwrap.indent(result_mod, TAB)
                    if (not signature) and (not doc): result_mod += '\n'
                result_pats += result_mod
            if showing_vars_and_pats: result_pats = textwrap.indent(result_pats, TAB)
            result += result_pats

        result = result.strip('\n')  # remove leading / trailing newlines
        return result

    @binding.bind(methodtype=classmethod)
    def help_str(cls, qstr=None, only=None, **kw):
        '''returns cls.help_quants_str(qstr=qstr, only=only, **kw).
        cls.help() calls help_str.
        subclasses might overwrite help_str, but probably won't touch help_quants_str.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        return cls.help_quants_str(qstr=qstr, only=only, **kw)
    
    @binding.bind(methodtype=classmethod)
    @format_docstring(**_help_quants_str_paramdocs)
    def cls_help(cls, qstr=None, only=None, *, tree=None, modules=False, signature=False,
                 doc=True, dense=False, print=True, **kw):
        '''prints str for help with quants. Fails for any quants which depend on present values of a cls instance.

        qstr: {qstr}
        only: {only}
        tree: {tree}
        modules: {modules}
        signature: {signature}
        doc: {doc}
        dense: {dense}
        print: {print}
        '''
        helpstr = cls.help_str(qstr=qstr, only=only, tree=tree,
                                modules=modules, signature=signature, doc=doc, dense=dense,
                                **kw)
        if print:
            builtins.print(helpstr)
        else:
            return helpstr

    @binding
    @format_docstring(**_help_quants_str_paramdocs)
    def help(self=UNSET, qstr=None, only=None, *, tree=None, modules=False, signature=False,
             doc=True, dense=False, print=True):
        '''prints str for help with quants.

        qstr: {qstr}
        only: {only}
        tree: {tree}
        modules: {modules}
        signature: {signature}
        doc: {doc}
        dense: {dense}
        '''
        if not isinstance(self, QuantityLoader):
            # user tried calling help as a classmethod. Raise helpful error message about it.
            errmsg = (f'Expected QuantityLoader self, got type(self)={type(self)}.\n'
                      'This might occur if you called cls.help, instead of obj.help.\n'
                      'Use cls.cls_help() instead of cls.help(), to try getting help from class.\n'
                      '  It should succeed for most vars, but fail for vars whose tree depends on present values.')
            raise InputError(errmsg)
        helpstr = self.help_str(qstr=qstr, only=only, tree=tree,
                                modules=modules, signature=signature, doc=doc, dense=dense,
                                _instance=self)
        if print:
            builtins.print(helpstr)
        else:
            return helpstr

    @binding
    def help_call_options(self, search=None):
        '''prints help for kw_call_options.
        if search is provided, only print help for keys containing search.
        '''
        # [TODO] option to return all this stuff as a string, instead of printing
        # [TODO] option to see docs for only some of the options, instead of all at once
        print('Showing self.help_call_options(): docs for keys from self.kw_call_options()')
        if search is not None: print(f'Only showing keys containing search={search!r}')
        print('---------------------------------------------------------------------------')
        for key in self.kw_call_options():
            if search is not None and search not in key:
                continue
            s = getattr(type(self), key, None)
            if s is None:
                print(f"'{key}': [no help found; this key is not an attribute of type(self)]")
            else:
                print(f"'{key}': {help_str(s, module=False).lstrip()}")
            print()
