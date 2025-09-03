"""
File Purpose: errors in PlasmaCalcs
"""


### --------------------- Misc Errors --------------------- ###

class BindingError(ValueError):
    '''error indicating an issue with binding; see tools.binding.'''
    pass

class ImportFailedError(ImportError):
    '''error indicating that an import failed in the past, which is why a module cannot be accessed now.'''
    pass

class TimeoutError(Exception):
    '''error indicating a timeout.'''
    pass

class FileAmbiguityError(OSError):
    '''error indicating some ambiguity due to which files exist or don't exist.'''
    pass


### --------------------- Quantity Calculation Errors --------------------- ###

class QuantCalcError(ValueError):
    '''error in quantity calculation.'''
    pass

class FormulaMissingError(QuantCalcError, NotImplementedError):
    '''error in locating formula to calculate quant.'''
    pass

class OverrideNotApplicableError(QuantCalcError):
    '''error indicating that an override function is not applicable.'''
    pass

class CacheNotApplicableError(QuantCalcError):
    '''error indicating there is no relevant value in the cache.'''
    pass

class UnitsError(QuantCalcError):
    '''error related to units.'''
    pass

class UnitsUnknownError(UnitsError):
    '''error related to units being unknown.'''
    pass

class FileContentsError(QuantCalcError):
    '''error related to contents of a file being incorrect or unexpected.'''
    pass

class ValueLoadingError(FileContentsError):
    '''error related to loading a value from a file, but NOT just because it's not yet implemented.
    E.g., when it is known that value "should" exist, but it turns out to not exist in the file.
    '''
    pass

class FileContentsMissingError(FileContentsError):
    '''error indicating missing information in a file.'''
    pass

class FileContentsConflictError(FileContentsError):
    '''error related to conflicting information in a file.'''
    pass

class LoadingNotImplementedError(FormulaMissingError):
    '''error indicating failed to implement how to load these values from files.'''
    pass

class SetvarNotImplementedError(FormulaMissingError):
    '''error indicating failed to implement setvar, e.g. for a particular var.'''
    pass

class TypevarNanError(FormulaMissingError):
    '''error indicating a typevar is nan,
    probably due to conditions making it impossible to load the corresponding var.
    '''
    pass

class MemorySizeError(QuantCalcError):
    '''error indicating size of data is too large.'''
    pass

class CollisionsModeError(QuantCalcError):
    '''error indicating an issue with the mode of collisions.'''
    pass


### --------------------- InputErrors --------------------- ###

class InputError(TypeError):
    '''error indicating something is wrong with the inputs, e.g. to a function.'''
    pass

class InputConflictError(InputError):
    '''error indicating two or more inputs provide conflicting information.
    E.g. foo(lims=None, vmin=None, vmax=None) receiving lims=(1,7), vmin=3, might raise this error,
    if the intention is for vmin and vmax to be aliases to lims[0] and lims[1].
    '''
    pass

class InputMissingError(InputError):
    '''error indicating that an input is missing AND doesn't have an appropriate default value.
    E.g. default=None; def foo(kwarg=None): if kwarg is None: kwarg=default; but foo expects non-None value.
    '''
    pass

class QuantInfoMissingError(InputError, QuantCalcError):
    '''error indicating that info is missing during a quantity calculation.
    E.g., cross table missing when attempting to read cross section.
    '''
    pass


### --------------------- Dimensions --------------------- ###

class DimensionError(Exception):
    '''error indicating some issue with a dimension'''
    pass

class DimensionalityError(DimensionError):
    '''error indicating dimensionality issue, e.g. wrong number of dimensions'''
    pass

class DimensionSizeError(DimensionError):
    '''error indicating a dimension is the wrong size.'''
    pass

class DimensionKeyError(KeyError, DimensionError):
    '''error indicating missing value of a dimension (e.g. FluidKeyError, SnapKeyError).'''
    def __str__(self):
        '''use standard error string. Avoid KeyError string which uses repr(message).'''
        return super(KeyError, self).__str__()

class DimensionValueError(ValueError, DimensionError):
    '''error indicating some incompatibility regarding the value of a dimension (e.g. SnapValueError)'''
    pass

class DimensionAttributeError(AttributeError, DimensionError):
    '''error indicating some issue with an attribute of a dimension, probably that it doesn't exist.'''
    pass

class ComponentKeyError(DimensionKeyError):
    '''error indicating component key not found.'''
    pass

class ComponentValueError(DimensionValueError):
    '''error indicating some issue with value for a Component.'''
    pass

class FluidKeyError(DimensionKeyError):
    '''error indicating Fluid key not found.'''
    pass

class FluidValueError(DimensionValueError):
    '''error indicating some issue with value for a Fluid.'''
    pass

class SnapKeyError(DimensionKeyError):
    '''error indicating Snap key not found.'''
    pass

class SnapValueError(DimensionValueError):
    '''error indicating some issue with value for a Snap.'''
    pass

class RunKeyError(DimensionKeyError):
    '''error indicating Run key not found.'''
    pass

class RunValueError(DimensionValueError):
    '''error indicating some issue with value for a Run.'''
    pass


### --------------------- PlottingErrors --------------------- ###

class PlottingError(ValueError):
    '''error indicating an issue with plotting'''
    pass

class MappableNotFoundError(PlottingError):
    '''error indicating mappable not found. E.g., might be raised during colorbar()'''
    pass

class PlottingAmbiguityError(PlottingError):
    '''error indicating an ambiguity with plotting, e.g. multiple images found when looking for only 1.'''
    pass

class PlottingNotImplementedError(PlottingError, NotImplementedError):
    '''error indicating some aspect of plotting is not implemented'''
    pass

class TooManyPlottablesError(PlottingError):
    '''error indicating too many things to make a plot.'''
    pass

class TooManySubplotsError(TooManyPlottablesError):
    '''error indicating too many subplots.'''
    pass

class PlotSettingsError(PlottingError):
    '''error indicating an issue with plot settings.'''
    pass

class PlottingNframesUnknownError(PlottingNotImplementedError):
    '''error indicating number of frames unknown for plotting a movie.'''
    pass


### --------------------- Serializing --------------------- ###

class SerializationError(ValueError):
    '''error indicating an issue related to serialization or deserialization.'''
    pass

class SerializingError(SerializationError):
    '''error indicating an issue when serializing.'''
    pass

class DeserializingError(SerializationError):
    '''error indicating an issue when deserializing.'''
    pass


### --------------------- Subsampling --------------------- ###

class SubsamplingError(ValueError):
    '''error indicating an issue with subsampling.'''
    pass

class SubsamplingFormatError(SubsamplingError):
    '''error indicating an issue with the format of subsampling.'''
    pass

class SubsamplingNotFoundError(SubsamplingError):
    '''error indicating that something related to subsampling was expected but not found.'''
    pass
