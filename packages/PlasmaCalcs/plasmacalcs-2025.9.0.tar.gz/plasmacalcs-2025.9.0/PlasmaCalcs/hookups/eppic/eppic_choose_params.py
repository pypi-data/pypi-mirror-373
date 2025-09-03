"""
File Purpose: making a new eppic input deck file, possibly based on existing file.
"""
import ast
import os

import numpy as np
import pandas as pd  # for pretty table of timescales

from .eppic_io_tools import (
    update_eppic_i_file, get_updated_eppic_i_str,
    _get_update_eppic_i_values_flat,
)
from ...errors import DimensionError, InputError
from ...tools import (
    format_docstring,
    alias,
    InDir, using_attrs,
    UNSET,
)
from ...defaults import DEFAULTS


### --------------------- EppicParam --------------------- ###

class EppicParam():
    '''a value for a single eppic parameters.
    Also with instructions for converting to str, and info about the old value.

    value: any
        value to use for this parameter.
    old: any
        old value for this parameter.
    fmt: str
        instructions for formatting the value.

    when this object is converted to str, will return fmt.format(value).
    '''
    def __init__(self, value, *, old=None, fmt='{:}'):
        self.value = value
        self.old = old
        self.fmt = fmt

    def fmt_str(self, value):
        '''returns self.fmt.format(value), or '0' if value==0.'''
        return '0' if value==0 else self.fmt.format(value)

    def str_value(self):
        '''returns self.fmt_str(self.value)'''
        return self.fmt_str(self.value)

    def str_old(self):
        '''returns self.fmt_str(self.old), or 'None' if self.old is None'''
        return 'None' if self.old is None else self.fmt_str(self.old)

    def eval_str_value(self):
        '''returns result of evaluating self.str_value().
        Might be different from value, due to rounding when converting to string.
        '''
        return ast.literal_eval(self.str_value())

    def eval_str_old(self):
        '''returns result of evaluating self.str_old().
        Might be different from old, due to rounding when converting to string.
        '''
        return ast.literal_eval(self.str_old())

    # # # DISPLAY # # #
    def __str__(self):
        return self.str_value()

    def __repr__(self):
        str_value = self.str_value()
        contents = [str_value]
        str_old = self.str_old()
        if str_old != str_value:
            contents.append(f'old={self.str_old()}')
        return f'{type(self).__name__}({", ".join(contents)})'


### --------------------- EppicChooseParams --------------------- ###

class EppicChooseParamsBase():
    '''class to help with choosing parameters for eppic.i file.

    Probably, use EppicChooseParams instead.
    
    values: dict
        {varname: value} for all pairs to update.
        Can also provide {dist number: dict of {varname: value} pairs to update for this dist}
            (inside of dist number dicts, varname can end with dist number or not;
            assume it does end with dist number in the file itself though)
            In this case, will be immediately converted to values_flat format.
    values_as_kw: optionally, provide additional values as kwargs.
    '''
    # # # CREATION # # #
    def __init__(self, values=dict(), *, dirname=None, **values_as_kw):
        self.values = self.values_flat(values, **values_as_kw)
        for k, v in self.values.items():
            if not isinstance(value, EppicParam):
                self.values[k] = EppicParam(v)
        self.dirname = os.path.abspath(os.curdir if dirname is None else dirname)

    # # # INSPECTION # # #
    @staticmethod
    def values_flat(values=dict(), **values_as_kw):
        '''return these values as a 'flat' dict, suitable for using to update eppic.i file.
        This is a dict of {key: value} pairs, appending dist number to key name where appropriate.
        '''
        return _get_update_eppic_i_values_flat({**values, **values_as_kw})

    # # # ADJUST VALUES # # #
    def update(self, values=dict(), **values_as_kw):
        '''update self.values with values. returns self'''
        values_flat = self.values_flat(values, **values_as_kw)
        self.values.update(values_flat)
        return self

    def setdefault(self, values=dict(), **values_as_kw):
        '''setdefault for self.values. returns self.
        Like self.update, but doesn't overwrite existing values.
        '''
        values_flat = self.values_flat(values, **values_as_kw)
        for k, v in values_flat.items():
            self.values.setdefault(k, v)
        return self

    # # # DICT-LIKE # # #
    def __getitem__(self, key):
        return self.values[key]
    def __setitem__(self, key, value):
        self.values[key] = value
    def __delitem__(self, key):
        del self.values[key]
    def __iter__(self):
        return iter(self.values)
    def __len__(self):
        return len(self.values)
    def __contains__(self, key):
        return key in self.values
    def items(self):
        return self.values.items()
    def keys(self):
        return self.values.keys()
    # don't def values()! we already have self.values...

    # # # WRITING TO FILE # # #
    def write(self, src='eppic.i', dst='eppic_updated.i', *,
              exists_ok=False, missing_values_ok=True, comment='previously={old}',
              **kw):
        '''write updated eppic.i file to dst.
        src: str
            path to source file to use as template.
        dst: str
            path to destination file to write.
        exists_ok: bool, default False
            whether it is okay for dst to already exist.
        missing_values_ok: bool
            whether it is okay for some of the varnames in values to not exist in eppic.i
        comment: None or str
            if not None, append comment as a comment to all updated lines.
            Also, this comment will be hit by .format(old=old value)

        additional kw passed to update_eppic_i_file.

        return abspath to dst.
        '''
        kw.update(exists_ok=exists_ok, missing_values_ok=missing_values_ok, comment=comment)
        with InDir(self.dirname):
            return update_eppic_i_file(src, dst, self.values, **kw)

    def str_from(self, src='eppic.i', missing_values_ok=True, comment='previously={old}', **kw):
        '''return str to use for the entire contents of the new, updated eppic.i file.
        src: str
            path to source file to use as template.
        missing_values_ok: bool
            whether it is okay for some of the varnames in values to not exist in eppic.i
        comment: None or str
            if not None, append comment as a comment to all updated lines.
            Also, this comment will be hit by .format(old=old value)

        additional kw passed to get_updated_eppic_i_str
        '''
        return get_updated_eppic_i_str(src, None, self.values, **kw)

    def __repr__(self):
        return f'{type(self).__name__}(values={self.values}, dirname={self.dirname!r})'


