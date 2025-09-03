"""
File Purpose: quantities known when quasineutral=True
"""

from .quantity_loader import QuantityLoader

class QuasineutralLoader(QuantityLoader):
    '''quantities that require quasineutral=True.
    Usually, this just provides a different way to get an electron quantity,
        e.g. electron number density using assumption of quasineutrality.
    '''
    _quasineutral = False
    _assert_QN = True   # whether to assert self.quasineutral before doing any operation here.

    def __init__(self, quasineutral=None, **kw_super):
        if quasineutral is not None: self.quasineutral = quasineutral
        super().__init__(**kw_super)

    cls_behavior_attrs.register('quasineutral', default=False)
    @property
    def quasineutral(self):
        '''tells whether self is in quasineutral mode.'''
        return self._quasineutral
    @quasineutral.setter
    def quasineutral(self, value):
        '''set self.quasineutral, then call self.on_changed_quasineutral(old=old_value, new=new_value)'''
        old_qn = self._quasineutral
        if value is not old_qn:
            self._quasineutral = value
            self.on_changed_quasineutral(old=old_qn, new=value)

    def on_changed_quasineutral(self, *, old, new):
        '''called when self.quasineutral changes.
        default behavior: do nothing.
        '''
        pass

    def assert_QN(self):
        '''asserts self.quasineutral. if not self._assert_QN, instead does not assert self.quasineutral.'''
        if self._assert_QN and not self.quasineutral:
            raise AssertionError(f'Expected {type(self).__name__}.quasineutral=True, got {self.quasineutral}.')

    @known_var(deps=['nq', 'q'], ignores_dims=['fluid'])
    def get_ne(self):
        '''electron number density. (ne qe) + sum_i (ni qi) = 0. (using qe < 0 convention)'''
        self.assert_QN()
        niqi = self('nq', fluid=self.fluids.ions())
        qe = self('q', fluid=self.fluids.get_electron())
        return niqi / -qe
