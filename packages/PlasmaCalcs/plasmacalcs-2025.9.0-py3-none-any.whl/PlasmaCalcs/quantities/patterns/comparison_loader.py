"""
File Purpose: ComparisonLoader.
"""
# [TODO] add tests for the patterns here, similar to basic arithmetic tests,
#   to ensure order of operations behaves as expected.

from ..quantity_loader import QuantityLoader
from ...tools import (
    UNSET, simple_property,
    xarray_at_max_of, xarray_at_min_of,
)

class ComparisonLoader(QuantityLoader):
    '''comparison operations, e.g. ==, !=, >, <, >=, <=.
    Also, some tools for boolean arrays: 'not_{var}', '{var0}_or_{var1}', '{var0}_and_{var1}'.
    Also, 'where': self('var_where_condition') --> self('var').where(self('condition'))
    Also, 'at_max_of' and 'at_min_of', for convenient argmaxing.
    '''
    # Caution: the order of these functions matters!
    # Patterns are checked in the order that functions were defined.
    # E.g., define 'or' before 'and' --> 'A_or_B_and_C' becomes 'A' or 'B_and_C'.
    # The order of definitions here matches Python standard order:
    #   not_A_or_B <--> (not_A)_or_B
    #   not_A_and_B <--> (not_A)_and_B
    #   A_or_B_and_C <--> A_or_(B_and_C)
    #   A_and_B_or_C <--> (A_and_B)_or_C
    # Additionally, logic (or, and, not) defined before comparisons (e.g. ==, >, <),
    #   ensures that, e.g., 'A==B_and_C' is parsed as '(A==B)_and_C'.
    #   (NOT parsed as 'A==(B_and_C)'.)

    @known_pattern(r'not_(.+)', deps=[0])  # 'not_{var}'
    def get_logical_not(self, var, *, _match=None):
        '''logical not. not var. Equivalent: ~self(var)'''
        var, = _match.groups()
        return ~self(var)

    @known_pattern(r'(.+)_or_(.+)', deps=[0, 1])  # '{var0}_or_{var1}'
    def get_logical_or(self, var, *, _match=None):
        '''logical or. var0 or var1. Equivalent: self(var0) | self(var1)'''
        var0, var1 = _match.groups()
        return self(var0) | self(var1)

    @known_pattern(r'(.+)_and_(.+)', deps=[0, 1])  # '{var0}_and_{var1}'
    def get_logical_and(self, var, *, _match=None):
        '''logical and. var0 and var1. Equivalent: self(var0) & self(var1)'''
        var0, var1 = _match.groups()
        return self(var0) & self(var1)

    # # # VALUE COMPARISONS # # #
    @known_pattern(r'(.+)[=][=](.+)', deps=[0,1])  # '{var0}=={var1}'
    def get_compare_equals(self, var, *, _match=None):
        '''self('A==B') --> boolean array: self('A') == self('B')'''
        var0, var1 = _match.groups()
        return self(var0) == self(var1)

    @known_pattern(r'(.+)[!][=](.+)', deps=[0,1])  # '{var0}!={var1}'
    def get_compare_not_equals(self, var, *, _match=None):
        '''self('A!=B') --> boolean array: self('A') != self('B')'''
        var0, var1 = _match.groups()
        return self(var0) != self(var1)

    # note - must define >= before >, otherwise e.g. 'a>=b' --> 'a' > '=b'.
    @known_pattern(r'(.+)[>][=](.+)', deps=[0,1])  # '{var0}>={var1}'
    def get_compare_greater_than_or_equal(self, var, *, _match=None):
        '''self('A>=B') --> boolean array: self('A') >= self('B')'''
        var0, var1 = _match.groups()
        return self(var0) >= self(var1)

    @known_pattern(r'(.+)[>](.+)', deps=[0,1])  # '{var0}>{var1}'
    def get_compare_greater_than(self, var, *, _match=None):
        '''self('A>B') --> boolean array: self('A') > self('B')'''
        var0, var1 = _match.groups()
        return self(var0) > self(var1)

    # note - must define <= before <, otherwise e.g. 'a<=b' --> 'a' < '=b'.
    @known_pattern(r'(.+)[<][=](.+)', deps=[0,1])  # '{var0}<={var1}'
    def get_compare_less_than_or_equal(self, var, *, _match=None):
        '''self('A<=B') --> boolean array: self('A') <= self('B')'''
        var0, var1 = _match.groups()
        return self(var0) <= self(var1)

    @known_pattern(r'(.+)[<](.+)', deps=[0,1])  # '{var0}<{var1}'
    def get_compare_less_than(self, var, *, _match=None):
        '''self('A<B') --> boolean array: self('A') < self('B')'''
        var0, var1 = _match.groups()
        return self(var0) < self(var1)

    # # # VAR_WHERE_CONDITION # # #
    cls_behavior_attrs.register('drop', default=UNSET)
    drop = simple_property('_drop', default=UNSET,
        doc='''value of 'drop' kwarg for any self('{var}_where_{condition}') calls.
        True --> drops points where condition is False. (See xarray.DataArray.where for details)
        False --> use nan where condition is False.
        default: UNSET --> True if self('condition') has ndim==1, else False.
            (easy when ndim==1 to drop nans, because condition is a 1D list of points.
             hard when ndim>=2. E.g. if mask (x,y)=(0,0) but not (0,1) and (1,0), can't drop x=0 nor y=0...)''')

    @known_pattern(r'(.+)_where_(.+)', deps=[0,1])  # '{var}_where_{condition}'
    def get_var_where_condition(self, var, *, _match=None):
        '''var_where_condition --> self(var).where(self(condition)).
        for 'drop' kwarg, in where(..., drop=...), use drop=self.drop.
        '''
        var, condition = _match.groups()
        condval = self(condition)
        drop = self.drop
        if drop is UNSET: drop = (condval.ndim == 1)
        return self(var).where(condval, drop=drop)

    @known_pattern(r'where_(.+)_(.+)', deps=[0,1])  # where_{condition}_{var}
    def get_where_condition_var(self, var, *, _match=None):
        '''where_condition_var --> self(var).where(self(condition)).
        Note: if var contains any underscores, must use parenthesis (like 'where_condition_(var)').
            The alias, self('var_where_condition'), does not have such a restriction.
        for 'drop' kwarg, in where(..., drop=...), use drop=self.drop_in_where.
        '''
        condition, var = _match.groups()
        return self(f'{var}_where_{condition}')

    # # # AT_MAX/MIN_OF # # #
    @known_pattern(r'(.+)_at_max_of_(.+)', deps=[0,1])  # '{var}_at_max_of_{ref}'
    def get_var_at_max_of_ref(self, var, *, _match=None):
        '''var_at_max_of_ref --> self(var) at argmax of self(ref),
        taking argmax across all dims in self(ref).
        For more precise control, consider directly using xarray_at_max_of.
        '''
        here, ref = _match.groups()
        return xarray_at_max_of(self(here), self(ref))

    @known_pattern(r'(.+)_at_min_of_(.+)', deps=[0,1])  # '{var}_at_min_of_{ref}'
    def get_var_at_min_of_ref(self, var, *, _match=None):
        '''var_at_min_of_ref --> self(var) at argmin of self(ref),
        taking argmin across all dims in self(ref).
        For more precise control, consider directly using xarray_at_min_of.
        '''
        here, ref = _match.groups()
        return xarray_at_min_of(self(here), self(ref))
