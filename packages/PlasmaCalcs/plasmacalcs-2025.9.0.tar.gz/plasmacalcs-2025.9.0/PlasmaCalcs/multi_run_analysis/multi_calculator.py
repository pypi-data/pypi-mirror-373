"""
File Purpose: MultiCalculator
"""
import os

from .multi_run_tools import canon_runs
from ..tools import (
    DictOfSimilar,
)

class MultiCalculator(DictOfSimilar):
    '''a class to handle multiple calculators.

    Example:
        calc1 = PlasmaCalculator(...)
        calc2 = PlasmaCalculator(...)
        mc = MultiCalculator({'c1':calc1, 'c2':calc2})
        mc.snap = 0             # sets calc.snap=0 for all calcs
        mc['slices', 'x'] = 7   # sets calc.slices['x'] = 7 for all calcs
        mc('Eheat')             # returns list of calc('Eheat') for all calcs
    '''
    cls_new = DictOfSimilar  # results will be DictOfSimilar instead of MultiCalculator.

    def _get_similar_attrs(self):
        '''return SIMILAR ATTRS for self.
        This is the intersection of all kw_call_options from calculators in self.
        '''
        # [EFF] if this ever becomes slow, use caching.
        options = [set(calc.kw_call_options()) for calc in self.values()]
        return set.intersection(*options)

    SIMILAR_ATTRS = property(lambda self: self._get_similar_attrs(),
        doc='''SIMILAR_ATTRS for self; operations on self will be broadcasted to these attrs,
        e.g. self.snap = 0 --> [calc.snap for calc in self.values()], if 'snap' in SIMILAR_ATTRS.''')

    @property
    def title(self):
        '''return a title for self: f'{calc1.title}|{calc2.title}|...|{calcN.title}'.'''
        return '|'.join([calc.title for calc in self.values()])

    @classmethod
    def from_canon(cls, makecalc, *, dir=os.curdir, exclude=[], singles=True, abbrv=True):
        '''return MultiCalculator from canonical runs within directory (and subdirectories).
        A run is "canonical" if in a 'run' or 'runs' parameter in a _canon.txt file.
        Paths in _canon.txt file are relative to the same directory as the _canon.txt file.

        makecalc: callable
            function to make a calculator, given abspath of run's directory.
        dir: str
            directory to search for _canon.txt files.
        exclude: str, or list of strs
            exclude any subdirectories whose name equals one of these strings or re.fullmatch one of these strings.
            E.g. exclude='*[.]io' will exclude all subdirectories whose name ends with '.io';
                exclude='parallel' will exclude all subdirectories whose name equals 'parallel'.
        singles: bool
            if True, assert all run lists from _canon.txt files have length 1,
                and replace each runlist with runlist[0].
        abbrv: bool
            whether to use abbreviated names for result keys and calculator titles.
            abbreviated names determined by removing os.path.commonpath() of run dirs.
            calculator titles set via calculator.title = abbrv_name, for each calculator.
        '''
        if not singles:
            raise NotImplementedError('[TODO] from_canon when singles!=True')
        canons = canon_runs(dir=dir, exclude=exclude, singles=singles)
        result = {k: makecalc(os.path.join(k, v)) for k, v in canons.items()}
        if abbrv:
            commonpath = os.path.commonpath(canons)
            result = {os.path.relpath(k, commonpath): v for k, v in result.items()}
            for k, v in result.items():
                v.title = k
        return cls(result)
