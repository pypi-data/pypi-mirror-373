"""
File Purpose: fluids for multifluid analysis of single-fluid mhd.
"""
import abc

from ..elements import Element, ElementList
from ...defaults import DEFAULTS
from ...dimensions import Fluid, FluidList, FluidSpecialValueSpecifier
from ...errors import InputError, FluidKeyError, FluidValueError
from ...tools import (
    alias, alias_child, simple_property, elementwise_property,
    UNSET, NO_VALUE,
    Binding, identity,
    is_iterable,
    as_roman_numeral,
)
binding = Binding(locals())


### --------------------- MhdFluid objects --------------------- ###

# # # ELEMENT HANDLER LOGIC # # #

class ElementHandler():
    '''MhdFluid which handles Elements, e.g. might have non-None self.element.
    provides get_element, get_elements, neutral, ion, and saha_list.
    '''
    element_cls = Element  # assert self.get_element() returns an instance of this class, if not None.
    # cls for making new Specie or SpecieList based on element or elements: 
    specie_cls = NotImplemented   # Specie; assigned later in this file.
    specie_list_cls = NotImplemented   # SpecieList; assigned later in this file.

    def get_element(self, default=NO_VALUE):
        '''return self.element if it exists and is not None, else crash with FluidKeyError.
        default: NO_VALUE or any value.
            If provided, when element missing or None, return default instead of crash.
        '''
        element = getattr(self, 'element', None)
        if element is None:
            if default is NO_VALUE:
                raise FluidKeyError(f'get_element() when self.element missing or None. (self={self!r})')
        elif not isinstance(element, self.element_cls):
            raise FluidValueError(f'get_element() expected {self.element_cls.__name__}; got {element!r}')
        return element

    def get_elements(self, default=NO_VALUE):
        '''return list of elements in self.
        The implementation here just returns [self.get_element(default=default)].
        '''
        return [self.get_element(default=default)]

    def neutral(self, **kw_specie):
        '''return neutral Specie of self.get_element().'''
        return self.specie_cls.neutral(self.get_element(), **kw_specie)

    def ion(self, q=1, **kw_specie):
        '''return ionized Specie of self.get_element()
        q: charge in elementary charge units. (default: +1)
        '''
        return self.specie_cls.ion(self.get_element(), q=q, **kw_specie)

    get_I = alias('neutral')
    get_II = alias('ion')

    def saha_list(self, *, istart=0, **kw_specie):
        '''return SpecieList of neutral & once-ionized ions of self.get_element().
        istart: start index for the SpecieList. Index affects conversion to int.
        '''
        neutral = self.neutral(**kw_specie)
        ion = self.ion(**kw_specie)
        return self.specie_list_cls([neutral, ion], istart=istart)


# # # MHDFLUID AND ELEMENTHAVER # # # 

class MhdFluid(ElementHandler, Fluid, abc.ABC):
    '''abstract base class for any fluid in multifluid analysis of single-fluid mhd.
    E.g. Specie or IonMixture.

    Every MhdFluid is an ElementHandler (e.g. has self.get_element(), might return None or crash)
        however not necessarily an ElementHaver (has self.element, probably non-None)
    '''
    # allow ordering of MhdFluids even if they aren't subclasses of each other (e.g. Specie & IonMixture).
    # super() gives NotImplemented if not subclasses of each other;
    # here only gives NotImplemented if not subclasses of MhdFluid.
    def __lt__(self, other):
        if isinstance(other, MhdFluid): return (self.i, self.s) < (other.i, other.s)
        else: return NotImplemented
    def __le__(self, other):
        if isinstance(other, MhdFluid): return (self.i, self.s) <= (other.i, other.s)
        else: return NotImplemented
    def __gt__(self, other):
        if isinstance(other, MhdFluid): return (self.i, self.s) > (other.i, other.s)
        else: return NotImplemented
    def __ge__(self, other):
        if isinstance(other, MhdFluid): return (self.i, self.s) >= (other.i, other.s)
        else: return NotImplemented


