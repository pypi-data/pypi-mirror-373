"""
Package Purpose: InstabilityCalculator specialized in computing EPPIC values.
Input is an xarray.Dataset.
Knows how to write input deck files for eppic, based on values.
"""

from .eppic_instability_calculator import EppicInstabilityCalculator
from .eppic_tfbi_calculator import EppicTfbiCalculator, EppicCalculatorWithTfbi

from .eppic_dist_inputs_loader import EppicDistInputsLoader
from .eppic_glob_inputs_loader import EppicGlobInputsLoader
from .eppic_safety_info_loader import EppicSafetyInfoLoader
from .eppici_maker import (
    EppiciMaker,
    eppici_dict, eppici,
)


# import submodule into this namespace so it can be accessed from elsewhere if needed.
# (necessary because it has the same name as this subpackage: eppic_instability_calculator)
from . import eppic_instability_calculator as _eppic_instability_calculator_py
