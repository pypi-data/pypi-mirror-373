"""
File Purpose: EbysusCollisionsLoader
"""
import xarray as xr

from ...errors import CollisionsModeError
from ...quantities import CollisionsLoader
from ...tools import UNSET, format_docstring

class EbysusCollisionsLoader(CollisionsLoader):
    '''collision frequency calculations.
    allows collisions_mode = 'helita' to get value via helita.
    '''
    @known_var(dims=['snap', 'fluid', 'jfluid'])
    def get_nusj_helita(self):
        '''collision frequency. (directly from Ebysus)
        for a single particle of s (self.fluid) to collide with any of j (self.jfluid).
        '''
        return self.load_maindims_var_across_dims('nu_ij', dims=['snap', 'fluid', 'jfluid'])

    COLLISIONS_MODE_OPTIONS = CollisionsLoader.COLLISIONS_MODE_OPTIONS.copy()
    COLLISIONS_MODE_OPTIONS['helita'] = \
            '''Use nusj_helita to get collision frequency.
            (However, for same fluid & jfluid, use 0 instead.)'''

    COLLISION_TYPE_TO_VAR = CollisionsLoader.COLLISION_TYPE_TO_VAR.copy()
    COLLISION_TYPE_TO_VAR['helita'] = 'nusj_helita'

    @format_docstring(docs_super=CollisionsLoader.get_collision_type)
    def get_collision_type(self):
        '''Similar to super().get_collision_type, but also allows 'helita' <--> do 'helita' collisions.
        
        super().get_collision_type docs copied here for reference:
        ----------------------------------------------------------
        {docs_super}
        '''
        try:
            return super().get_collision_type()
        except CollisionsModeError:
            if self.collisions_mode == 'helita':
                return xr.DataArray('helita')
            else:
                raise