class ElementHaver(MhdFluid):
    '''fluid which may "have" an element. E.g. Element or Specie.

    name: None or str
        name of this fluid. None --> name unknown.
    i: None or int
        index of this fluid (within an ElementHaverList)
    element: None, dict, or Element
        the element which this ElementHaver "has".
        dict --> convert to Element via Element.from_dict(element).
    '''
    def __init__(self, name=None, i=None, *, element=None, **kw_super):
        super().__init__(name=name, i=i, **kw_super)
        # (super(MhdFluid) because we want to skip MhdFluid's __init__ which causes crash.)
        if (element is not None) or (not hasattr(self, 'element')):
            if (element is not None) and not isinstance(element, Element):
                element = Element.from_dict(element)
            self.element = element

    def to_dict(self, *, element_to_dict=True):
        '''return dictionary of info about self. Attribute values for keys in self._kw_def.
        e.g. if _kw_def={'name', 'i', 'm'}, then result = {'name': self.name, 'i': self.i, 'm': self.m}

        element_to_dict: bool, default True
            whether to also convert result['element'].to_dict() too, if non-None 'element' in result.
        '''
        result = super().to_dict()
        if element_to_dict and (result.get('element', None) is not None):
            result['element'] = result['element'].to_dict()
        return result


# # # ELEMENT CLASS HOOKUP # # #
# Element is a "virtual subclass" of ElementHaver, instead of a true subclass,
# to keep the elements.py code focused on single-fluid mhd,
# without worrying about multifluid complications.

ElementHaver.register(Element)  # (see abc.ABC for details)
with binding.to(Element):  # assign most of the relevant ElementHandler methods & attributes:
    # cls for making new Element, Specie, or SpecieList objects:
    Element.element_cls = Element
    Element.specie_cls = NotImplemented   # Specie; assigned later in this file.
    Element.specie_list_cls = NotImplemented   # SpecieList; assigned later in this file.
    # methods that are exactly the same for Element and ElementHaver:
    Element.neutral   = ElementHaver.neutral
    Element.ion       = ElementHaver.ion
    Element.get_I     = ElementHaver.get_I
    Element.get_II    = ElementHaver.get_II
    Element.saha_list = ElementHaver.saha_list

    # stuff defined here:
    Element.element = property(identity,
        doc='''alias to self. because self (an Element) is the element corresponding to self.''')

    @binding
    def get_element(self, *args__None, **kw__None):
        '''return self (because self is an Element...).
        (ElementHaver-related logic expects this method to exist.)
        '''
        return self

    @binding
    def get_elements(self, *args__None, **kw__None):
        '''return [self] (because self is an Element...).
        (ElementHaver-related logic expects this method to exist.)
        '''
        return [self]

    # no need to bind to_dict; the existing Element.to_dict (from super()) works just fine.


# # # SPECIE # # #
# [TODO] make GenericSpecie for electron, neutral, or ion,
#   and make ElectronSpecie (for electron) and Specie (for non-electron) subclasses,
#   so that Specie can actually require element to be provided.

