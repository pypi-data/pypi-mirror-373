"""
Package Purpose: PlasmaCalculator for different types of inputs
"""

from .bifrost import BifrostCalculator, BifrostMultifluidCalculator
from .ebysus import EbysusCalculator
from .eppic import (
    EppicCalculator, EppicHybridCalculator,
    EppicInstabilityCalculator, EppicTfbiCalculator, EppicCalculatorWithTfbi,
)
from .muram import MuramCalculator, MuramMultifluidCalculator
from .copapic import CopapicCalculator
