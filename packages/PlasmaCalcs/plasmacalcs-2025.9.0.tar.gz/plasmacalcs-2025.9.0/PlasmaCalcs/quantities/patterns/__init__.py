"""
Package Purpose: common patterns for quantities. E.g. stats, arithmetic, derivatives.
"""
# import loaders
from .parenthesis_loader import ParenthesisLoader
from .basic_arithmetic import BasicArithmeticLoader
from .basic_derivatives import BasicDerivativeLoader
from .blur_loader import BlurLoader
from .caches_loader import CachesLoader
from .comparison_loader import ComparisonLoader
from .fft_loader import FFTLoader
from .fluids_loader import FluidsLoader
from .polyfit_loader import PolyfitLoader
from .stats_loader import StatsLoader
from .vector_arithmetic import VectorArithmeticLoader
from .vector_derivatives import VectorDerivativeLoader

# import other things
from .vector_arithmetic import (
    magnitude, unit_vector, angle_xy, angle_xy_to_hat,
    dot_product, cross_product, cross_component,
    take_perp_to, take_parallel_to,
)