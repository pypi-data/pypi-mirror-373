"""
File Purpose: calculating stats especially relevant to plasma
"""

from .patterns import StatsLoader

class PlasmaStatsLoader(StatsLoader):
    '''plasma stats, e.g. mean weighted by n.'''
    @known_pattern(r'nmean_(.+)', deps=[0])
    def get_nmean(self, var, *, _match=None):
        '''mean of var, weighted by n. nmean = sum(var * n) / sum(n). n=self('n').
        Equivalent: 'nmean_var' <--> 'weighted_n_mean_var'
        '''
        var, = _match.groups()
        return self(f'weighted_n_mean_{var}')

    @known_pattern(r'nstd_(.+)', deps=[0])
    def get_nstd(self, var, *, _match=None):
        '''std of var, weighted by n. nstd = std(n*var)/mean(n), with n=self('n').'''
        var, = _match.groups()
        return self(f'weighted_n_std_{var}')
