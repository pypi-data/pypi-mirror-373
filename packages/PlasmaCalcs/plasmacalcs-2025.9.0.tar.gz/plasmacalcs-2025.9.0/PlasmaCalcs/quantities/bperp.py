"""
File Purpose: shorthand for quantities "perpendicular to B"
"""

from .quantity_loader import QuantityLoader

class BperpLoader(QuantityLoader):
    '''shorthand for quantities "perpendicular to B".'''
    @known_var(deps=['u_perp_B'])
    def get_uperp(self):
        '''velocity vector, perpendicular to B. This is a full 3-vector.
        Equivalent: self('u_perp_B') == u - self('u_par_B') == u - (u dot Bhat) Bhat
        '''
        return self('u_perp_B')

    @known_var(deps=['u_par_B'])
    def get_upar(self):
        '''velocity vector, parallel to B. This is a full 3-vector.
        Equivalent: self('u_par_B') == (u dot Bhat) Bhat
        '''
        return self('u_par_B')

    @known_var(deps=['E_perp_B'])
    def get_Eperp(self):
        '''electric field, perpendicular to B. This is a full 3-vector.
        Equivalent: self('E_perp_B') == E - self('E_par_B') == E - (E dot Bhat) Bhat
        '''
        return self('E_perp_B')

    @known_var(deps=['E_par_B'])
    def get_Epar(self):
        '''electric field, parallel to B. This is a full 3-vector.
        Equivalent: self('E_par_B') == (E dot Bhat) Bhat
        '''
        return self('E_par_B')

    @known_pattern(r'Ta(joule)?perp', deps=[{0: 'Ta{group0}_perp_B'}])
    def get_Taperp(self, var, *, _match=None):
        '''Taperp --> anisotropic temperature, perpendicular to B. This is a full 3-vector.
        Equivalent: self('Ta_perp_B') == Ta - self('Ta_par_B') == Ta - (Ta dot Bhat) Bhat
        Also supports 'Tajouleperp' to get value in energy units; == 'Taperp*kB'.
        '''
        joule, = _match.groups()
        if joule is None: joule = ''
        return self(f'Ta{joule}_perp_B')

    @known_pattern(r'T(joule)?par', deps=[{0: 'Ta{group0}_par_B'}])
    def get_Tapar(self, var, *, _match=None):
        '''Tapar --> anisotropic temperature, parallel to B. This is a full 3-vector.
        Equivalent: self('Ta_par_B') == (Ta dot Bhat) Bhat
        Also supports 'Tajoulepar' to get value in energy units; == 'Tapar*kB'.
        '''
        joule, = _match.groups()
        if joule is None: joule = ''
        return self(f'Ta{joule}_par_B')