class Specie(ElementHaver):
    '''Fluid corresponding to a specie, e.g. H_I, H_II, e, Fe_II.
    (code uses 'specie' as singular of 'species', to clarify singular vs plural.)

    CAUTION: some code assumes (without checking) that Specie objects are immutable.
        Changing a Specie after creating it could lead to unexpected behavior.

    species usually have a name. Every specie has a charge (possibly charge=0)
    non-electron species should also have an associated Element.

    name: UNSET, None, or str
        name of this specie.
        UNSET --> infer from element and q; None if no element.
                inferred name will be element name + roman numeral based on q,
                e.g. H_I for neutral H, H_II for H+.
        None --> cannot convert self to str.
    i: None or int
        the index of this specie (within a SpecieList).
        None --> cannot convert self to int.
    q: number
        charge, in elementary charge units (e.g. -1 for electrons, +1 for H_II)
    m: UNSET, None, or number
        mass, in atomic mass units (e.g. ~1 for H_I or H_II).
        UNSET --> use element.m.
        None --> cannot get self.m
    element: None, dict, or Element
        Element associated with this specie.
        dict --> convert to Element via Element.from_dict(element).
    '''
    _kw_def = {'name', 'i', 'q', 'm', 'element'}

    def __init__(self, name=UNSET, i=None, *, q, m=UNSET, element=None):
        if (element is not None) and not isinstance(element, Element):
            element = Element.from_dict(element)
        if name is UNSET:
            name  = None if element is None else f'{element.name}_{as_roman_numeral(q+1)}'
        if m is UNSET:
            m     = None if element is None else element.m
        super().__init__(name=name, i=i, m=m, q=q, element=element)

    # # # CREATION OPTIONS # # #
    @classmethod
    def electron(cls, name='e', i=None, *, m=UNSET, **kw_init):
        '''create an electron Specie (with q=-1).
        m: if UNSET, use physical value: DEFAULTS.PHYSICAL.CONSTANTS_SI['me amu-1']
        '''
        if m is UNSET: m = DEFAULTS.PHYSICAL.CONSTANTS_SI['me amu-1']
        return cls(name=name, i=i, q=-1, m=m, **kw_init)

    @classmethod
    def from_element(cls, element, i=None, *, q, **kw_init):
        '''create a Specie from this Element (& charge q [elementary charge units]).
        name and m inferred from element and q, unless provided explicitly here.
        '''
        return cls(i=i, q=q, element=element, **kw_init)

    @classmethod
    def neutral(cls, element, i=None, **kw_init):
        '''create a neutral Specie (with q=0) from element.
        element: Element object. Used to infer name and m, by default.
        '''
        return cls.from_element(element, i=i, q=0, **kw_init)

    @classmethod
    def ion(cls, element, i=None, *, q=1, **kw_init):
        '''create an ion Specie from element and q [elementary charge units]
        element: Element object. Used to infer name and m, by default.
        '''
        if q <= 0:
            raise FluidValueError(f'q must be positive for ions, but got q={q}')
        return cls.from_element(element, i=i, q=q, **kw_init)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [repr(val) for val in [self.name, self.i] if val is not None]
        contents.append(f'q={self.q}')
        if (self.m is not None) and ((self.element is None) or (self.m != self.element.m)):
            contents.append(f'm={self.m:{".1e" if self.m < 1e-3 else ".3f"}}')
        if self.element is not None:
            contents.append(f'element={self.element.name}')
        return f'{type(self).__name__}({", ".join(contents)})'


# # # ION MIXTURE # # #

