"""
File Purpose: EbysusEfieldLoader
"""

import xarray as xr

from ...quantities import QuantityLoader
from ...tools import UNSET, xarray_sum

class EbysusEfieldLoader(QuantityLoader):
    '''calculate electric field from ebysus'''

    @known_var(dims=['snap', 'component'])
    def get_E_helita(self):
        '''electric field. (directly from helita)'''
        return self.load_maindims_var_across_dims('ef', dims=['snap', 'component'])

    @known_var(deps=['u', 'B'], ignores_dims=['fluid'])
    def get_E_uxB(self, *, _u_e=UNSET):
        '''electric field u x B contribution. E_uxB == -1 * u_electron cross B

        [EFF] for efficiency, can provide full u_e, if already known. (provide as _u_e)
                (requires full ue, not just one component, since will do ue cross B.)
        '''
        result = UNSET
        # in case appropriate _u_e was provided:
        if _u_e is not UNSET:
            uecomps = _u_e.coords.get('component', [])
            if not xr.core.utils.is_scalar(uecomps) and len(uecomps) == 3:
                B = self('B')
                result = self.cross_product(B, _u_e, components=self.component)
        # in case appropriate _u_e was not provided:
        if result is UNSET:
            result = self('B_cross_u', fluid=self.fluids.get_electron())
        return result.drop_vars('fluid')  # drop the fluid coordinate because result doesn't care about it.

    @known_var(deps=['grad_P', 'n', 'q'], ignores_dims=['fluid'])
    def get_E_bat(self, *, _u_e=None):
        '''electric field battery contribution. E_bat == grad(P_e) / (ne qe)'''
        with self.using(fluid=self.fluids.get_electron()):
            grad_Pe = self('grad_P')
            ne = self('n')
            qe = self('q')
        result = grad_Pe / (ne * qe)
        return result.drop_vars('fluid')  # drop the fluid coordinate because result doesn't care about it.

    @known_var(deps=['nu_ij', 'u', 'q'], ignores_dims=['fluid'])
    def get_E_momj(self, *, _u_e=UNSET):
        '''electric field momentum contribution due to jfluid.
        E_momj == -1 * me ne nu_ej * (uj - ue) / (ne qe)

        [EFF] for efficiency, can provide u_e if already known. (provide as _u_e)
            (only used if _u_e.coords['component'] has the exact same values as self.component.)
        '''
        with self.using(fluid=self.fluids.get_electron()):
            nuej = self('nusj')
            #ne = self('n')  # ne cancels out; don't need it.
            qe = self('q')
            me = self('m')
            uj = self.getj('u')
            ue = UNSET
            # in case appropriate _u_e was provided:
            if _u_e is not UNSET:
                uecomps = _u_e.coords.get('component', [])
                if not xr.core.utils.is_scalar(uecomps):
                    if set(c.item() for c in uecomps) == set(self.component):
                        ue = _u_e
            # in case appropriate _u_e was not provided:
            if ue is UNSET:
                ue = self('u')
        result = (me / qe) * nuej * (ue - uj)
        return result.drop_vars('fluid')  # drop the fluid coordinate because result doesn't care about it.

    @known_var(deps=['E_momj'], ignores_dims=['jfluid'])
    def get_E_mom(self, *, _u_e=UNSET):
        '''electric field momentum contribution. E_mom == -1 * sum_j me ne nu_ej * (uj - ue) / (ne qe)
        Equivalent: E_mom = sum(E_momj), where sum is taken across jfluids.

        [EFF] for efficiency, can provide full u_e, if already known. (provide as _u_e)
                (requires full ue, not just one component, since will do ue cross B.)
        '''
        # [EFF] skip jfluids which are known to have nu_ej == 0:
        electron = self.fluids.get_electron()
        jfluids = [fj for fj in self.jfluids if self('collision_type', fluid=electron, jfluid=fj).item() != '0']
        result = self('E_momj', jfluid=jfluids, _u_e=_u_e)
        return xarray_sum(result, dim='jfluid')
        # [EFF] below is significantly slower than above; maybe due to needing ue multiple times?
        # results = []
        # for fj in jfluids:
        #     results.append(self('E_momj', jfluid=fj))
        # return sum(results).drop_vars('jfluid')  # drop the jfluid coordinate because result doesn't care about it.

    @known_var(deps=['E_uxB', 'E_bat', 'E_mom'])
    def get_E_terms(self):
        '''xarray Dataset of the terms which contribute to E.
        Dataset with 'E_uxB', 'E_bat', and 'E_mom' as data vars.

        Suggestion: to quickly determine which E_terms are most important, consider using, e.g.:
            self('mod_E_terms').pc.stats(keep='variable')  # for mod across all components
            self('E_terms', component=0).pc.stats(keep='variable')  # for just component 0
        '''
        ue = self('u', fluid=self.fluids.get_electron())  # [EFF] calculate this only once.
        return self(['E_uxB', 'E_bat', 'E_mom'], _u_e=ue)

    @known_var(deps=['E_uxB', 'E_bat', 'E_mom'])
    def get_E(self):
        '''electric field. E = E_uxB + E_bat + E_mom'''
        # [EFF] (2024/03/16) ~20% faster than helita when doing all three components, thanks to _u_e.
        #     However, ~70% slower than helita when doing only 1 component.
        #     (tested with a 512x512 grid for ~10 snapshots.)
        # accuracy check: seems to be reasonably similar at dd.stagger_kind='first' or 'fifth'.
        # [TODO] further efficiency improvements?
        ue = self('u', fluid=self.fluids.get_electron())  # [EFF] calculate this only once.
        return self('E_uxB', _u_e=ue) + self('E_bat') + self('E_mom', _u_e=ue)