class EppicChooseParams(EppicChooseParamsBase):
    '''class to help with choosing parameters for eppic.i file.
    
    ec: EppicCalculator object
        the EppicCalculator to use for getting values and directory of original eppic.i file.
    var: None, str, or list of strings
        tells which getters to use when getting values. See self.GETTERS.keys() for options.
        None --> use all vars in self.GETTERS.
        str --> use this var.
        list --> use these vars.
        Use [] to use no vars, i.e. initialize only with user-provided values.
        if getting vars gives keys also provided in ``values``, use the value from ``values`` instead.
    values: dict
        {varname: value} for pairs to update in new eppic.i file.
        Can also provide {dist number: dict of {varname: value} pairs to update for this dist}
            (inside of dist number dicts, varname can end with dist number or not;
            assume it does end with dist number in the file itself though)
            Will be immediately converted to self.values_flat format.
    additional kwargs:
        passed as self(var, **kw_call) when determining initial values.

    Examples:
        Basic usage:
            choices = EppicChooseParams(eppic_calculator_object)  # create instance;
            # ^ will also fill choices with defaults based on calculations,
            #   e.g. including vtherm calculated from temperatures, and dx from ldebye from electrons.
            choices.update(...)   # any choices of params you specifically want to set can go here.
            choices.write(...)  # write a new eppic.i file based on the original, and choices.

        Other common use case - learn info about timescales:
            choices.timescales()  # EppicTimescales object
    '''
    def __init__(self, ec, var=None, *, values=dict(), **kw_call_self):
        '''create EppicChooseParameters by reading values from EppicCalculator.get_vals_for_inputs()'''
        self.ec = ec
        dirname = getattr(self.ec.input_deck, 'dirname', None)
        super().__init__(values, dirname=dirname)
        get_var_values = self(var=var, **kw_call_self)
        self.setdefault(get_var_values)

    # # # CALCULATING & CHECKING VALUES # # #
    GETTERS = dict()  # dict of {param name: method name} to use for getting values.
    CHECKERS = dict()  # dict of {check name: method name} to use for checking values.

    checks_mode = 'warn'   # default mode for doing checks. See help(self.__call__) for details.

    get = alias('__call__')

    def __call__(self, var=None, *, precision=UNSET, checks=UNSET, units='raw', **kw):
        '''return dict of {key: value} to use in input deck, based on current values in self.ec.
        (Ignores current values of self. Consider using: self.setdefault(self()).)
        Or, checks current values in self.ec for "reasonable-ness".

        var: None, str, or list of strings
            tells which getters & checkers to include.
            See self.GETTERS.keys() and self.CHECKERS.keys() for options.
            None --> use all vars in self.GETTERS and all vars in self.CHECKERS.
            str --> use this var.
            list --> use these vars.
        precision: UNSET, dict, or int
            digits of precision for exponential values when converting to strings.
            UNSET --> use each var's default, defined within its getter function.
            dict --> {{var: precision to use for var}}, for var in self.GETTERS.
        checks: UNSET, bool, 'warn', or 'crash'
            whether to check values for "reasonable-ness", and how to behave if a check fails.
            UNSET --> use self.checks_mode.
            False --> don't check.
            True --> equivalent to 'warn'
            'warn' --> print warning message for any failed checks.
            'crash' --> raise AssertionError for any failed checks.
        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        # # bookkeeping # #
        # var
        if var is None:
            var = list(self.GETTERS.keys())
            var.extend(v for v in self.CHECKERS.keys() if not v in var)
        else:
            if isinstance(var, str):
                var = [var]
            for v in var:
                if not (v in self.GETTERS or v in self.CHECKERS):
                    errmsg = (f'unknown var {v!r}! Expected one of self.GETTERS.keys(): {list(self.GETTERS.keys())} '
                              f'or self.CHECKERS.keys(): {list(self.CHECKERS.keys())}')
                    raise KeyError(errmsg)
        # precision
        if precision is UNSET:
            precision = dict()
        elif isinstance(precision, int):
            precision = {v: precision for v in var}
        # looping
        values = dict()
        with self.ec.using(units=units, **kw):
            for v in var:
                if v in self.GETTERS:
                    getter = getattr(self, self.GETTERS[v])
                    kw_v = dict(units=units, **kw)
                    if v in precision:
                        kw_v['precision'] = precision[v]
                    values.update(getter(**kw_v))
                if v in self.CHECKERS:
                    self.check(v, mode=checks)
        return values

    def check(self, var=None, *, mode=UNSET, **kw_checker):
        '''check current values in self.ec for "reasonable-ness".

        var: None, str, or list of strings
            tells which checkers to include. See self.CHECKERS.keys() for options.
            None --> use all vars in self.CHECKERS.
            str --> use this var.
            list --> use these vars.
        mode: UNSET, bool, 'warn', or 'crash'
            whether to check values for "reasonable-ness", and how to behave if a check fails.
            UNSET --> use self.checks_mode.
            False --> don't check.
            True --> equivalent to 'warn'
            'warn' --> print warning message for any failed checks.
            'crash' --> raise AssertionError for any failed checks.

        additional kwargs are passed to every used checker.

        returns dict {v: result from check_v} for each v in var.
        '''
        if var is None:
            var = list(self.CHECKERS.keys())
        else:
            if isinstance(var, str):
                var = [var]
            for v in var:
                if not (v in self.CHECKERS):
                    errmsg = (f'unknown var {v!r}! Expected one of self.CHECKERS.keys(): {list(self.CHECKERS.keys())}')
                    raise KeyError(errmsg)
        # checks_mode
        if mode is UNSET:
            checks_mode = self.checks_mode
        elif mode in (False, True, 'warn', 'crash'):
            checks_mode = mode
        else:
            raise InputError(f'invalid mode={mode!r}. Must be UNSET, False, True, "warn", or "crash".')
        if not mode:
            return dict()  # nothing to check.
        # looping
        result = dict()
        with using_attrs(self, checks_mode=checks_mode):
            for v in var:
                checker = getattr(self, self.CHECKERS[v])
                result[v] = checker(**kw_checker)
        return result

    # # GETTERS # #
    def _param_getter(f, getters=GETTERS):
        '''return f after putting f.__name__ into getters
        assert f.__name__ looks like 'get_{var}', then puts {var: f.__name__} into getters.
        '''
        fname = f.__name__
        START = 'get_'
        if not fname.startswith(START):
            raise AssertionError(f'expected f.__name__ to start with "{START}", but got {f.__name__!r}')
        name = fname[len(START):]
        getters[name] = fname
        return f

    @_param_getter
    def get_n(self, precision=3, *, units='raw', **kw):
        '''return dict of values to use for n0d for all fluids in self.ec.fluid.
        keys are n0d0, n0d1, etc. values are EppicParam objects, with old=n0d from input deck.
        precision is for converting to str in exponential form.

        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        values = dict()
        ec = self.ec
        with ec.using(units=units, **kw):
            assert ec.current_n_snap()==1, 'get_n expects self.ec.snap to be a single snap.'
            for fluid in ec.iter_fluid():
                old = fluid.get('n0d', None)
                key = f'n0d{int(fluid)}'
                n = ec('mean_n', item=True)
                values[key] = EppicParam(n, old=old, fmt=f'{{:.{precision}e}}')
        return values

    @_param_getter
    def get_v0(self, precision=3, *, units='raw', **kw):
        '''return dict of values to use for vx0d, vy0d, vz0d for all fluids in self.ec.fluid,
        for component in ec.component (e.g. use ec.component=('x', 'y') to ignore 'z')
        keys are vx0d0, vx0d1, etc. values are EppicParam objects, with old=vx0d from input deck.
        precision is for converting to str in exponential form.

        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        values = dict()
        ec = self.ec
        with ec.using(units=units, **kw):
            assert ec.current_n_snap()==1, 'get_v0 expects self.ec.snap to be a single snap.'
            for fluid in ec.iter_fluid():
                for x in ec.iter_component():
                    old = fluid.get(f'v{x}0d', None)
                    key = f'v{x}0d{int(fluid)}'
                    u = ec('mean_u', item=True)
                    values[key] = EppicParam(u, old=old, fmt=f'{{:.{precision}e}}')
        return values

    @_param_getter
    def get_vtherm(self, precision=3, *, units='raw', **kw):
        '''return dict of values to use for vxthd, vythd, vzthd for all fluids in self.ec.fluid,
        for component in ec.component (e.g. use ec.component=('x', 'y') to ignore 'z')
        keys are vxthd0, vxthd1, etc. values are EppicParam objects, with old=vxthd from input deck.
        precision is for converting to str in exponential form.

        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        values = dict()
        ec = self.ec
        with ec.using(units=units, **kw):
            assert ec.current_n_snap()==1, 'get_vtherm expects self.ec.snap to be a single snap.'
            for fluid in ec.iter_fluid():
                for x in ec.iter_component():
                    old = fluid.get(f'v{x}thd', None)
                    key = f'v{x}thd{int(fluid)}'
                    vtherm = ec('mean_vtherm', item=True)
                    values[key] = EppicParam(vtherm, old=old, fmt=f'{{:.{precision}e}}')
        return values

    @_param_getter
    def get_vtherm_n(self, precision=3, *, units='raw', **kw):
        '''return dict of {'vth_neutral': EppicParam(value to use for vth_neutral, old=value from input deck)}.

        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        ec = self.ec
        with ec.using(units=units, **kw):
            assert ec.current_n_jfluid() == 1, 'get_vtherm_n expects exactly one jfluid.'
            assert all(jfluid.is_neutral() for jfluid in ec.iter_jfluid()), 'get_vtherm_n expects neutral jfluid.'
            vtherm_n = ec.getj('mean_vtherm', item=True)
        old = ec.input_deck.get('vth_neutral', None)
        return {'vth_neutral': EppicParam(vtherm_n, old=old, fmt=f'{{:.{precision}e}}')}

    @_param_getter
    @format_docstring(default_ldebye_safety=DEFAULTS.EPPIC.DSPACE_SAFETY)
    def get_dx(self, precision=1, *, ldebye_safety=UNSET, units='raw', **kw):
        '''return dict of values to use for dx, dy, dz.
        keys are dx, dy, dz. values are EppicParam objects, with old=dx, dy, dz from input deck.
        precision is for converting to str in exponential form.

        ldebye_safety: UNSET or number
            dx, dy, dz = ldebye_safety * debye length of electrons.
            UNSET --> use DEFAULTS.EPPIC.DSPACE_SAFETY (default: {default_ldebye_safety})
        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        if ldebye_safety is UNSET: ldebye_safety = DEFAULTS.EPPIC.DSPACE_SAFETY
        values = dict()
        ec = self.ec
        with ec.using(units=units, **kw):
            assert ec.current_n_snap()==1, 'get_dx expects self.ec.snap to be a single snap.'
            KEYS = ('dx', 'dy', 'dz')
            old = {key: ec.input_deck.get(key, None) for key in KEYS}
            electron = ec.fluids.get_electron()
            ldebe = ec('mean_ldebye', fluid=electron, item=True)
            dx = ldebye_safety * ldebe
            values.update({key: EppicParam(dx, old=old[key], fmt=f'{{:.{precision}e}}') for key in KEYS})
        return values

    @_param_getter
    @format_docstring(default_dt_safety=DEFAULTS.EPPIC.DT_SAFETY)
    def get_dt(self, precision=1, *, dt_safety=UNSET, units='raw', **kw):
        '''return dict of {{'dt': EppicParam(value to use for dt, old=dt from input deck)}}.
        precision is for converting to str in exponential form.

        dt_safety: UNSET or number
            dt = dt_safety * minimum timescale.
            UNSET --> use DEFAULTS.EPPIC.DT_SAFETY (default: {default_dt_safety})
        units, kw:
            passed to self.ec.using(...) while using this method.
        '''
        if dt_safety is UNSET: dt_safety = DEFAULTS.EPPIC.DT_SAFETY
        with self.ec.using(**kw):
            timescales = self.timescales(units=units)
        dt = dt_safety * timescales.min()
        old = self.ec.input_deck.get('dt', None)
        return {'dt': EppicParam(dt, old=old, fmt=f'{{:.{precision}e}}')}

    def timescales(self, *, units='raw', **kw_init):
        '''returns an EppicTimescales object, to help with understanding the relevant timescales.
        kwargs are pased to EppicTimescales(...)
        '''
        return EppicTimescales(self.ec, units=units, **kw_init)

    # # CHECKERS # #
    def _param_checker(f, checkers=CHECKERS):
        '''return f after putting f.__name__ into checkers
        assert f.__name__ looks like 'check_{var}', then puts {var: f.__name__} into checkers.
        '''
        fname = f.__name__
        START = 'check_'
        if not fname.startswith(START):
            raise AssertionError(f'expected f.__name__ to start with "{START}", but got {f.__name__!r}')
        name = fname[len(START):]
        checkers[name] = fname
        return f

    def failed_check(self, msg):
        '''what to do when a check fails. depends on self.checks_mode.
            'warn' --> print warning message.
            'crash' --> raise AssertionError.
            True --> equivalent to 'warn'
            False --> do nothing.
        '''
        if self.checks_mode == 'warn' or self.checks_mode is True:
            print(f'WARNING: {msg}')
        elif self.checks_mode == 'crash':
            raise AssertionError(msg)
        elif self.checks_mode is False:
            pass  # do nothing.
        else:
            raise InputError(f'invalid checks_mode={self.checks_mode!r}. Must be True, False, "warn", or "crash".')

    @_param_checker
    def check_dt(self):
        '''checks that input_deck dt is smaller than or equal to the value from self.get_dt().
        returns self.get_dt(units='raw'), since it tells the suggested and old values for dt.
        '''
        dt = self.get_dt(units='raw')['dt']  # EppicParam for dt. 'raw' units to match input deck.
        value = dt.eval_str_value()
        old = dt.eval_str_old()
        if old is not None and old > value:
            self.failed_check(f'input_deck dt = {dt.str_old()} is too large! suggest dt <= {dt.str_value()}.')
        return dt

    @_param_checker
    def check_dx(self):
        '''checks that input_deck dx is smaller than or equal to the value from self.get_dx().
        returns self.get_dx(units='raw'), since it tells the suggested and old values for dx.
        '''
        dspace = self.get_dx(units='raw')  # dict of EppicParam for dx, dy, dz. 'raw' units to match input deck.
        for key, dx in dspace.items():
            value = dx.eval_str_value()
            old = dx.eval_str_old()
            if old is not None and old > value:
                self.failed_check(f'input_deck {key} = {dx.str_old()} is too large! suggest {key} <= {dx.str_value()}.')
        return dspace

    @_param_checker
    @format_docstring(default_rosenberg_safety=DEFAULTS.EPPIC.ROSENBERG_SAFETY)
    def check_rosenberg_qn(self, *, rosenberg_safety=UNSET):
        '''check the rosenberg criterion for quasineutrality, for each fluid: (nusn / wplasma)^2 << 1.
        
        rosenberg_safety: UNSET or number
            the check passes iff (nusn / wplasma)^2 <= rosenberg_safety.
            UNSET --> use DEFAULTS.EPPIC.ROSENBERG_SAFETY (default: {default_rosenberg_safety})

        return xarray of (mean(nusn / wplasma))^2 for each fluid
        '''
        ec = self.ec
        assert ec.current_n_snap()==1, 'check_rosenberg_qn expects self.ec.snap to be a single snap.'
        if rosenberg_safety is UNSET: rosenberg_safety = DEFAULTS.EPPIC.ROSENBERG_SAFETY
        rosenberg_qn = ec('max_rosenberg_qn')  # max <--> checking the "worst case".
        for fluid, val in ec.take_fluid(rosenberg_qn, as_dict=True).items():
            v = val.item()  # item() <--> expecting a single value here.
            if v > rosenberg_safety:
                errmsg = (f'Failed rosenberg_qn, for fluid {fluid}.'
                          f'\n    Expected (nusn / wplasma)^2 << 1, but got {v:.3g}, which is too large.'
                          f'\n    (Larger than {rosenberg_safety:.3g}, from DEFAULTS.EPPIC.ROSENBERG_SAFETY).')
                self.failed_check(errmsg)
        return rosenberg_qn