class IonMixture(MhdFluid):
    '''Fluid corresponding to multiple ions grouped together, e.g. Mg+Al+Si_II

    CAUTION: some code assumes (without checking) that IonMixture objects are immutable.
        Changing an IonMixture after creating it could lead to unexpected behavior.

    IonMixtures usually have a name. Every IonMixture has a charge (probably charge=1).
    Name and charge can be inferred from the species in the mixture.

    species: iterable of Specie or dict objects
        the list of Species in this mixture. length must be at least 1.
        internally stored as SpecieList(species)
        dicts --> convert to SpecieList via SpecieList.from_dicts(species).
    i: None or int
        the index of this mixture (within an IonMixtureList or MhdFluidList)
        None --> cannot convert self to int.
    q: UNSET or number
        charge, in elementary charge units (e.g. +1 for H_II).
        all species must have the same charge else raise NotImplementedError.
        UNSET --> infer q from species.
        number --> assert q > 0, and q == spec.q for spec in species.
    name: UNSET, None, or str
        name of this mixture. None --> unnamed.
        UNSET --> infer from species. E.g. Mg_II, Al_II, Si_II --> Mg+Al+Si_II
    m_mean_mode: str in {'simple', 'density'}
        how to calculate the mass of this mixture.
        'simple' --> m = mean(spec.m for spec in species). This is a constant.
        'density' --> m = density weighted mean of spec.m for spec in species.
                          this might vary across maindims and snaps...
    m_tol: UNSET, None, or number
        crash if any |m_s - mean(m)| is more than m_tol * mean(m).
        (using simple mean for this test, regardless of m_mean_mode)
        (Prevents accidentally creating a mixture of ions with very different masses.)
        UNSET --> use self.DEFAULT_M_TOL (default=0.1)
        None --> allow any masses.
    '''
    _kw_def = {'species', 'i', 'q', 'name', 'm_mean_mode', 'm_tol'}
    _kw_eq = {'species', 'i', 'q', 'name', 'm_mean_mode'}  # (don't check m_tol when testing for equality)

    specie_cls = Specie  # ensure all species are instances of this class.
    specie_list_cls = NotImplemented  # SpecieList; assigned later in this file

    # crash if |m_s - mean(m)| > m_tol * mean(m).
    DEFAULT_M_TOL_SIMPLE = 0.1  # default m_tol when m_mean_mode='simple'
    DEFAULT_M_TOL_DENSITY = 0.3  # default m_tol when m_mean_mode='density'
    # m_tol density default larger because density-weighting is probably more physically accurate,
    #    e.g. if one of the species' is not present it will not contribute at all.
    
    def __init__(self, species, i=None, *, q=UNSET, name=UNSET,
                 m_mean_mode='simple', m_tol=UNSET):
        if len(species) == 0:
            raise InputError(f'{type(self).__name__} requires len(species)>0')
        if isinstance(species[0], dict):
            species = self.specie_list_cls.from_dicts(species)
        else:
            species = self.specie_list_cls(species)
        if self.specie_cls is not None:
            if any(not isinstance(spec, self.specie_cls) for spec in species):
                errmsg = (f'{type(self).__name__} expects all species to be '
                          f'instances of {self.specie_cls.__name__}, but got {species}')
                raise FluidValueError(errmsg)
        self.species = species
        if name is UNSET:
            name = self.infer_name()
        if q is UNSET:
            q = species[0].q
        charges = [spec.q for spec in species]
        if any(charge != q for charge in charges[1:]):
            raise NotImplementedError(f"{type(self).__name__} if species charges differ: {charges}")
        if q is None or q <= 0:
            raise InputError(f'{type(self).__name__} requires q > 0, but got q={q}')
        self.m_mean_mode = m_mean_mode
        if m_tol is UNSET:
            m_tol = self.DEFAULT_M_TOL_SIMPLE if m_mean_mode == 'simple' else self.DEFAULT_M_TOL_DENSITY
        self.m_tol = m_tol
        self._check_m_tol()
        if m_mean_mode == 'simple':
            m = self.m_mean
        else:
            m = None  # mass not constant
        super().__init__(name=name, i=i, q=q, m=m)

    def _check_m_tol(self):
        '''crash if any |m_s - mean(m)| is more than m_tol * mean(m).
        return max(|m_s - mean(m)| / mean(m)).
        '''
        m_tol = self.m_tol
        m_mean = self.m_mean
        largest_diff = 0
        for spec in self.species:
            diff = abs(spec.m - m_mean)
            if (m_tol is not None) and (diff > m_tol * m_mean):
                errmsg = (f'{type(self).__name__} specie mass is too far from mean, for specie {spec}.\n'
                          f'Require |m_s - mean(m)| < m_tol * mean(m), when provided non-None m_tol.\n'
                          f'(m_s={spec.m:.1f}, mean(m)={m_mean:.1f},'
                          f' m_tol={m_tol:.3f}, m_tol*mean(m)= {m_tol*m_mean:.1f})')
                raise FluidValueError(errmsg)
            largest_diff = max(largest_diff, diff / m_mean)
        return largest_diff

    _VALID_M_MEAN_MODES = ('simple', 'density')
    m_mean_mode = simple_property('_m_mean_mode', validate_from='_VALID_M_MEAN_MODES',
            doc='''str telling how to calculate the mass of this mixture.
            'simple' --> m = mean(spec.m for spec in species). This is a constant.
            'density' --> m = density weighted mean of spec.m for spec in species.
                              this might vary across maindims and snaps...''')

    @property
    def m_mean(self):
        '''return mean mass of species in this mixture.
        (Always using a simple mean: sum(s.m for s in species)/len(species))
        '''
        if any(spec.m is None for spec in self.species):
            raise FluidValueError(f'{type(self).__name__}.m_mean needs non-None m for all species.')
        return sum(spec.m for spec in self.species) / len(self.species)

    def infer_name(self):
        '''infer name based on species' names.
        if all species' names have the same suffix (starting at underscore),
            '+'.join(names without suffix) + suffix.
        else, '+'.join(names).
        '''
        prefixes = []
        suffix = None
        names = [spec.name for spec in self.species]
        if all('_' in name for name in names):
            for name in names:
                prefix, _, suffix_here = name.rpartition('_')
                if suffix is None:
                    suffix = suffix_here
                elif suffix != suffix_here:
                    suffix = None
                    break
                prefixes.append(prefix)
        if suffix is None:
            return '+'.join(names)
        else:
            return '+'.join(prefixes) + '_' + suffix

    # temporarily disabled... xarray doesn't like using IonMixture as coord if these are enabled...
    # def __iter__(self):
    #     return iter(self.species)
    # def __len__(self):
    #     return len(self.species)
    # def __getitem__(self, key):
    #     return self.species[key]
    
    # # # DIMENSION VALUE BEHAVIOR # # #
    get = alias_child('species', 'get', doc='''return self.species.get(key)''')

    def lookup_dict(self):
        '''return dict for looking up self within a DimensionValueList, given int, str, or self.
        (used by DimensionValueList.lookup_dict)
        in addition to being able to lookup self,
            also allows lookup of any species within self, by name or object (but not index).
        E.g. if H_II=Specie('H_II', i=3) in self,
            result will include {'H_II': H_II, H_II: H_II}, but will not include {3: H_II}
        '''
        result = super().lookup_dict()
        for spec in self.species:
            result[spec] = spec
            result[str(spec)] = spec
        return result

    def to_dict(self, *, species_to_dict=True):
        '''return dictionary of info about self. Attribute values for keys in self._kw_def.

        species_to_dict: bool, default True
            whether to also convert result['species'].to_dict() too.
        '''
        result = super().to_dict()
        if species_to_dict:
            result['species'] = result['species'].to_dict()  # SpecieList has to_dict() method.
        return result

    # # # ELEMENT HANDLING # # #
    def get_elements(self, default=NO_VALUE):
        '''return list of elements in self, i.e. spec.get_element() for spec in self.'''
        return [spec.get_element(default=default) for spec in self.species]

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [repr(val) for val in [self.name, self.i] if val is not None]
        contents.append(f'q={self.q}')
        if self.m is not None:
            contents.append(f'm={self.m:{".1e" if self.m < 1e-3 else ".3f"}}')
        if self.m_mean_mode != 'simple':
            contents.append(f'm_mean_mode={self.m_mean_mode!r}')
        return f'{type(self).__name__}({", ".join(contents)})'


