"""
File Purpose: Dimension values & lists for Ebysus
"""

from ...dimensions import Fluid, FluidList


### --------------------- EbysusFluid and EbysusFluidList --------------------- ###

class EbysusFluid(Fluid):
    '''a single Fluid for Ebysus. Similar to Fluid but also knows about SL.
    SL tells (ispecie, ilevel). SL will always internally be stored as tuple(SL).
    '''
    _kw_def = {'name', 'i', 'm', 'q', 'SL'}

    def __init__(self, name=None, i=None, *, m=None, q=None, SL=None):
        super().__init__(name=name, i=i, m=m, q=q)
        self.SL = tuple(SL)  # storing as tuple prevents crash if SL is array,
        # if checking whether SL here == other SL. (Numpy requires using np.all(SL0==SL1)).

    def _repr_contents(self):
        '''contents used by self.__repr__'''
        result = super()._repr_contents()
        if self.SL is not None:
            result.append(f'SL={self.SL}')
        return result


class EbysusFluidList(FluidList):
    '''a list of EbysusFluid objects.'''
    value_type = EbysusFluid

    # pass... all other behavior is inherited from FluidList.
