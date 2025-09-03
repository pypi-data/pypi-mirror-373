"""
File Purpose: Muram Calculator
"""
import os

import numpy as np

from .muram_bases import MuramBasesLoader
from .muram_direct_loader import MuramDirectLoader
from .muram_eos_loader import MuramEosLoader
from .muram_snaps import MuramSnapList
from ...mhd import  MhdCalculator, MhdUnitsManager
from ...tools import alias


class MuramCalculator(MuramEosLoader, MuramBasesLoader,
                      MuramDirectLoader,
                      MhdCalculator):
    '''PlasmaCalculator for Muram outputs.
    
    dir: str
        directory where files are located. Stored as self.dirname = os.path.abspath(dir).
    units: 'si' or 'raw'
        units system for outputs of self. 'raw' for same as muram data, 'si' for SI units.
        'cgs' for cgs, but note cgs electromagnetic quantities are not yet implemented.
        Implementation here assumes Muram outputs are always in cgs, and that mu0_raw = 1;
            i.e. MhdUnitsManager.from_mhd_cgs(ucgs_l=1, ucgs_t=1, ucgs_r=1, mu0_raw=1)
    '''

    def __init__(self, *, dir=os.curdir, units='si', **kw_super):
        self.dirname = os.path.abspath(dir)
        self.init_snaps()
        self.u = MhdUnitsManager.from_mhd_cgs(ucgs_l=1, ucgs_t=1, ucgs_r=1, mu0_raw=1)
        self.units = units
        super().__init__(**kw_super)

    # # # DIMENSIONS SETUP -- SNAPS # # #
    def init_snaps(self):
        '''set self.snaps based on snap files in self.dirname.'''
        self.snaps = MuramSnapList.from_here(dir=self.dirname)

    # # # PARAMS # # #
    @property
    def params(self):
        '''return the global params shared by all snaps.
        Equivalent to self.snaps.params_global(recalc=False).
        '''
        return self.snaps.params_global(recalc=False)

    # # # DIMENSIONS SETUP -- MAINDIMS # # #
    @property
    def maindims(self):
        '''maindims of MURAM data, i.e. ('x', 'y', 'z').
        (currently only 3D MURAM data reading is implemented.)
        see MainDimensionsHaver for more maindims implementation details.
        '''
        return ('x', 'y', 'z')

    get_space_coords = alias('get_maindims_coords')

    def get_maindims_coords(self):
        '''return dict of {'x': xcoords, 'y': ycoords, 'z': zcoords}.
        Units will be whatever is implied by self.coords_units system (default: self.units)
        coords will be sliced according to self.slices, if relevant.
        '''
        maindims = self.maindims
        u_l = self.u('l', self.coords_units_explicit)
        dx = {x: self.params[f'd{x}'] * u_l for x in maindims}
        Nx = {x: self.params[f'N{x}'] for x in maindims}
        result = {x: np.arange(Nx[x]) * dx[x] for x in maindims}
        result = self._apply_maindims_slices_to_dict(result)
        return result

    # # # INPUT TABLES (self.tabin) # # #
    @property
    def tabinputfile(self):
        '''abspath to tabinputfile (used when creating default self.tabin).
        return os.path.join(self.dirname, 'tabparam.in')
        '''
        return os.path.join(self.dirname, 'tabparam.in')