### --------------------- MhdFluidList objects --------------------- ###

# # # ELEMENT HANDLER LIST LOGIC # # #

class ElementHandlerList():
    '''list of ElementHandler objects'''
    element_list_cls = ElementList  # class for making new ElementList

    element = elementwise_property('element',
            doc='''[fluid.element for fluid in self].
            To ignore fluids missing elements, consider self.unique_elements() instead.''')
    elements = alias('element')

    def unique_elements(self, *, istart=None):
        '''return ElementList composed of unique elements from ElementHandlers in self.
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        element_lists = [h.get_elements(default=None) for h in self]
        elements = [el for ellist in element_lists for el in ellist if el is not None]
        return self.element_list_cls.unique_from(elements, istart=istart)


# # # MHDFLUIDLIST # # #

class MhdFluidList(ElementHandlerList, FluidList, abc.ABC):
    '''list of any MhdFluid objects.'''
    value_type = MhdFluid
    specie_cls = Specie   # class for making new Specie objects
    ion_mixture_cls = IonMixture   # class for making new IonMixture objects

    def _new_mhd_fluid_list(self, *args, **kw):
        '''return new MhdFluidList (or subclass), with args & kw passed to __init__.
        Subclass might override to also pass info from self into the result.
        '''
        return self._new(*args, **kw)

    def prepend_electron(self, *, electron=UNSET, istart=0, **kw_specie):
        '''return MhdFluidList like self but prepend electron to result.
        electron: UNSET or Specie
            UNSET --> make new electron Specie via Specie.electron().
            Specie --> assert is_electron() then prepend this specie to result.
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        if electron is UNSET:
            electron = self.specie_cls.electron()
        elif not electron.is_electron():
            raise FluidValueError(f'cannot prepend non-electron specie {electron} to list of species')
        return self._new_mhd_fluid_list([electron] + list(self), istart=istart)

    def neutral_list(self, *, unique=False, default=NO_VALUE, istart=0, **kw_specie):
        '''return MhdFluidList of neutral species for elements of fluids in self.
        unique: bool
            whether to give result based on self.unique_elements(), or neutral(f) for f in self.
            False --> result[k] guaranteed to correspond to self[k] for all k.
            True --> ignore fluids without neutral (e.g. electron, or fluid without element),
                     and allow fluids to provide multiple neutrals (e.g. IonMixture with len>1).
        default: NO_VALUE or any value
            if provided, when unique=False and element missing, return default instead of crash.
        istart: None or int.
            int --> use result[k].with_i(istart + k) for all k.
        '''
        if isinstance(default, Element):
            raise NotImplementedError('default=Element not yet supported.')
        if unique:
            elements = self.unique_elements(istart=istart)
        else:
            elements = []
            for f in self:  # use for loop instead of list comprehension for easier debugging if crash.
                el = f.get_element(default=default)  # crashes if element missing and default=NO_VALUE.
                elements.append(el)
        result = [el.neutral(**kw_specie) for el in elements]
        return self._new_mhd_fluid_list(result, istart=istart)

    def ion_list(self, *, q=1, unique=False, default=NO_VALUE, istart=0, **kw_specie):
        '''return MhdFluidList of once-ionized ions for elements of fluids in self.
        q: number, probably int
            charge in elementary charge units. (default: +1)
        unique: bool
            whether to give result based on self.unique_elements(), or ion(f) for f in self.
            False --> result[k] guaranteed to correspond to self[k] for all k.
                      (IonMixtures will remain IonMixtures.)
            True --> ignore fluids without ions (e.g. electron, or fluid without element),
                     and allow fluids to provide multiple ions (e.g. IonMixture with len>1).
        default: bool
            if provided, when unique=False and element missing, return default instead of crash.
        istart: None or int.
            int --> use result[k].with_i(istart + k) for all k.
        '''
        if isinstance(default, Element):
            raise NotImplementedError('default=Element not yet supported.')
        if unique:  # handle IonMixtures separately
            elements = self.unique_elements(istart=istart)
            ions = [el.ion(q=q, **kw_specie) for el in elements]
        else:
            ions = []
            for f in self:
                if isinstance(f, IonMixture):
                    if f.q != q:
                        raise NotImplementedError(f'[TODO] ion_list(q={q}) when q != ion_mixture.q (={f.q})')
                    ions.append(f)
                else:
                    el = f.get_element(default=default)
                    ions.append(el.ion(q=q, **kw_specie))
        return self._new_mhd_fluid_list(ions, istart=istart)

    def saha_list(self, *, istart=0, **kw_specie):
        '''return MhdFluidList of neutral & once-ionized ion for elements of fluids in self.
        Internally, equivalent to: [spec for f in self for spec in f.saha_list()]
        crashes if any fluid is missing an element.
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        result = []
        for f in self:
            result.extend(f.saha_list(**kw_specie))
        return self._new_mhd_fluid_list(result, istart=istart)

    def one_neutral_many_ions(self, *, q=1, unique=False, default=NO_VALUE, istart=0, **kw_specie):
        '''return MhdFluidList of self[0].neutral() then self.ion_list(q=q).
        q, unique, and default all get passed directly to self.ion_list.
        istart: None or int. int --> use result[k].with_i(istart + k) for all k.
        '''
        neutral = self[0].neutral(**kw_specie)
        ions = self.ion_list(q=q, unique=unique, default=default, **kw_specie)
        return self._new_mhd_fluid_list([neutral] + ions, istart=istart)

    # # # MIXING # # #
    def mix(self, fluids, *, append=False, istart=0, **kw_ion_mixture):
        '''return MhdFluidList but with the indicated fluids turned into an IonMixture.
        fluids can be any valid key for self.get which will return an iterable.
            E.g. slice, range, list of indices, list of strings. But not single int or str.
        append: bool
            if True, append mixture instead of putting it at position of first ion that got mixed.
        istart: None or int.
            int --> use result[k].with_i(istart + k) for all k.
        '''
        indices, ions = self.indices(fluids, return_get=True)
        if (getattr(ions, 'ndim', 1) == 0) or (is_iterable(ions) and len(ions) <= 1):
            raise FluidKeyError(f'cannot mix less than 2 fluids; got self.get({fluids!r})=={ions!r}')
        mixed = self.ion_mixture_cls(ions, **kw_ion_mixture)
        i_insert = len(self) if append else min(indices)
        result_without_mix = self.without_i(indices)
        result = result_without_mix.inserted(i_insert, mixed)
        return self._new_mhd_fluid_list(result, istart=istart)

    def mixing(self, *mixes, append=False, istart=0, **kw_ion_mixture):
        '''return MhdFluidList but with the indicated groups of fluids turned into IonMixtures.
        Equivalent: self.mix(mixes[0], **kw).mix(mixes[1], **kw)...

        mixes: iterable of fluids to mix. Each fluid can be any valid key for self.get.
            E.g. slice, range, list of indices, list of strings. But not single int or str.
            CAUTION: mixes are applied in order. Using index-based mixes might produce unexpected results.
        append: bool
            if True, append each mixture instead of putting it at position of first ion that got mixed.
        istart: None or int.
            int --> use result[k].with_i(istart + k) for all k.
        '''
        result = self
        for fluids in mixes:
            result = result.mix(fluids, append=append, istart=istart, **kw_ion_mixture)
        return result

    def mix_heavy_ions(self, m_tol=0.1, *, m_min=5, q=1, append=False, istart=0, **kw_ion_mixture):
        '''return MhdFluidList but grouping heavy ions into as few IonMixtures as possible,
        given the tolerance level for mass deviations within a group, set by m_tol.
        (If any IonMixture would have length==1, leave it as an ion instead.)

        The implementation here takes the naive approach:
            group heavy ions in order, making each group as large as possible.
        This is not necessarily the optimal solution (fewest number of IonMixtures),
            but it produces decent results with minimal compuation / coding effort.
            [TODO] find the actual optimal solution?

        m_tol: number
            maximum allowed relative mass deviation from mean within a group.
            within each group, all ions have |m_ion - mean(m)| < m_tol * mean(m).
            E.g. 0.1 --> all ions in each group are within 10% of that group's mean mass.
        m_min: number
            minimum mass (in amu, i.e. m_H ~= 1) for an ion to be considered "heavy".
            ions with m < m_min are ignored.
        q: number
            charge in elementary charge units. (default: +1)
            ions with different value of q are ignored.
        append: bool
            if True, append each mixture instead of putting it at position of first ion that got mixed.
        istart: None or int.
            int --> use result[k].with_i(istart + k) for all k.
        '''
        heavy_ions = [f for f in self.ions() if (f.m is not None) and (f.m >= m_min)]
        # sort by mass
        heavy_ions = [(f.m, f) for f in heavy_ions]
        heavy_ions.sort()
        heavy_ions = [f for (m, f) in heavy_ions]
        # group into mixtures as large as possible.
        mixtures = []
        while heavy_ions:
            first = heavy_ions.pop(0)
            group = [first]
            msum = first.m
            while heavy_ions:
                ion = heavy_ions[0]
                msum = msum + ion.m
                mmean = msum / (1+len(group))  # 1+ <-- "as if ion was added to group"
                if (ion.m - mmean) > m_tol * mmean:  # new ion would be too massive
                    break
                if (mmean - group[0].m) > m_tol * mmean:  # including new ion would make ions[0] not massive enough
                    break
                # else, this ion belongs in this group.
                group.append(heavy_ions.pop(0))
            mixtures.append(group)
        # remove mixtures with length 1 (IonMixture implementation requires 2+ ions)
        mixtures = [m for m in mixtures if len(m) > 1]
        # convert fluids to strings (prevents crash if multiple mixtures)
        mixtures = [[str(f) for f in m] for m in mixtures]
        # make mixtures
        return self.mixing(*mixtures, append=append, istart=istart, m_tol=m_tol, **kw_ion_mixture)

    # # # GETTING SUBSETS OF VALUES # # #
    def i_species(self):
        '''return indices of Specie fluids in self'''
        return [i for i, f in enumerate(self) if isinstance(f, Specie)]
    def species(self):
        '''return MhdFluidList of Specie fluids in self.'''
        return self[self.i_species()]

    def i_ion_mixtures(self):
        '''return indices of IonMixture fluids in self'''
        return [i for i, f in enumerate(self) if isinstance(f, IonMixture)]
    def ion_mixtures(self):
        '''return MhdFluidList of IonMixture fluids in self.'''
        return self[self.i_ion_mixtures()]

    def ion_mixture_species(self):
        '''return MhdFluidList of Specie fluids from IonMixture fluids in self.'''
        i_mixtures = self.i_ion_mixtures()
        mixtures = [self[i] for i in i_mixtures]
        species = [spec for mix in mixtures for spec in mix.species]
        return self._new_mhd_fluid_list(species)


class ElementHaverList(MhdFluidList):
    '''list of ElementHaver objects.'''
    value_type = ElementHaver


# # # ELEMENTLIST CLASS HOOKUP # # #
# Element is a "virtual subclass" of MhdFluidList, instead of a true subclass,
# to keep the elements.py code focused on single-fluid mhd,
# without worrying about multifluid complications.

ElementHaverList.register(ElementList)  # (see abc.ABC for details)
with binding.to(ElementList):  # assign most of the relevant ElementHandler methods & attributes:
    # cls for making new Specie, IonMixture, ElementList, or MhdFluidList objects:
    ElementList.specie_cls = Specie
    ElementList.ion_mixture_cls = IonMixture
    ElementList.element_list_cls = ElementList
    ElementList.mhd_fluid_list_cls = MhdFluidList
    # stuff that is exactly the same for Element and ElementHaver:
    ElementList.element          = ElementHaverList.element
    ElementList.elements         = ElementHaverList.elements
    ElementList.unique_elements  = ElementHaverList.unique_elements
    ElementList.prepend_electron = ElementHaverList.prepend_electron
    ElementList.neutral_list     = ElementHaverList.neutral_list
    ElementList.ion_list         = ElementHaverList.ion_list
    ElementList.saha_list        = ElementHaverList.saha_list
    ElementList.one_neutral_many_ions = ElementHaverList.one_neutral_many_ions

    # stuff defined here:
    @binding
    def _new_mhd_fluid_list(self, *args, **kw):
        '''return new MhdFluidList, with args & kw passed to __init__.'''
        return self.mhd_fluid_list_cls(*args, **kw)


# # # SPECIELIST # # #

class SpecieList(MhdFluidList):
    '''list of Specie objects.'''
    value_type = Specie


# # # IONMIXTURELIST # # #

class IonMixtureList(MhdFluidList):
    '''list of IonMixture objects'''
    value_type = IonMixture


### --------------------- Connect stuff that was NotImplemented --------------------- ###

ElementHandler.specie_cls = Specie
ElementHandler.specie_list_cls = SpecieList
Element.specie_cls = Specie
Element.specie_list_cls = SpecieList
IonMixture.specie_list_cls = SpecieList


### --------------------- SpecialValueSpecifiers --------------------- ###

SPECIES = FluidSpecialValueSpecifier('species', 'SPECIES')
ION_MIXTURES = FluidSpecialValueSpecifier('ion_mixtures', 'ION_MIXTURES')
ION_MIXTURE_SPECIES = FluidSpecialValueSpecifier('ion_mixture_species', 'ION_MIXTURE_SPECIES')
