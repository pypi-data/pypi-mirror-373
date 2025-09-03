"""
File Purpose: electric field in Bifrost
"""
import numpy as np

from ...errors import FormulaMissingError
from ...quantities import QuantityLoader
from ...tools import alias, simple_property


### --------------------- BifrostEfieldLoader --------------------- ###

class BifrostEfieldLoader(QuantityLoader):
    '''quantities related to electric field in Bifrost'''
    @known_var(dims=['snap'])
    def get_qjoule(self):
        '''joule heating (?). eta * |J|**2. Directly from Bifrost aux.
        qjoule in aux is stored in raw units.
            for more aux units see: https://ita-solar.github.io/Bifrost/aux_variables/
        '''
        if 'qjoule' not in self.directly_loadable_vars():
            raise FormulaMissingError('qjoule when not saved to aux')
        ufactor = self.u('energy_density time-1', convert_from='raw')
        return self.load_maindims_var_across_dims('qjoule', u=ufactor, dims=['snap'])

    @known_var(deps=['qjoule', 'mod2_J'])
    def get_eta(self):
        '''eta (scalar), such that E = -u x B + eta J + ....'''
        return self('qjoule') / self('mod2_J')

    cls_behavior_attrs.register('eta_hall_mode', default='best')
    ETA_HALL_MODE_OPTIONS = {
        'best': '''use 'aux' if possible, else |B|/(|qe| * self('ne', ne_mode='best'))''',
        'aux': '''use 'eta_hall' from aux''',
        'ne_best': '''|B|/(|qe| * self('ne', ne_mode='best'))''',
        'neq': '''|B| / (|qe| * self('ne_neq'))''',
        'table': '''|B| / (|qe| * self('ne_fromtable'))''',
        'ne': '''|B| / (|qe| * self('ne')) using present value of self.ne_mode.''',
    }
    eta_hall_mode = simple_property('_eta_hall_mode', default='best',
        validate_from='ETA_HALL_MODE_OPTIONS',
        doc='''tells where to get eta_hall from. See self.ETA_HALL_MODE_OPTIONS for details.''')

    eta_hall_mode_explicit = alias('eta_hall_mode',
        doc='''self.eta_hall_mode, but if 'best' convert to the explicit mode to use.''')
    @eta_hall_mode_explicit.getter
    def eta_hall_mode_explicit(self):
        mode = self.eta_hall_mode
        if mode == 'best':
            if 'eta_hall' in self.directly_loadable_vars():
                mode = 'aux'
            else:
                mode = 'ne_best'
        return mode

    _ETA_HALL_MODE_EXPLICIT_TO_NE_DEPS = {
        'aux': [],
        'ne_best': ['mod_B', 'abs_qe', ('ne', {'ne_mode': 'best'})],
        'neq': ['mod_B', 'abs_qe', 'ne_neq'],
        'table': ['mod_B', 'abs_qe', 'ne_fromtable'],
        'ne': ['mod_B', 'abs_qe', 'ne'],
    }
    @known_var(dims=['snap'],
               attr_deps=[('eta_hall_mode_explicit', '_ETA_HALL_MODE_EXPLICIT_TO_NE_DEPS')])
    def get_eta_hall(self):
        '''eta_hall (scalar), such that E = -u x B + eta_hall J x Bhat + ....
        eta_hall in aux is stored in raw(?) units ([TODO]-check!).
        eta_hall is equivalent to |B| / (ne * |qe|).

        self.eta_hall_mode controls whether to load from aux or use a formula;
            see self.ETA_HALL_MODE_OPTIONS for options & descriptions.

        result will have 'eta_hall_mode' attr telling the mode used.
            (if 'best' but aux exists, will say 'aux' instead of 'best'.
        '''
        mode = self.eta_hall_mode_explicit
        if mode == 'aux':
            if 'eta_hall' not in self.directly_loadable_vars():
                raise FormulaMissingError('eta_hall when not saved to aux')
            ufactor = self.u('e_field current_density-1', convert_from='raw')
            result = self.load_maindims_var_across_dims('eta_hall', u=ufactor, dims=['snap'])
        else:
            mode_to_ne_mode = {'ne_best': 'best', 'neq': 'neq', 'table': 'table', 'ne': self.ne_mode}
            result = self('(mod_B)/(abs_qe*ne)', ne_mode=mode_to_ne_mode[mode])
        return result.assign_attrs(eta_hall_mode=mode)

    @known_var(dims=['snap'])
    def get_eta_amb(self):
        '''eta_amb (scalar), such that E = -u x B - eta_amb (J x Bhat) x Bhat + ....
        eta_amb in aux is stored in raw(?) units ([TODO]-check!).
        '''
        if 'eta_amb' not in self.directly_loadable_vars():
            raise FormulaMissingError('eta_amb when not saved to aux')
        ufactor = self.u('e_field current_density-1', convert_from='raw')
        return self.load_maindims_var_across_dims('eta_amb', u=ufactor, dims=['snap'])

    @known_var(deps=['(SF_u)_cross_B'], aliases=['E_motional'])
    def get_E_uxB(self, *, _B=None):
        '''E_uxB = -u x B, the motional electric field. E = E_uxB + ...
        [EFF] for efficiency, can provide B if already known.
            CAUTION: if providing B, any missing components assumed to be 0.
        '''
        result = -self('(SF_u)_cross_B', _B=_B)
        # don't include fluid=SINGLE_FLUID in result.
        result = result.drop_vars('fluid')  # [TODO] handle 'fluid not in result coords' case?
        return result

    @known_var(deps=['eta', 'J'])
    def get_E_etaJ(self, *, _J=None):
        '''E_etaJ = eta * J. Goes into E = E_uxB + E_etaJ + ...
        [EFF] for efficiency, can provide J if already known.
        '''
        J = self('J') if _J is None else _J
        return self('eta') * J

    @known_var(deps=['eta_hall', 'J_cross_B'])
    def get_E_hall(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E_hall = eta_hall * J x B / |B|. Goes into E = E_uxB + E_hall + ...
        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        eta_hall = self('eta_hall')
        JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
        mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
        return eta_hall * JxB / mod_B

    @known_var(deps=['eta_amb', 'J', 'B'])
    def get_E_amb(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E_amb = -eta_amb (J x B) x B / |B|**2. Goes into E = E_uxB + E_amb + ...
        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        eta_amb = self('eta_amb')
        JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
        JxBxB = self('(J_cross_B)_cross_B', _val0=JxB, _B=_B)
        mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
        return -eta_amb * JxBxB / mod_B**2

    cls_behavior_attrs.register('E_from_aux', default=None)
    E_from_aux = simple_property('_E_from_aux', default=None,
        doc='''whether to load bifrost E from aux (ex ey ez).
        None --> True if ex ey ez all in aux, else False.
        True --> always load from ex ey ez aux (crash if not available)
        False --> never load from ex ey ez aux.''')

    E_from_aux_explicit = alias('E_from_aux',
        doc='''self.E_from_aux, but if None convert to the explicit mode to use.''')
    @E_from_aux_explicit.getter
    def E_from_aux_explicit(self):
        if self.E_from_aux is None:
            return all(x in self.directly_loadable_vars() for x in ['ex', 'ey', 'ez'])
        else:
            return self.E_from_aux

    @known_var(deps=['E_etaJ', 'E_hall', 'E_amb'])
    def get_E_u0(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E without motional electric field contribution. E_u0 = E_etaJ + E_hall + E_amb.
        if self.E_from_aux_explicit, instead computed via: E_u0 = E (from aux ex ey ez) - E_uxB.

        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        from_aux = self.E_from_aux_explicit
        if from_aux:
            result = self('E-E_uxB')
        else:
            with self.using(component=None):  # all 3 vector components here
                J = self('J') if _J is None else _J
                B = self('B') if _B is None else _B
                JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
                mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
            E_etaJ = self('E_etaJ', _J=J)
            E_hall = self('E_hall', _J=J, _B=B, _JxB=JxB, _mod_B=mod_B)
            E_amb  = self('E_amb',  _J=J, _B=B, _JxB=JxB, _mod_B=mod_B)
            result = E_etaJ + E_hall + E_amb
        return result.assign_attrs(E_from_aux=from_aux)

    @known_var(deps=['E_uxB', 'E_u0'])
    def get_E(self):
        '''electric field from Bifrost. E = E_uxB + E_u0.
        loaded from aux ex ey ez if self.E_from_aux_explicit, else from E_uxB + E_u0.
        '''
        from_aux = self.E_from_aux_explicit
        if from_aux:
            result = self.load_maindims_var_across_dims('e', u='e_field', dims=['snap', 'component'])
        else:
            with self.using(component=None):  # all 3 vector components here
                B = self('B')
            E_uxB = self('E_uxB', _B=B)
            E_u0  = self('E_u0',  _B=B)
            result = E_uxB + E_u0
        return result.assign_attrs(E_from_aux=from_aux)

    @known_var(attr_deps=[('E_un0_type', '_E_UN0_TYPE_TO_DEPS')])
    def get_E_un0(self):
        '''electric field in u_n=0 frame.
        Result depends on self.E_un0_mode; see help(type(self).E_un0_mode) for details.
        Note: using E_un0_mode=None (the default) and self.assume_un='u',
            is equivalent to using E_un0_mode = 'un=u', which will just give self('E_u0').
        Else, E_un0 = E + u_n x B, if can get u_n (crash if can't get u_n).
        '''
        if self.E_un0_type == 'E+unxB':  # slightly more helpful error than super(); u_neutral will probably crash.
            try:
                un = self('u_neutral', component=None)  # check if can get u_n... probably cant...
            except NotImplementedError:
                errmsg = 'E_un0, when E_un0_mode=None, u_neutral unknown, and self.assume_un != "u".'
                raise FormulaMissingError(errmsg)
            else:
                result = self('E')
                if np.any(un != 0):
                    result = result + self('u_neutral_cross_B', _u_neutral=un)
        else:
            result = super().get_E_un0()
        return result

    @property   # [TODO] should be a known var instead.
    def E_un0_type(self):
        '''string telling method that will be used to get E_un0. Based on self.E_un0_mode and assume_un.
        possible results:
            'nan' <--> will crash. (e.g. this occurs if E_un0_mode = 'E0_perpmodB_min')
            'E+unxB' <--> self('E') + self('u_neutral_cross_B')
            'E_u0' <--> self('E_u0')
            'E+uxB' <--> self('E') + self('u_cross_B')
            'E' <--> self('E')
            'E0_perpB' <--> self('E0_un0_perpB')
        '''
        if self.E_un0_mode is None and self.assume_un == 'u':
            return 'E_u0'
        else:
            return super().get_E_un0_type()
