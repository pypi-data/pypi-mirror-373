"""
File Purpose: testing array-related methods
"""
import pytest

import PlasmaCalcs as pc

def test_fractional_indexing():
    '''tests that interprets_fractional_indexing works as intended.'''
    # leave ints unchanged
    ints = [0, 1, 2, 3, 4, 5, -1, -2, -3, -4, -5]
    for i in ints:
        assert i == pc.interprets_fractional_indexing(i)
        assert slice(i) == pc.interprets_fractional_indexing(slice(i))
        assert slice(None, i) == pc.interprets_fractional_indexing(slice(None, i))
        assert slice(None, None, i) == pc.interprets_fractional_indexing(slice(None, None, i))
    # handle list
    assert ints == pc.interprets_fractional_indexing(ints)
    # handle fractions when L is provided
    ## 0.5 --> halfway through the list
    ### for odd lengths, that is the unique middle index (regardless of rounding)
    odds = [3, 5, 7, 9, 27, 123, 999]
    for L in odds:
        I = (L-1)//2
        assert I == pc.interprets_fractional_indexing(0.5, L=L)
        for rounding in ('round', 'int', 'floor', 'ceil'):
            assert I == pc.interprets_fractional_indexing(0.5, L=L, rounding=rounding)
        ## also check that -0.5 works as expected:
        assert -I == pc.interprets_fractional_indexing(-0.5, L=L)
        for rounding in ('round', 'int', 'floor', 'ceil'):
            assert -I == pc.interprets_fractional_indexing(-0.5, L=L, rounding=rounding)
        ## also check that slices & iterables work as expected:
        assert slice(I, None, None) == pc.interprets_fractional_indexing(slice(0.5, None, None), L=L)
        assert slice(None, I, None) == pc.interprets_fractional_indexing(slice(None, 0.5, None), L=L)
        assert slice(None, None, I) == pc.interprets_fractional_indexing(slice(None, None, 0.5), L=L)
        assert slice(-7, 200, I) == pc.interprets_fractional_indexing(slice(-7, 200, 0.5), L=L)
        assert [0, -1, I, 2, -2, 1, I] == pc.interprets_fractional_indexing([0, -1, 0.5, 2, -2, 1, 0.5], L=L)
    ### for even lengths, 0.5 depends on rounding.
    evens = [4, 6, 8, 10, 28, 124, 1000]
    for L in evens:
        Ifloor = L//2 - 1
        Iceil = L//2
        assert Ifloor == pc.interprets_fractional_indexing(0.5, L=L, rounding='floor')
        assert Iceil == pc.interprets_fractional_indexing(0.5, L=L, rounding='ceil')
        ## also check that -0.5 works as expected (abs for floor & ceil swap below 0):
        assert -Ifloor == pc.interprets_fractional_indexing(-0.5, L=L, rounding='ceil')
        assert -Iceil == pc.interprets_fractional_indexing(-0.5, L=L, rounding='floor')
    # handle exceptions / edge cases
    inputs = [0.2, -0.7,
            slice(0.2, 10), slice(-0.7, 10), slice(-100, 0.3),
            [0.2, 0.3, -0.7, 0.5], [100, -8, 0.3, 9, 10]]
    ## crash when L not provided but fractional indexing is required:
    for i in inputs:
        with pytest.raises(pc.InputMissingError):
            pc.interprets_fractional_indexing(i)  # didn't provide L but fractional indexing required.
    ## crash when L <= 1 but only if fractional indexing is required:
    for i in inputs:
        with pytest.raises(ValueError):
            pc.interprets_fractional_indexing(i, L=0)
        with pytest.raises(ValueError):
            pc.interprets_fractional_indexing(i, L=1)
        with pytest.raises(ValueError):
            pc.interprets_fractional_indexing(i, L=-20)
    assert pc.interprets_fractional_indexing(7, L=0) == 7   # no crash; fractional indexing not required.
    assert pc.interprets_fractional_indexing(slice(0, 7, 3), L=1) == slice(0, 7, 3)
    assert pc.interprets_fractional_indexing([9, 8, 2, -7, 5], L=-20) == [9, 8, 2, -7, 5]
