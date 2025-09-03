"""
File Purpose: loading single-fluid MHD quantities related to Equation Of State (EOS).
"""

from .mhd_bases import MhdBasesLoader
from .mhd_er_tables import erTabInputManager
from ..defaults import DEFAULTS
from ..errors import (
    FormulaMissingError, LoadingNotImplementedError,
    InputError, InputMissingError,
)
from ..tools import simple_property, UNSET


''' --------------------- MhdEosLoader--------------------- '''

class MhdEosLoader(MhdBasesLoader):
    '''single-fluid MHD quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.

    Future refactors of PlasmaCalcs might split the functionality here,
        e.g. if there are other types of tables, add code to manage table types.
    '''
    tabin_cls = erTabInputManager  # class for making tabin during self._default_tabin()

    tabin = simple_property('_tabin', setdefaultvia='_default_tabin',
        doc='''dict-like manager for Equation Of State tables; should include keys 'ne', 'T', 'P'.
        Each table=tabin[var] should have a table.interp(r=r, e=e) method,
            which returns value of var in 'raw' units, given values of r & e in 'raw' units.''')

    def _default_tabin(self):
        '''return default value of self.tabin: erTabInputManager(self.tabinputfile, u=self.u).'''
        tabinputfile = self.tabinputfile
        return self.tabin_cls(tabinputfile, u=self.u)

    tabinputfile = simple_property('_tabinputfile',
        doc='''path to tabinputfile, used by self._default_tabin() to create self.tabin.''')
    @tabinputfile.getter
    def tabinputfile(self):
        if hasattr(self, '_tabinputfile'):
            return self._tabinputfile
        else:
            errmsg = (f"{type(self).__name__}.tabinputfile not set. You might need to set it explicitly,\n"
                      f"or this subclass might still need to implement default value for tabinputfile.")
            raise InputMissingError(errmsg)


    # # # EOS MODE DISPATCH / CODE ARCHITECTURE # # #
    cls_behavior_attrs.register('eos_mode', default='table')
    EOS_MODE_OPTIONS = {
        'ideal': '''treat as ideal gas. P = n kB T = (gamma - 1) e, and can't get ne.''',
        'table': '''plug r and e into tables (see self.tabin) to get ne, T, P.'''
    }
    eos_mode = simple_property('_eos_mode', setdefaultvia='_default_eos_mode', validate_from='EOS_MODE_OPTIONS',
            doc='''mode for "Equation of State" related variables (ne, T, P).
            see EOS_MODE_OPTIONS for details about available options.''')

    def _default_eos_mode(self):
        '''default value for self.eos_mode. Here: 'table'. Subclass might override.'''
        return 'table'

    _EOS_MODE_TO_NE_VAR = {'ideal': 'nan', 'table': 'ne_fromtable'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_NE_VAR')])
    def get_ne(self):
        '''electron number density. Depends on self.eos_mode; see self.EOS_MODE_OPTIONS for details.
        'ideal' --> cannot get ne. Crash with TypevarNanError.
        'table' --> ne from plugging r and e into EOS lookup tables (see self.tabin).
        [more options might be available (depending on subclass) -- check self.EOS_MODE_OPTIONS for details.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        mode = self.eos_mode
        if mode not in self._EOS_MODE_TO_NE_VAR:
            raise LoadingNotImplementedError(f"{type(self).__name__}('ne') when eos_mode={mode!r}.")
        var = self._EOS_MODE_TO_NE_VAR[mode]
        if var == 'nan':
            self._handle_typevar_nan(errmsg=f"get_ne fails, when eos_mode={mode!r}.")
        return self(var)

    _EOS_MODE_TO_T_VAR = {'ideal': 'T_ideal', 'table': 'T_fromtable'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_T_VAR')])
    def get_T(self):
        '''temperature. Depends on self.eos_mode; see self.EOS_MODE_OPTIONS for details.
        'ideal' --> T from ideal gas law: P_ideal = n kB T_ideal --> T_ideal = P_ideal / (n kB).
        'table' --> T from plugging r and e into EOS lookup tables (see self.tabin).
        [more options might be available (depending on subclass) -- check self.EOS_MODE_OPTIONS for details.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        mode = self.eos_mode
        if mode not in self._EOS_MODE_TO_T_VAR:
            raise LoadingNotImplementedError(f"{type(self).__name__}('T') when eos_mode={mode!r}.")
        var = self._EOS_MODE_TO_T_VAR[mode]
        if var == 'nan':  # (no nans for T in MhdEosLoader, but subclass might want to use nan.)
            self._handle_typevar_nan(errmsg=f"get_T fails, when eos_mode={mode!r}.")
        return self(var)

    _EOS_MODE_TO_P_VAR = {'ideal': 'P_ideal', 'table': 'P_fromtable'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_P_VAR')])
    def get_P(self):
        '''pressure. Depends on self.eos_mode; see self.EOS_MODE_OPTIONS for details.
        'ideal' --> P from ideal gas law: P_ideal = n kB T_ideal = (gamma - 1) e.
        'table' --> P from plugging r and e into EOS lookup tables (see self.tabin).
        [more options might be available (depending on subclass) -- check self.EOS_MODE_OPTIONS for details.]
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        mode = self.eos_mode
        if mode not in self._EOS_MODE_TO_P_VAR:
            raise LoadingNotImplementedError(f"{type(self).__name__}('P') when eos_mode={mode!r}.")
        var = self._EOS_MODE_TO_P_VAR[mode]
        if var == 'nan':  # (no nans for P in MhdEosLoader, but subclass might want to use nan.)
            self._handle_typevar_nan(errmsg=f"get_P fails, when eos_mode={mode!r}.")
        return self(var)


    # # # EOS == IDEAL GAS # # #

    @known_var(deps=['e', 'gamma'])
    def get_P_ideal(self):
        '''pressure (from ideal gas law?) P = (gamma - 1) * e
        [TODO] when is this relation actually true? is it ideal gas law, or something else?
        '''
        return (self('gamma') - 1) * self('e')

    @known_var(deps=['P_ideal', 'n'])
    def get_T_ideal(self):
        '''temperature, assuming ideal gas law. P = n kB T --> T = P / (n kB)'''
        return self('P_ideal') / (self('n') * self.u('kB'))


    # # # EOS == TABLES # # #

    def _get_ertab_var_raw(self, var):
        '''get var in 'raw' units, from the eos tables, using single-fluid r and e from self.
        CAUTION: array values use [raw], but coords use [self.coords_units].
        see self.tabin.keys() for var options. gets value via interpolation.
        '''
        table = self.tabin[var]  # <-- in its own line to help with debugging in case of crash.
        with self.using(coords_units=self.coords_units_explicit, units='raw'):
            # table values are always in 'raw' units, but result coords are in self.coords_units.
            e = self('SF_e')  # 'SF' - value for SINGLE_FLUID mode.
            r = self('SF_r')
        return table.interp(r=r, e=e)  # [raw] units for values, [self.units] for coords.

    def get_ertab_var(self, var, ustr):
        '''get var in self.units units from the eos tables, using r and e from self.
        see self.tabin.keys() for var options. gets value via interpolation.
        ustr: str
            convert result from raw to self.units by multiplying by self.u(ustr).
        '''
        result = self._get_ertab_var_raw(var) * self.u(ustr)
        return self.record_units(result)

    @known_var(deps=['SF_e', 'SF_r'], aliases=['ne_tab'])
    def get_ne_fromtable(self):
        '''electron number density, from plugging r and e into eos tables (see self.tabin).'''
        return self.get_ertab_var('ne', 'n')

    @known_var(deps=['SF_e', 'SF_r'], aliases=['T_tab'])
    def get_T_fromtable(self):
        '''temperature, from plugging r and e into eos tables (see self.tabin).'''
        # note: multifluid T_fromtable assumes same T for all fluids.
        return self.get_ertab_var('T', 'temperature')

    @known_var(deps=['SF_e', 'SF_r'], aliases=['P_tab'])
    def get_P_fromtable(self):
        '''pressure, from plugging r and e into eos tables (see self.tabin).'''
        self.assert_single_fluid_mode('P')
        return self.get_ertab_var('P', 'pressure')
