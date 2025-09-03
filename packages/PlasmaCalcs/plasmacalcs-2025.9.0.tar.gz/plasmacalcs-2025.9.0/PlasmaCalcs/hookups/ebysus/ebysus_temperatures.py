"""
File Purpose: EbysusTemperaturesLoader

[TODO][MV] this probably belongs in a different file;
most of it would also apply to any other fluid models.
"""

from ...quantities import QuantityLoader

class EbysusTemperaturesLoader(QuantityLoader):
    '''temperature calculations.'''
    @known_var(deps=['Tjoule', 'u', 'm'])
    def get_vsqr(self):
        '''Average particle v^2 amongst all particles in each grid cell,
        as if the grid cell had particles in it (i.e., can be inferred even for fluid models).

        vsqr = (kB Ta / m) + u^2
        Ta = anisotropic temperatures. For Ebysus, use Ta == T.

        Inferred from temperature & velocity in cell:
            kB Ta = m * <(v - u)^2>, where u = <v>. This is the definition of Ta.
                Here, the averaging is taken across many particles.
                (T within a grid cell includes only the particles in the cell;
                "global" T across many cells includes all particles in all those cells.)
            Simplifying yields kB Ta == m * (<v^2> - 2<v>u + u^2) == m * (<v^2> - u^2).
            Thus, it is possible to infer <v^2> within a cell from T aand u in that cell:
                <v^2>_cell = (kB Ta_cell / m) + u_cell^2
        '''
        Tjoule = self('Tjoule')  # == kB * T   # uses Ta == T for Ebysus.
        return (Tjoule / self('m')) + self('u')**2

    @known_pattern(r'T(a)?(joule)?_global', deps=['vsqr', 'nmean_u', 'm'])
    def get_T_global(self, var, *, _match=None):
        '''quantity whose density-weighted mean is the global temperature,
        when all particles across the box are considered, as if the system had particles in it.

        Tjoule --> result will be in energy units.
        T (not Ta) --> take rms of components of result, e.g. sqrt((Tx^2 + Ty^2 + Tz^2) / 3)

        Tajoule_global = m * (vsqr - (nmean_u)^2)
            == kB Ta + m*u^2 - m*(nmean_u)^2
        Note that nmean(Ta_global) does NOT equal nmean(Ta). Instead:
            nmean(kB Ta_global) = nmean(kB Ta) + m*nmean(u^2) - m*(nmean_u)^2

        "DERIVATION" / EXPLANATION:
            kB Ta = m * <(v - u)^2>, where u = <v>.
            Simplifying yields kB Ta == m * (<v^2> - 2<v>u + u^2) == m * (<v^2> - u^2).
            Note that taking an average across all particles is equivalent to a
                density-weighted average across all cells, as density scales with number of particles.
                (This doesn't apply directly to T because particles don't have individual values of T,
                but it does apply to <v^2> and <v> because particles do have individual values of v.)
            Using the equation above to infer T across all particles:
                kB nmean_Ta_global = m * <v^2> - <v>^2,
                where <v^2> are the means of cell values, taken across all particles:
                --> kB nmean_Ta_global = m * (nmean(<v^2>_cell) - (nmean_u)^2)

            Ta_global is defined as the quantity whose nmean satisfies the relationship above. i.e.:
                kB Ta_global = m * <v^2>_cell - nmean_u^2

            As described in get_vsqr, we can also infer <v^2> within a cell:
                <v^2>_cell = (kB Ta_cell / m) + u_cell^2
            If desired, these can be combined, to see:
                kB Ta_global = kB Ta + m * (u_cell^2 - nmean_u^2)
        '''
        anisotropic, joule = _match.groups()
        # if getattr(self, '_debug_Ta_global', False):
        #     print('_debugging - using alternate method for Ta_global')
        #     nmean_u = self('nmean_u')
        #     u2 = self('u**2')
        #     if joule:
        #         return self('Tjoule') + self('m/kB') * (u2 - nmean_u**2)
        #     else:
        #         return self('T') + self('m/kB') * (u2 - nmean_u**2)
        # else:
        const = self('m') if joule else self('m/kB')
        result = const * (self('vsqr') - self('nmean_u')**2)
        return result if anisotropic else self.rmscomps(result)

    @known_pattern(r'T(a)?(joule)?_global_correction', deps=['u', 'mean_u', 'm'])
    def get_T_global_correction(self, var, *, _match=None):
        '''m*(u^2 - (nmean_u)^2) / kB
        Ta_global_correction + Ta == Ta_global.

        if Tajoule, don't divide by kB (answer will be in energy units).
        it T (not Ta), take rms of components.

        see self.help('T_global') for more detailed explanation.
        '''
        anisotropic, joule = _match.groups()
        const = self('m') if joule else self('m/kB')
        result = const * (self('u')**2 - self('nmean_u')**2)
        return result if anisotropic else self.rmscomps(result)

    @known_var(deps=['rmscomps_nmean_Ta_global'], ignores_dims=['component'])
    def get_T_box(self):
        '''temperature of the entire simulation box, as if full of particles,
        and observed by something that could not resolve the individual cells.

        Ignores Ta components for directions in which the box has no extent.
        (E.g. 512x512x1 box --> ignore Tz.)

        See self.help('rmscomps_nmean_Ta_global') for more details.
        '''
        return self('rmscomps_nmean_Ta_global', component=self.maindims_with_extent())
