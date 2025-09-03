"""
File Purpose: The main single-fluid mhd calculator class, for hookups to inherit from.
"""

from .mhd_bases import MhdBasesLoader
from .mhd_eos_loader import MhdEosLoader
from ..plasma_calculator import PlasmaCalculator

class MhdCalculator(MhdEosLoader, MhdBasesLoader, PlasmaCalculator):
    '''class for single-fluid mhd plasma calculator object.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    pass
