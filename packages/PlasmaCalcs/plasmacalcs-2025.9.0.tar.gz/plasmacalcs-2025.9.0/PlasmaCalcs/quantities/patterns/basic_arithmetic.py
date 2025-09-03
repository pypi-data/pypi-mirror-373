"""
File Purpose: basic arithmetic (e.g. parenthesis, *, +, log, abs)
"""
import numpy as np
import xarray as xr

from ..quantity_loader import QuantityLoader
from ...tools import np_all_int


class BasicArithmeticLoader(QuantityLoader):
    '''basic arithmetic operations, e.g. *, +, log, abs. For parenthesis, see ParenthesisLoader.
    Also, numerical values (0, 1, and any other integer) are available, for convenience;
        the results for 'N' where N looks like an int, will be an xarray with value int(N).
    '''
    # Caution: the order of these functions matters!
    # Patterns are checked in the order that functions were defined.
    #    (technically - the order of keys in self.KNOWN_PATTERNS... which are tracked via @known_pattern)
    # Examples:
    #    get_plus before get_times --> self('a*b+c') sees '+' first, giving self('a*b')+self('c').
    #    get_minus before get_sqrt --> self('sqrt_a-b') sees '-' first, giving self('sqrt_a')-self('b')

    # # # NUMBERS # # #
    # (numbers come first to ensure, e.g., 1e-7 registers as '1e-7', not '1e'-'7'.
    @known_pattern(r'([+-]?\d+)')  # {int} --> the value of that int.
    def get_int(self, var, *, _match=None):
        '''any integer, as an xarray.'''
        i, = _match.groups()
        return xr.DataArray(int(i))

    @known_var
    def get_0(self):
        '''0, as an xarray. Code can also handle generic ints via self.get_int pattern.'''
        return xr.DataArray(0)

    @known_var
    def get_1(self):
        '''1, as an xarray. Code can also handle generic ints via self.get_int pattern.'''
        return xr.DataArray(1)

    @known_var(aliases=['NaN'])
    def get_nan(self):
        '''NaN, as an xarray.'''
        return xr.DataArray(np.nan)

    @known_var(aliases=['infinity'])
    def get_inf(self):
        '''infinity, as an xarray.'''
        return xr.DataArray(np.inf)

    # non-int numbers
    @known_pattern(r'([+-]?\d+[.]\d+)')  # {float} --> the value of that float.
    def get_float(self, var, *, _match=None):
        '''any float, as an xarray.'''
        f, = _match.groups()
        return xr.DataArray(float(f))

    @known_pattern(r'([+-]?\d+(?:[.]\d+)?)[eE]([+-]?\d+)')  # {number} --> the value of that number.
    def get_sci_number(self, var, *, _match=None):
        '''any number in scientific notation, as an xarray.'''
        base, exp = _match.groups()
        baseval = float(base) if '.' in base else int(base)
        return xr.DataArray(baseval * 10 ** int(exp))

    # # # BASIC OPERATIONS # # #
    @known_pattern(r'(.+)[+](.+)', deps=[0, 1])  # '{var0}+{var1}'
    def get_plus(self, var, *, _match=None):
        '''addition. var0 + var1.'''
        var0, var1 = _match.groups()
        return self(var0) + self(var1)

    @known_pattern(r'(.+)[-](.+)', deps=[0, 1])  # '{var0}-{var1}'
    def get_minus(self, var, *, _match=None):
        '''subtraction. var0 - var1.'''
        var0, var1 = _match.groups()
        return self(var0) - self(var1)

    # note - must be defined after plus & minus, otherwise e.g. '-a+b' --> '-' & 'a+b', <--> '-(a+b)'
    @known_pattern(r'[-](.+)', deps=[0])  # '-{var0}'
    def get_negation(self, var, *, _match=None):
        '''negation. -var.'''
        var, = _match.groups()
        return -self(var)

    @known_pattern(r'(.*[^*])[*]([^*].*)', deps=[0, 1])  # '{var0}*{var1}'. [^*] avoids matching **
    def get_times(self, var, *, _match=None):
        '''multiplication. var0 * var1.'''
        var0, var1 = _match.groups()
        return self(var0) * self(var1)

    @known_pattern(r'(.+)[/÷](.+)', deps=[0, 1])  # '{var0}/{var1}' or '{var0}÷{var1}'
    def get_divide(self, var, *, _match=None):
        '''division. var0 / var1.'''
        var0, var1 = _match.groups()
        return self(var0) / self(var1)

    @known_pattern(r'(.+)[*][*](.+)', deps=[0, 1])  # '{var0}**{var1}'
    def get_power(self, var, *, _match=None):
        '''power. var0 ** var1.'''
        var0, var1 = _match.groups()
        val0 = self(var0)
        val1 = self(var1)
        # caution - avoid naive implementation, because numpy is a bit finicky.
        #    in particular, when result would be complex but val0 & val1 are not,
        #    need to use np.emath.power, instead of **. Otherwise, will get NaN values.
        # need caution unless: any(val0 < 0) and any(val1 not an integer).
        if np.any(val0 < 0) and not np_all_int(val1):
            val0_raised_to_val1 = np.emath.power(val0, val1)
            # sadly, np.emath.power doesn't return an xarray. Make an xarray.
            result, _ = xr.broadcast(val0, val1)
            result = result.copy(data=val0_raised_to_val1)
            return result
        else:
            return val0 ** val1

    # # # BASIC FUNCTIONS # # #
    @known_pattern(r'abs_(.+)', deps=[0])  # 'abs_{var}'
    def get_abs(self, var, *, _match=None):
        '''absolute value. abs(var)'''
        var, = _match.groups()
        return np.abs(self(var))

    @known_pattern(r'log10_(.+)', deps=[0])  # 'log10_{var}'
    def get_log10(self, var, *, _match=None):
        '''log base 10. log10(var)'''
        var, = _match.groups()
        return np.log10(self(var))

    @known_pattern(r'log2_(.+)', deps=[0])  # 'log2_{var}'
    def get_log2(self, var, *, _match=None):
        '''log base 2. log2(var)'''
        var, = _match.groups()
        return np.log2(self(var))

    @known_pattern(r'loge_(.+)', deps=[0])  # 'loge_{var}'  # <-- alias for ln
    @known_pattern(r'ln_(.+)', deps=[0])    # 'ln_{var}'
    def get_ln(self, var, *, _match=None):
        '''log base e. ln(var). ('ln' and 'loge' are aliases. Uses np.log; not np.log10.)'''
        var, = _match.groups()
        return np.log(self(var))

    @known_pattern(r'exp_(.+)', deps=[0])  # 'exp_{var}'
    def get_exp(self, var, *, _match=None):
        '''exponentiation. exp(var). Also known as e^var. See also: get_power'''
        var, = _match.groups()
        return np.exp(self(var))

    @known_pattern(r'sqrt_(.+)', deps=[0])  # 'sqrt_{var}'
    def get_sqrt(self, var, *, _match=None):
        '''square root. sqrt(var)'''
        var, = _match.groups()
        val = self(var)
        result = np.emath.sqrt(val)  # emath --> use complex value, not NaN, if var is negative.
        # sadly, np.emath.sqrt doesn't return an xarray. Make an xarray.
        result = val.copy(data=result)
        return result

    @known_pattern(r'imag_(.+)', deps=[0])  # 'imag_{var}'
    def get_imag(self, var, *, _match=None):
        '''imaginary part. np.imag(self(var))'''
        var, = _match.groups()
        return np.imag(self(var))

    @known_pattern(r'real_(.+)', deps=[0])  # 'real_{var}'
    def get_real(self, var, *, _match=None):
        '''real part. np.real(self(var))'''
        var, = _match.groups()
        return np.real(self(var))
