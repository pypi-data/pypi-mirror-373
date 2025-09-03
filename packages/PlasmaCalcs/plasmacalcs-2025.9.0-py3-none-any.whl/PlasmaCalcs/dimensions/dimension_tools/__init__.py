"""
Package Purpose: helper classes for dimensions subpackage.

Not intended for direct use; use a subclass instead.


This is where most of the logic for dimensions is implemented. Overview:

    DimensionValue: a single value of a dimension.
        E.g. Fluid('H', 0) or Snap('1600', 20, t=1.6e-5, dt=1e-8).
        can be converted to string or int, and is hashable (can be used as dict keys).

    DimensionValueList: a list of DimensionValue elements.
        E.g. FluidList([Fluid('H', 0), Fluid('H+', 1), Fluid('C+', 2)])
        list-like, also provides DimensionValueList.get(key) to look up elements,
            by key = str, int, slice, range, tuple, list, or DimensionValue.

    DimPoint: a dict of values representing a single point in dimension-space.
        some parts of the code will refer to "dimpoints".

    Dimension: a single dimension, representing a current value AND a list of all possible values.
        The "current value" might be a list of multiple values! And, it can change frequently.
            Meanwhile, the list of all possible values will probably not change.
        You will probably create a subclass of Dimension before making a subclass DimensionHaver,
            and use Dimension.setup_haver to decorate the DimensionHaver subclass.
        See help(Dimension) for more details.
        And/or, see examples in snaps.py, fluids.py, components.py, runs.py.

    DimensionHaver: a class which can have multiple Dimensions attached to it.
        Manages multiple Dimensions and provides methods for working with them, such as:
            current_n_dimpoints, dim_values, enumerate_dimpoints, get_first_dimpoint.
        Additionally, provides the load_across_dims method.
            load_across_dims is extremely useful for proper bookkeeping when loading arrays from multiple files,
                so it will probably be most commonly used in the hookup's "BasesLoader".
                E.g., loading 'n' across 'snap' and 'fluid' because number density varies from snap to snap
                    and from fluid to fluid. load_across_dims handles iterating across dimension values
                    and concatenating the results. (The "load from file & label array" function must be
                    provided to load_across_dims; that is defined elsewhere. See e.g. load_maindims_var.)
            Examples: see EppicBasesLoader, EbysusBasesLoader.
            Note: it might not appear directly; the method was so commonly used in "BasesLoader" classes,
                that the relevant code for calling it was included as an option in quantity_tools.py.
                Providing @known_var(..., load_across_dims=[list of strings]) will lead to calling
                load_across_dims while using the decorated function. (similar for @known_pattern.)
"""
from .dim_point import DimPoint, DimRegion
from .dimension import Dimension
from .dimension_haver import DimensionHaver
from .dimension_value import (
    DimensionValue, DimensionValueList,
    SliceableList, string_int_lookup,
    DimensionSpecialValueSpecifier, DimensionSingleValueSpecifier,
    DimensionFractionalIndexer,
    SpecialDimensionValue, UniqueDimensionValue,
)
from .multi_slices import MultiSlices, _paramdocs_multi_slices
