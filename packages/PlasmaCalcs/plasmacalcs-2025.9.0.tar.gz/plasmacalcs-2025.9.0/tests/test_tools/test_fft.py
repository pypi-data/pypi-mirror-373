"""
File Purpose: testing fft-related tools.
"""

import pytest

import PlasmaCalcs as pc


def test_fft_dimname():
    '''test FFTDimname class.'''
    # test creation
    pc.FFTDimname('x')   # should not crash
    pc.FFTDimname('x', rad=True)   # should not crash
    K_X = pc.DEFAULTS.FFT_FREQ_RAD_DIMNAMES.get('x', 'freqrad_x')
    assert K_X != 'freqrad_x'  # <-- if x removed from DEFAULTS.FFT_FREQ_RAD_DIMNAMES, can remove this line.
    # test from_post
    for postname, postrad in [('freq_x', False), ('freqrad_x', True), (K_X, True)]:
        dimname = pc.FFTDimname.from_post(postname, rad=None)
        assert dimname.name == 'x'
        assert dimname.rad == postrad
        pc.FFTDimname.from_post(postname, rad=postrad)  # should not raise error.
        with pytest.raises(pc.DimensionKeyError):
            pc.FFTDimname.from_post(postname, rad=not postrad)  # should raise error.
    # test __str__
    assert str(pc.FFTDimname('x')) == 'freq_x'
    assert str(pc.FFTDimname('x', rad=True)) == K_X
    # test implied_from
    for rad in (None, True, False):
        assert pc.FFTDimname.implied_from('x', ['x', 'y'], rad=rad) == pc.FFTDimname('x', rad=rad)
    assert pc.FFTDimname.implied_from(K_X, ['x', 'y']) == pc.FFTDimname('x', rad=True)
    assert pc.FFTDimname.implied_from('freq_x', ['x', 'y']) == pc.FFTDimname('x', rad=False)
    assert pc.FFTDimname.implied_from('x', [K_X, 'k_y'], post_fft=True) == pc.FFTDimname('x', rad=True)
    assert pc.FFTDimname.implied_from(K_X, [K_X, 'k_y'], post_fft=True) == pc.FFTDimname('x', rad=True)
    with pytest.raises(pc.DimensionKeyError):
        pc.FFTDimname.implied_from('freq_x', [K_X, 'k_y'], post_fft=True)
    with pytest.raises(pc.DimensionKeyError):
        pc.FFTDimname.implied_from('x', ['k_y', 't'])
    assert pc.FFTDimname.implied_from('x', ('fluid', 'x', 'y', 't')) == pc.FFTDimname('x')
