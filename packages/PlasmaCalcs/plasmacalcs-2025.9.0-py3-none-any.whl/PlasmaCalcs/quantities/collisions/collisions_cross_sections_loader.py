"""
File Purpose: collisional cross sections calculations
"""

from .cross_section_tools import CrossMapping
from ..quantity_loader import QuantityLoader

from ...errors import InputError, FluidKeyError
from ...tools import simple_property


class CollisionsCrossSectionsLoader(QuantityLoader):
    '''cross section calculations. Mapping stored in self.collcross_map.

    This subclass is especially not intended for direct use; see CollisionsLoader instead.
    e.g. some methods here assume existence of helper methods implemented in CollisionsLoader.
    '''
    cross_mapping_type = CrossMapping

    cls_behavior_attrs.register('collisions_cross_mapping', default=CrossMapping())
    collisions_cross_mapping = simple_property('_collisions_cross_mapping', setdefaultvia='_default_cross_mapping',
        doc='''the collisions cross sections mapping to use.
        keys are (fluid1, fluid2) pairs; values are CrossTable objects.
            see self.CROSS_TABLE_DEFAULTS for shorthand options for values.
            for convenient methods to build the cross mapping, see:
                self.set_collisions_crosstab, self.set_collisions_crosstab_defaults.''')

    def _default_cross_mapping(self):
        '''return default CrossMapping object to use as self.collisions_cross_mapping.
        Called when accessing self.collisions_cross_mapping when no value has been set yet.
        '''
        cls = self.cross_mapping_type
        result = cls()
        self.set_collisions_crosstab_defaults(crossmap=result)
        return result

    def set_collisions_crosstab(self, fluid1, fluid2, crosstab, *, crossmap=None):
        '''roughly, does self.collisions_cross_mapping[(fluid1, fluid2)] = crosstab,
        but this is a bit more convenient since it allows more shorthand options (see below)

        fluid1, fluid2: int, str, or Fluid
            the fluids to set the crosstab for.
            Fluid --> use the provided value.
            int or str --> infer the Fluid based on self.fluids.
        crosstab: None, str, or CrossTable
            None --> del self.collisions_cross_mapping[(fluid1, fluid2)], if possible.
            else --> self.collisions_cross_mapping[(fluid1, fluid2)] = crosstab.
                -- CrossTable --> will use the provided value.
                -- str --> will use the CrossTable corresponding to this filename or key,
                            key from self.CROSS_TABLE_DEFAULTS.
                        Note: self.collisions_cross_mapping.smart=False can disable this.
        crossmap: None or CrossMapping
            if provided, set value in crossmap instead of in self.collisions_cross_mapping.
        
        Example, these are all equivalent, if fluids[0]=='e' and fluids[1]=='H II':
            self.set_collisions_crosstab('e', 'H II', 'e-h')
            self.set_collisions_crosstab(0, 1, 'e-h-cross.txt')
            self.set_collisions_crosstab(self.fluids.get('e'), self.fluids.get('H II'),
                                        CrossTable.from_file('e-h-cross.txt'))
            self.collisions_cross_mapping[(self.fluids.get(0), self.fluids.get(1))] = 'e-h'
        '''
        f1 = self._as_single_fluid_or_jfluid(fluid1)
        f2 = self._as_single_jfluid_or_fluid(fluid2)
        if crossmap is None: crossmap = self.collisions_cross_mapping
        if crosstab is None:
            crossmap.pop((f1, f2), None)
        else:
            crossmap[(f1, f2)] = crosstab

    def get_collisions_crosstab(self, fluid1, fluid2, *, crossmap=None):
        '''roughly, returns self.collisions_cross_mapping[(fluid1, fluid2)],
        but, this is more convenient, because:
            - fluid1 and fluid2 can be provided in shorthand.
                can provide them as Fluid objects, ints, or strs.
        crossmap: None or CrossMapping
            if provided, get value from crossmap instead of from self.collisions_cross_mapping.
        '''
        f1 = self._as_single_fluid_or_jfluid(fluid1)
        f2 = self._as_single_jfluid_or_fluid(fluid2)
        if crossmap is None: crossmap = self.collisions_cross_mapping
        return crossmap[(f1, f2)]

    @known_var(load_across_dims=['fluid', 'jfluid'], aliases=['collcross'])
    def get_collisions_cross_section(self):
        '''cross section between self.fluid and self.jfluid.
        interpolates on self.collisions_cross_mapping based on mass-weighted temperature;
            cross_table = collisions_cross_mapping[(fluid, jfluid)]
            T_sj = (m_j * T_s + m_s * T_j) / (m_j + m_s)
            result_si = cross_table(T_sj, input='T', output='cross_si')
            result = result_si * self.u('area')  # convert to self.units unit system.

        if collisions_cross_mapping[(fluid, jfluid)] is not found:
            either return 0 (as an xarray), or raise QuantInfoMissingError,
            depending on self.collisions_mode. see help(type(self).collisions_mode) for details.
        '''
        fs = self.fluid
        fj = self.jfluid
        if fs == fj:  # exclude same-same collisions
            return self('0')  # 0 as xarray
        try:
            cross_table = self.collisions_cross_mapping[(fs, fj)]
        except KeyError:
            return self._handle_missing_collisions_crosstab()  # if crash, includes KeyError info in traceback.
        T_sj = self('T_sj')
        result_si = cross_table(T_sj, input='T', output='collcross_si')
        result = result_si * self.u('area', convert_from='si')
        return result

    # # # DEFAULTS # # #
    @property
    def CROSS_TABLE_DEFAULTS(self):
        '''dict of {shorthand: (filename, fc)} with shorthand useable in self.set_collisions_crosstab.'''
        return self.cross_mapping_type.cross_table_type.DEFAULTS

    def _set_collisions_crosstab_defaults_from(self, mode='bruno', *,
                                               e=None,
                                               H_I=None, H_II=None,
                                               He_I=None, He_II=None, He_III=None,
                                               crossmap=None,
                                               ):
        '''set as many CROSS_TABLE_DEFAULTS cross sections as possible, for provided fluids.
        see also: self.set_collisions_crosstab_defaults - it provides relevant fluids from self.

        e.g. if provided e, H_I, H_II, He_II, would set:
            crossmap[e, H_I] = 'e-h'
            crossmap[H_II, H_I] = 'h-p'
            crossmap[He_II, H_I] = 'h-he'
            crossmap[H_I, H_I] = 'h-h'
        if provided more fluids, would set more crossmaps too.
        see self.CROSS_TABLE_DEFAULTS for list of available defaults.

        mode: 'bruno' or 'vranjes'
            tells which defaults to use. (bruno is probably more accurate than vranjes.)
        e, H_I, H_II, He_I, He_II, He_III: None, Fluid, int, str, or other fluid specifier.
            specifiers for electrons, H(neutral), H+, He(neutral), He+, He++ fluids.
            None --> do not set default cross tables related to this fluid.
            else --> will find corresponding Fluid value in self.fluids or self.jfluids.
        crossmap: None or CrossMapping
            if provided, set values in crossmap instead of in self.collisions_cross_mapping.
        '''
        if crossmap is None: crossmap = self.collisions_cross_mapping
        # readability is more important than efficiency here!
        inputs = dict(e=e, H_I=H_I, H_II=H_II, He_I=He_I, He_II=He_II, He_III=He_III)
        p = {k: (v is not None) for k, v in inputs.items()}  # whether each value was provided.
        if mode == 'bruno':
            # -- bruno -- charged-neutral collisions --
            if p['e'] and p['H_I']:
                self.set_collisions_crosstab(e, H_I, 'e-h', crossmap=crossmap)
            if p['e'] and p['He_I']:
                self.set_collisions_crosstab(e, He_I, 'e-he', crossmap=crossmap)
            if p['H_I'] and p['H_II']:
                self.set_collisions_crosstab(H_II, H_I, 'h-p', crossmap=crossmap)
            if p['H_I'] and p['He_II']:
                self.set_collisions_crosstab(He_II, H_I, 'h-hep', crossmap=crossmap)
            if p['H_I'] and p['He_III']:
                self.set_collisions_crosstab(He_III, H_I, 'h-hepp', crossmap=crossmap)
            if p['He_I'] and p['H_II']:
                self.set_collisions_crosstab(H_II, He_I, 'he-p', crossmap=crossmap)
            if p['He_I'] and p['He_II']:
                self.set_collisions_crosstab(He_II, He_I, 'he-hep', crossmap=crossmap)
            if p['He_I'] and p['He_III']:
                self.set_collisions_crosstab(He_III, He_I, 'he-hepp', crossmap=crossmap)
            # -- bruno -- neutral-neutral collisions --
            if p['H_I']:
                self.set_collisions_crosstab(H_I, H_I, 'h-h', crossmap=crossmap)
            if p['H_I'] and p['He_II']:
                self.set_collisions_crosstab(He_II, H_I, 'he-h', crossmap=crossmap)
            if p['He_I']:
                self.set_collisions_crosstab(He_I, He_I, 'he-he', crossmap=crossmap)
        elif mode == 'vranjes':
            # -- vranjes -- charged-neutral collisions --
            if p['e'] and p['H_I']:
                self.set_collisions_crosstab(e, H_I, 'e-h_vranjes', crossmap=crossmap)
            if p['e'] and p['He_I']:
                self.set_collisions_crosstab(e, He_I, 'e-he_vranjes', crossmap=crossmap)
            if p['H_I'] and p['H_II']:
                self.set_collisions_crosstab(H_II, H_I, 'h-p_vranjes', crossmap=crossmap)
            if p['He_I'] and p['H_II']:
                self.set_collisions_crosstab(H_II, He_I, 'he-p_vranjes', crossmap=crossmap)
            # -- vranjes -- neutral-neutral collisions --
            if p['H_I']:
                self.set_collisions_crosstab(H_I, H_I, 'h-h_vranjes', crossmap=crossmap)
            if p['He_I']:
                self.set_collisions_crosstab(He_I, He_I, 'he-he_vranjes', crossmap=crossmap)
        else:
            raise InputError(f'mode={mode!r}; expected "bruno" or "vranjes".')

    def set_collisions_crosstab_defaults(self, mode='bruno', *, crossmap=None):
        '''set CROSS_TABLE_DEFAULTS cross sections for all relevant fluids in self.
        e.g. if self has fluids e, H_I, H_II, He_II, would set:
            crossmap[e, H_I] = 'e-h'
            crossmap[H_II, H_I] = 'h-p'
            crossmap[He_II, H_I] = 'h-he'
            crossmap[H_I, H_I] = 'h-h'
        if self has more relevant fluids, would set more crossmaps too.
        see self.CROSS_TABLE_DEFAULTS for list of available defaults.
        (note that order of keys doesn't matter for crossmap since it's a SymmetricPairMapping.)

        mode: 'bruno' or 'vranjes'
            tells which defaults to use. (bruno is probably more accurate than vranjes.)
        crossmap: None or CrossMapping
            if provided, set values in crossmap instead of in self.collisions_cross_mapping.

        gets relevant fluids from self.get_collisions_crosstab_default_fluids;
            subclass may wish to override that method.
        '''
        fluids = self.get_collisions_crosstab_default_fluids()
        self._set_collisions_crosstab_defaults_from(mode=mode, **fluids, crossmap=crossmap)

    _COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES = {
        'H_I'   : ['H_I',    'H I',    'H'],
        'H_II'  : ['H_II',   'H II',   'H+'],
        'He_I'  : ['He_I',   'He I',   'He'],
        'He_II' : ['He_II',  'He II',  'He+'],
        'He_III': ['He_III', 'He III', 'He++'],
    }

    def get_collisions_crosstab_default_fluids(self):
        '''return dict of fluids from self which have any corresponding CROSS_TABLE_DEFAULTS.
        keys will be e, H_I, H_II, He_I, He_II, He_III.
        values will be Fluid objects (from self.fluids or self.jfluids)

        checks multiple possible shorthand notations for each fluid:
            e     : fluids.get_electron(), jfluids.get_electron()
            H_I   : 'H_I',    'H I',    'H'
            H_II  : 'H_II',   'H II',   'H+'
            He_I  : 'He_I',   'He I',   'He'
            He_II : 'He_II',  'He II',  'He+'
            He_III: 'He_III', 'He III', 'He++'
        if multiple matches found in any case, raise FluidValueError.
            subclass could implement more sophisticated matching if needed;
            the implementation here aims to be flexible, but crash if anything is ambiguous.
        note: possible shorthands defined by self._COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES;
            subclass might override that instead of this method, if just needing to alter shorthands.
        '''
        result = {}
        # electrons
        try:
            result['e'] = self.fluids.get_electron()
        except FluidKeyError:  # no electron in self.fluids
            try:
                result['e'] = self.jfluids.get_electron()
            except FluidKeyError:  # no electron in self.jfluids
                pass
        # other fluids:
        for f, aliases in self._COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES.items():
            try:
                result[f] = self._get_fluid_or_jfluid_like(aliases)
            except FluidKeyError:  # this fluid not found in self.fluids or self.jfluids
                pass
                # (note, above will still crash with FluidValueError, if 2+ fluids found.)
        return result

