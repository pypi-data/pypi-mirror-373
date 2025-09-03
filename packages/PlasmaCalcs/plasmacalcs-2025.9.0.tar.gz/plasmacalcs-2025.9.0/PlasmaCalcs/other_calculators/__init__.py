"""
Package Purpose: other PlasmaCalculators.
E.g. allow user to input data directly during __init__.

These can require addons, but should not require hookups.
    hookups are for reading specific kinds of data.
    other_calculators are for generic data.
E.g., a hookup might rely on one of the other_calculators.
"""
from .from_dataset import (
    DimensionlessFromDatasetCalculator, ComponentHavingFromDatasetCalculator,
    FromDatasetCalculator, MultifluidFromDatasetCalculator,
    SnaplessMultifluidFromDatasetCalculator,
    VectorlessFromDatasetCalculator, VectorlessMultifluidFromDatasetCalculator,
)
from .instability_calculator import (
    VectorlessInstabilityCalculator, InstabilityCalculator,
)