### --------------------- EppicTimescales --------------------- ###

class EppicTimescales():
    '''helps with calculating dt based on physical timescales for eppic.

    ec: EppicCalculator
        used for calculations of values.
    units: str, default 'raw'
        units system for output values. Probably 'raw' or 'si'.
    item: bool, default True
        True --> convert all values to scalars (e.g., python floats).
        False --> keep values as xarrays.
    calc: bool, default True
        whether to calc all values when initializing, via self.calc().
    precision: None or int
        precision to use when converting to strings.
        None --> use type(self).precision (default 1)

    self.tt will be a dict like {scalename: {key: value}},
        where key will be:
            fluid, for timescales associated with a specific fluid;
            'global', for global timescales;
            'min', for timescales which are the minimum (e.g., across fluids).
    '''
    precision = 1  # digits of precision for exponential values when converting to strings.

    def __init__(self, ec, *, units='raw', item=True, calc=True, precision=None):
        self.tt = dict()
        self.ec = ec
        self.units = units
        self.item = item
        if precision is not None:
            self.precision = precision
        if calc:
            self.calc()

    # # # CALCULATING TIMESCALES # # #
    def values(self):
        '''returns a list of all timescale from self, in no particular order.'''
        return [value for d in self.tt.values() for value in d.values()]

    def min(self):
        '''returns the minimum timescale from within self.'''
        return min(self.values())

    def calc(self):
        '''calculate all timescales, updating self.tt. returns self.'''
        self.calc_timescales()
        self.calc_subcycling()
        self.calc_mins()
        return self

    def calc_timescales(self):
        '''calculate timescales for fluids, updating self.tt. returns self.
        calculations are in units system defined by self.units (probably 'raw' or 'si').

        (the actual math for timescales is in TimescalesLoader, in timescales.py)
        '''
        tt = self.tt
        ec = self.ec
        item = self.item
        units = self.units
        with ec.using(units=units):
            if item and not ec.current_n_snap()==1:
                errmsg = 'calc_timescales expectes self.ec.snap to be a single value. (when self.item=True).'
                raise DimensionError(errmsg)
            self.snap = ec.snap   # save the current snap, for display purposes.
            # plasma frequency
            d = tt.setdefault('wplasma', dict())
            for fluid in ec.iter_fluid():
                d[fluid] = ec('min_timescale_wplasma', item=item)  # min across space.
            # gryofrequency
            d = tt.setdefault('gyrof', dict())
            for fluid in ec.iter_fluid():
                d[fluid] = ec('min_timescale_gyrof', item=item)
            # collision frequency
            d = tt.setdefault('nusn', dict())
            for fluid in ec.iter_fluid():
                d[fluid] = ec('min_timescale_nusn', item=item)
            # thermal velocity (over dx). (Note, csound is basically vtherm.)
            d = tt.setdefault('vtherm', dict())
            for fluid in ec.iter_fluid():
                d[fluid] = ec('min_timescale_vtherm', item=item)
            # |E| / |B| speed (over dx)
            d = tt.setdefault('E/B', dict())
            d['global'] = ec('min_timescale_EBspeed', item=item)
        return tt

    def calc_subcycling(self):
        '''calculate timescales incorporating subcycling of fluids, updating self.tt. returns self.
        Equivalent to dividing every fluid timescale by `subcycle` for that fluid.
        scalenames will be old scalename with '_subcycle' appended.

        Does not remove old scalenames.
        '''
        tt = self.tt
        ec = self.ec
        subcycle = self.ec('subcycle')
        for scalename, d in list(tt.items()):
            if scalename.endswith('_subcycle'):
                continue  # don't subcycle the same thing twice by accident...
            ttsub = tt.setdefault(f'{scalename}_subcycle', dict())
            for fluid, value in list(d.items()):
                if fluid == 'min':
                    continue
                elif fluid == 'global':
                    ttsub[fluid] = value
                else:
                    ttsub[fluid] = value / subcycle.sel(fluid=np.array(fluid)).item()
        return self

    def calc_mins(self):
        '''calculate 'min' for each scalename, updating self.tt. returns self.'''
        tt = self.tt
        for scalename, d in list(tt.items()):
            d['min'] = min(d.values())
        return self

    # # # TO PANDAS # # #
    def to_pandas(self):
        '''return pandas DataFrame of timescales.
        'min' and 'global' columns will appear before other columns.
        '''
        result = pd.DataFrame(self.tt).T  # .T --> header will be fluid names.
        # re-order
        header = result.columns.to_list()
        order = []
        if 'min' in header:
            order.append('min')
        if 'global' in header:
            order.append('global')
        order.extend([h for h in header if h not in order])
        result = result[order]
        return result

    # # # DISPLAY # # #
    def to_pandas_display(self):
        '''return self.to_pandas(), but prettier, for display purposes:
        - replaces NaNs with '---'.
        - converts numbers to exponential form using self.precision.
        - put a helpful caption, including self.units, self.ec.snap, and self.ec.input_deck['dt']
        - highlights the minimum value in each row (but not in the 'min' column)
        - highlights the minimum value in the 'min' column (in a different color ^)
        - puts a horizontal border above the first row whose name ends with '_subcycle'
        '''
        pdvals = self.to_pandas()
        result = pdvals.copy()
        # replace NaNs with '---'
        result = result.fillna('---')
        # convert numbers to exponential form
        def val_to_str(x):
            return x if isinstance(x, str) else f'{x:.{self.precision}e}'
        result = result.map(val_to_str)
        # # STYLER -- must (must occur after all data is editted) # #
        # add caption
        NEWLINE = '\n<br>'  # newline; works in html or not.
        caption = f'timescales [units={self.units!r}], at snap = {getattr(self, "snap", None)!r}'
        run_title = self.ec.input_deck.get('title', None)
        if run_title is not None:
            caption += f'{NEWLINE}(run title = {run_title!r})'
        dt_raw = self.ec.input_deck.get('dt', None)
        if dt_raw is not None:
            dt = dt_raw * self.ec.u('t', self.units, convert_from='raw')
            caption += f'{NEWLINE}(dt from input deck = {dt} [{self.units!r}])'
            dtmin = self.min()
            if dt > dtmin:
                caption += f'{NEWLINE}>>>> WARNING: dt > min timescale ({val_to_str(dtmin)}) <<<<'
        #caption += f'{NEWLINE}(use {type(self).__name__}.to_pandas() to get pandas DataFrame.)'
        result = result.style.set_caption(caption)
        # highlight minimum value in each row
        def highlight_min(row):
            '''highlight the minimum value in this row.'''
            minval = row.iloc[0]  # min should be first column..
            result = ['']
            for v in row.iloc[1:]:
                if v == minval:
                    result.append('background-color: #abf7b1')  # light green
                else:  # not the min
                    result.append('')
            return result
        result = result.apply(highlight_min, axis=1)
        # highlight minimum value in the 'min' column
        def highlight_min_min(col):
            '''highlight the minimum value in the 'min' column.'''
            minval = val_to_str(np.nanmin(pdvals))
            result = []
            for v in col:
                if v == minval:
                    result.append('background-color: #5ced73')  # slightly darker light green
                else:   
                    result.append('')
            return result
        result = result.apply(highlight_min_min, axis=0, subset=['min'])
        # put a border above the first row whose name ends with '_subcycle'
        # (but only if _subcycle isn't the first row)
        rownames = result.index.to_list()
        subcycle_rows = [i for i, name in enumerate(rownames) if name.endswith('_subcycle')]
        if len(subcycle_rows) > 0:
            result.set_properties(subset=(result.index[subcycle_rows[0]],),
                                  **{'border-top': '2px solid black'})
        return result

    def _repr_html_(self):
        '''display hook for jupyter notebook.'''
        return self.to_pandas_display()._repr_html_()

    def __repr__(self):
        return f'{type(self).__name__}(tt=dict with keys {list(self.tt.keys())})'
