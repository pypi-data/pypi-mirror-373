"""
File Purpose: The main calculator class, for hookups to inherit from.

Subclassing order recommendation:
    put the PlasmaCalculator class LAST in the order, to ensure methods from subclass are used.
    E.g. class HookupCalculator(FooLoader, BarLoader, QuuxHaver, PlasmaCalculator).
"""

from .addons import AddonLoader
from .dimensions import (
    ComponentHaver, FluidsHaver, SnapHaver,
    MainDimensionsHaver,
)
from .plotting import PlotterManager
from .quantities import (
    # bases:
    AllBasesLoader, SimpleDerivedLoader,
    # misc:
    BperpLoader,
    CollisionsLoader,
    ConstantsLoader,
    MaskLoader,
    PlasmaDriftsLoader, PlasmaHeatingLoader, PlasmaParametersLoader,
    PlasmaStatsLoader,
    QuasineutralLoader,
    TimescalesLoader,
    # patterns, especially stats, arithmetic, calculus:
    ParenthesisLoader,
    CachesLoader,
    BlurLoader,
    FFTLoader,
    FluidsLoader,
    PolyfitLoader,
    StatsLoader,
    BasicArithmeticLoader, BasicDerivativeLoader,
    ComparisonLoader,
    VectorArithmeticLoader, VectorDerivativeLoader,
)
from .units import UnitsHaver, CoordsUnitsHaver

class DimensionlessPlasmaCalculator(
                        UnitsHaver,   # units come first since they are used by some loaders
                        ParenthesisLoader,   # check for parenthesis before other patterns
                        BperpLoader,
                        ConstantsLoader,
                        # drifts & heating inherits from parameters loader, so they must come first:
                        PlasmaDriftsLoader, PlasmaHeatingLoader, PlasmaParametersLoader,
                        PlasmaStatsLoader,  # inherits from StatsLoader, so must come first.
                        QuasineutralLoader,
                        TimescalesLoader,
                        # bases loaders go last, in case other vars loaders override:
                        AllBasesLoader, SimpleDerivedLoader,
                        # pattern-based loaders go after bases loaders.
                        CachesLoader,
                        BlurLoader,
                        FFTLoader,
                        PolyfitLoader,
                        StatsLoader,
                        BasicArithmeticLoader, BasicDerivativeLoader,
                        ComparisonLoader,
                        MaskLoader,
                        # addons go last; addons can provide extra methods but not override existing
                        AddonLoader,
                        # plotter manager can go anywhere
                        PlotterManager,
                       ):
    '''class for plasma calculator object.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    # note: the order of Loader classes *does* matter;
    #  will look in earlier classes for implementations first.
    #  e.g. if PlasmaCalculator(..., classA, ..., classB, ...) and classA and classB
    #       both have a get_foo method, then classA.get_foo will be used.
    pass

class ComponentHavingPlasmaCalculator(
            ComponentHaver,
            DimensionlessPlasmaCalculator,
            # vector loaders intentionally after DimensionlessPlasmaCalculator,
            #   so that they will be after basic arithmetic.
            #   E.g., this way log10_E_par_B gets log10_(E_par_B), not (log10_E)_par_B.
            VectorArithmeticLoader, VectorDerivativeLoader,
            ):
    '''DimensionlessPlasmaCalculator but with vector arithmetic and derivatives.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    pass

class PlasmaCalculator(CoordsUnitsHaver, MainDimensionsHaver, SnapHaver,
                       ComponentHavingPlasmaCalculator):
    '''DimensionlessPlasmaCalculator but added dimensions: component, main dimensions, snaps.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    pass

class MultifluidPlasmaCalculator(CollisionsLoader, FluidsLoader, FluidsHaver,
                                 PlasmaCalculator):
    '''PlasmaCalculator, also with fluid and jfluid.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    # CollisionsLoader goes here since it depends on jfluid.
    pass


### --------------------- Niche combinations, sometimes useful --------------------- ###

class VectorlessPlasmaCalculator(CoordsUnitsHaver, MainDimensionsHaver, SnapHaver,
                                 DimensionlessPlasmaCalculator):
    '''PlasmaCalculator without vector components/arithmetic/derivatives.
    Has all other features of PlasmaCalculator (e.g. main dimensions, snaps)

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    pass

class VectorlessMultifluidPlasmaCalculator(CollisionsLoader, FluidsLoader, FluidsHaver,
                                           VectorlessPlasmaCalculator):
    '''VectorlessPlasmaCalculator, also with fluid and jfluid.
    same as MultifluidPlasmaCalculator except without vector components / arithmetic.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    pass
