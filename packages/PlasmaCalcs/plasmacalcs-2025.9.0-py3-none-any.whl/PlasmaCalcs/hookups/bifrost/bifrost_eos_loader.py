"""
File Purpose: loading single-fluid Bifrost quantities related to Equation Of State (EOS).
"""
from ...mhd import MhdEosLoader
from ...tools import alias


''' --------------------- BifrostEosLoader--------------------- '''

class BifrostEosLoader(MhdEosLoader):
    '''single-fluid Bifrost quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.
    '''

    # non-NEQ functionality is inherited from MhdEosLoader.
    # NEQ ("nonequilibrium") functionality is implemented here.

    EOS_MODE_OPTIONS = {**MhdEosLoader.EOS_MODE_OPTIONS,
        'neq': '''non-equilibrium ionization for H (possibly also for He too):
            ne and T from hionne and hiontg (from aux). P from table, r, and e.'''
    }

    _default_eos_mode = alias('eos_mode_sim')

    def eos_mode_sim(self):
        '''how simulation handled "Equation of State" related variables (ne, T, P).
        (provides default value for self.eos_mode.)

        'ideal' --> treated as ideal gas: P = n kB T = (gamma - 1) e.
            ne not available.
        'table' --> plugged into EOS lookup tables (see self.tabin)
            plug r and e into tables to get ne, T, P.
        'neq' --> non-equilibrium ionization for H (possibly also for He too):
            ne and T from hionne and hiontg (from aux). P from table, r, and e.
        '''
        if 'tabinputfile' not in self.params:
            return 'ideal'
        elif self.params.get('do_hion', False):
            return 'neq'
        else:
            return 'table'

    # tell super().get_ne to use self('ne_neq') if eos_mode=='neq':
    _EOS_MODE_TO_NE_VAR = {**MhdEosLoader._EOS_MODE_TO_NE_VAR, 'neq': 'ne_neq'}

    # tell super().get_T to use self('T_neq') if eos_mode=='neq':
    _EOS_MODE_TO_T_VAR = {**MhdEosLoader._EOS_MODE_TO_T_VAR, 'neq': 'T_neq'}

    # tell super().get_P to use self('P_fromtable') if eos_mode=='neq':
    _EOS_MODE_TO_P_VAR = {**MhdEosLoader._EOS_MODE_TO_P_VAR, 'neq': 'P_fromtable'}
    # (even in 'neq' mode, P still comes from table, r, and e.)

    @known_var(dims=['snap'])
    def get_ne_neq(self):
        '''electron number density, from 'hionne' in aux.
        hionne in aux is stored in cgs units.
        '''
        ufactor = self.u('n', convert_from='cgs')
        return self.load_maindims_var_across_dims('hionne', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_T_neq(self):
        '''temperature, from 'hiontg' in aux.
        hiontg in aux is stored in [K] units.
        '''
        # note: multifluid T_neq assumes same T for all fluids.
        return self.load_maindims_var_across_dims('hiontg', u='K', dims=['snap'])
