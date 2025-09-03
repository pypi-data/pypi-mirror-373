"""
File Purpose: handling parenthesis in var names.
"""

from ..quantity_loader import QuantityLoader
from ...errors import QuantCalcError, InputError
from ...tools import BijectiveMemory, UNSET


class ParenthesisLoader(QuantityLoader):
    '''parenthesis.
    parenthesis_memory: BijectiveMemory (subclass of dict).
        {key: var} for all vars ever inside parentheses, across all instances of ParenthesisLoader.
        keys <--> var mapping is one-to-one during each Python session.
        parenthesis_memory.inverse provides the {var: key} mapping.
    '''
    # # # HELPERS # # #
    parenthesis_memory = BijectiveMemory()

    @classmethod
    def _parenthesis_converted_var(cls, before, here, after):
        '''returns the var after converting it from var like '{before}({here}){after}'.
        use same before & after, but use {i} instead of here.
        Looks like: f'{before}{{{key}}}{after}' where key=int, unique to this var.
        '''
        key = cls.parenthesis_memory.key(here)
        return before + '{' + str(key) + '}' + after  # '+' instead of f-string for code-readability with braces.

    def _braced_int_dep(self, _var, groups):
        '''returns the 'dep' associated with this var for _get_braced_int_from_parenthesis_memory'''
        i, = groups
        return self.parenthesis_memory[int(i)]  # if this key doesn't exist, made a coding error.

    def _parenthesis_dep(self, _var, groups):
        '''returns the 'dep' associated with this var for get_parenthesis.'''
        before, here, after = groups
        return self._parenthesis_converted_var(before, here, after)

    # # # GETTABLE PATTERNS # # #
    # '{before}({here}){after}', with no parenthesis inside {here}
    @known_pattern(r'(.*)[(]([^()]+)[)](.*)', deps=[_parenthesis_dep])
    def get_parenthesis(self, var, *, _match=None, **kw):
        '''parenthesis. '{prefix}({here}){suffix}', with no parenthesis inside {here}.
        Ensures that {here} is interpreted as a single expression. Useful when combining operations.

        E.g. 'sqrt_q/m', with no parenthesis, has an ambiguous interpretation.
            'sqrt_(q/m)' unambiguously refers to "sqrt(ratio between q and m)".
            '(sqrt_q)/m' unambiguously refers to "ratio between sqrt(q) and m".
            The no-parenthesis interpretation is subject to change without warning, in future code updates.
            (You can always check the interpretation that is being used, via self.match_var_tree(var))
        '''
        before, here, after = _match.groups()
        newvar = self._parenthesis_converted_var(before, here, after)  # e.g. mean_(u/n) --> mean_{0}
        return self(newvar, **kw)   # the braces will be evaluated later, during self.get_braced_int_from_parenthesis_memory.

    # '{i}' where i is an int.
    @known_pattern(r'[{](\d+)[}]', deps=[_braced_int_dep])
    def get_braced_int_from_parenthesis_memory(self, var, *, _match=None):
        '''{i} --> self(mem_var), where mem_var = self.parenthesis_memory_key_to_var[int(i)].'''
        i, = _match.groups()
        mem_var = self.parenthesis_memory[int(i)]
        return self(mem_var)

    # # # PICKLING # # #
    def __getstate__(self):
        '''return state for pickling. pickle default ignores class attr (parenthesis_memory) but we need it.'''
        if hasattr(super(), '__getstate__'):
            state = super().__getstate__()
        else:
            state = self.__dict__.copy()
        state['parenthesis_memory'] = self.parenthesis_memory
        return state

    def __setstate__(self, state):
        '''set state for pickling. pickle default ignores class attr (parenthesis_memory) but we need it.'''
        mem = state.pop('parenthesis_memory')
        if hasattr(super(), '__setstate__'):
            super().__setstate__(state)
        else:
            self.__dict__.update(state)
        self.parenthesis_memory.update(mem)
        # important: ensure that self.parenthesis_memory is the same as the class attr;
        #   i.e., didn't accidentally assign self.parenthesis_memory to a different object.
        #   this matters because some methods might assume self.parenthesis_memory is the class attr.
        #   (first attempt at __setstate__ code had this bug!)
        assert self.parenthesis_memory is type(self).parenthesis_memory, "setstate messed up! coding error."
