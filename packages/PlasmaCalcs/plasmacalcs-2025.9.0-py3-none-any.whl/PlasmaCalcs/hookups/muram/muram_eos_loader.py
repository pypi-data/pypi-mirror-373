"""
File Purpose: loading single-fluid Muram quantities related to Equation Of State (EOS).
"""
import os

from ...errors import SnapValueError
from ...mhd import MhdEosLoader


''' --------------------- MuramEosLoader--------------------- '''

class MuramEosLoader(MhdEosLoader):
    '''single-fluid Bifrost quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.
    '''

    # non-aux functionality is inherited from MhdEosLoader.
    # 'aux' functionality is implemented here: read directly from aux files.

    EOS_MODE_OPTIONS = {**MhdEosLoader.EOS_MODE_OPTIONS,
        'aux': '''read directly from aux files for eosP, eosT, and eosne.'''
    }

    def _all_eos_aux_files_exist(self):
        '''returns whether eos aux files (eosP, eosT, and eosne) exist for all snaps in self.'''
        try:
            loadable = self.directly_loadable_vars()
        except SnapValueError:
            return False  # [TODO] this is overly restrictive...
        else:
            return all(var in loadable for var in ('eosT', 'eosP', 'eosne'))

    def _default_eos_mode(self):
        '''default for how to handle "Equation of State" related variables (ne, T, P).
        (provides default value for self.eos_mode.)

        result will be 'aux' if files for 'eosT', 'eosP', and 'eosne' exist for each snap,
        else 'table' if 'tabparams.in' file exists,
        else 'ideal'.
        '''
        if self._all_eos_aux_files_exist():
            return 'aux'
        elif os.path.isfile(os.path.join(self.dirname, 'tabparams.in')):
            return 'table'
        else:
            return 'ideal'

    # tell super().get_ne to use self('ne_aux') if eos_mode=='aux':
    _EOS_MODE_TO_NE_VAR = {**MhdEosLoader._EOS_MODE_TO_NE_VAR, 'aux': 'ne_aux'}

    # tell super().get_T to use self('T_aux') if eos_mode=='aux':
    _EOS_MODE_TO_T_VAR = {**MhdEosLoader._EOS_MODE_TO_T_VAR, 'aux': 'T_aux'}

    # tell super().get_P to use self('P_aux') if eos_mode=='aux':
    _EOS_MODE_TO_P_VAR = {**MhdEosLoader._EOS_MODE_TO_P_VAR, 'aux': 'P_aux'}

    @known_var(dims=['snap'])
    def get_ne_aux(self):
        '''electron number density, from 'eosne' file.'''
        ufactor = self.u('n', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosne', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_T_aux(self):
        '''temperature, from 'eosT' file.'''
        # note: multifluid T_aux assumes same T for all fluids.
        return self.load_maindims_var_across_dims('eosT', u='K', dims=['snap'])

    @known_var(dims=['snap'])
    def get_P_aux(self):
        '''pressure, from 'eosP' file.'''
        ufactor = self.u('pressure', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosP', u=ufactor, dims=['snap'])
