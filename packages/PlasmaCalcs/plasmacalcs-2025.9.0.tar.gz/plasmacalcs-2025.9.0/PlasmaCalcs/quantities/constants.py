"""
File Purpose: values of constants (e.g. kB)

(Be careful not to use ambiguous letters here which might be used for other values,
    e.g. might want to avoid using 'e' to mean 2.728...
    since 'e' might be used for a variable like energy density.
    In those cases, can use a more descriptive name, e.g. 'econst' or 'eulerconst')
"""
import numpy as np

from .quantity_loader import QuantityLoader

class ConstantsLoader(QuantityLoader):
    '''load values of constants (numbers which depend on, at most, self.units)
    [EFF] note, it's more efficient to get these numbers directly inside functions,
        instead of calling self an extra time to load the constant.
        E.g. self.u('kB') instead of self('kB').
    However, it's sometimes very convenient to be able to access these values
        directly from the call architecture. E.g. when testing different variables
        and making plots based on them, such as self('m*(vsqr-u**2)/kB')
    '''
    @known_var
    def get_pi(self):
        '''pi. numpy.pi. 3.1415...'''
        return np.pi

    @known_var
    def get_kB(self):
        '''boltzmann constant, in [self.units] units. Equivalent to self.u('kB')'''
        return self.u('kB')

    @known_var
    def get_amu(self):
        '''1 atomic mass unit, in [self.units] units. Equivalent to self.u('amu')'''
        return self.u('amu')

    @known_var(deps=['m'])
    def get_m_amu(self):
        '''mass in atomic mass units. Equivalent to self('m/amu').'''
        return self('m/amu')

    @known_var
    def get_eps0(self):
        '''vacuum permittivity, in [self.units] units. Equivalent to self.u('eps0')'''
        return self.u('eps0')

    @known_var
    def get_abs_qe(self):
        '''|electron charge|, in [self.units] units. Equivalent to self.u('qe').
        abs to avoid any possible ambiguity, since electron charge itself is negative.
        '''
        return self.u('qe')
