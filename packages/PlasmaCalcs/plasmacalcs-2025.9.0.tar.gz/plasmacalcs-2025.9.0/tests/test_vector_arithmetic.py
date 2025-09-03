"""
File Purpose: test vector arithmetic patterns from quantity loader.
"""
import PlasmaCalcs as pc

import numpy as np


def test_vector_arithmetic_basics():
    '''tests basics of vector arithmetic.'''
    p = pc.PlasmaCalculator()  # plasma calculator object not associated with any files.
    # components dimension
    assert len(p.components) == 3
    p.component = None  # use all components
    assert len(p.component) == 3
    assert p.components == pc.XYZ
    assert p.components == ['x', 'y', 'z']
    assert p.components == [0, 1, 2]
    assert p.components == ['x', 1, pc.XYZ[2]]
    # unit vectors & components
    assert np.all(p('xhat') == pc.XHAT)
    assert np.all(p('yhat') == pc.YHAT)
    assert np.all(p('zhat') == pc.ZHAT)
    for (x, y, z) in ('xyz', 'yzx', 'zxy'):
        assert p(f'{x}hat_{x}').item() == 1   # {x}hat == 1 in the {x} direction
        assert p(f'{x}hat_{y}').item() == 0   # {x}hat == 0 in the {y} direction
        assert p(f'{x}hat_{z}').item() == 0   # {x}hat == 0 in the {z} direction
    # composing vectors from components
    assert np.all(p('-xhat') == -p('xhat'))
    assert np.all(p('-xhat') == [-1, 0, 0])
    assert np.all(p('xhat*7') == [7, 0, 0])
    assert np.all(p('3*yhat+2*zhat') == [0, 3, 2])
    assert np.all(p('xhat*7+yhat*3+zhat*2') == [7, 3, 2])
    assert np.all(p('-xhat*7+3*yhat-zhat*2') == [-7, 3, -2])
    # dot products of pairs of unit vectors
    for x in 'xyz':
        for y in 'xyz':
            assert p(f'{x}hat_dot_{y}hat').item() == (x == y)
    # dot products of vectors composed of unit vectors
    assert p('(3*xhat)_dot_xhat').item() == 3
    assert p('(3*xhat+2*yhat)_dot_xhat') == 3
    assert p('(3*xhat+2*yhat)_dot_yhat') == 2
    assert p('(3*xhat+2*yhat)_dot_zhat') == 0
    assert p('(3*xhat+yhat+4*zhat)_dot_(7*xhat+50*zhat)') == 7*3 + 50*4
    # cross products of pairs of unit vectors
    assert np.all(p('xhat_cross_yhat') == p('zhat'))
    assert np.all(p('yhat_cross_zhat') == p('xhat'))
    assert np.all(p('zhat_cross_xhat') == p('yhat'))
    assert np.all(p('yhat_cross_xhat') == p('-zhat'))
    assert np.all(p('zhat_cross_yhat') == p('-xhat'))
    assert np.all(p('xhat_cross_zhat') == p('-yhat'))
    # cross products of vectors composed of unit vectors
    assert np.all(p('(3*xhat)_cross_xhat') == 0)
    assert np.all(p('(3*xhat+2*yhat)_cross_xhat') == [0, 0, -2])
    assert np.all(p('(3*xhat+2*yhat)_cross_xhat') == p('-2*zhat'))
    assert np.all(p('(3*xhat+2*yhat)_cross_yhat') == p('3*zhat'))
    assert np.all(p('(3*xhat+2*yhat)_cross_yhat') == [0, 0, 3])
    assert np.all(p('(3*xhat+2*yhat)_cross_zhat') == p('2*xhat-3*yhat'))
    assert np.all(p('(3*xhat+2*yhat)_cross_zhat') == p('-3*yhat+2*xhat'))
    assert np.all(p('(3*xhat+2*yhat)_cross_zhat') == [2, -3, 0])
    assert np.all(p('(3*xhat+yhat+4*zhat)_cross_(7*xhat+50*zhat)') == [1*50, -3*50 + 7*4, -1*7])  # [50, -122, -7]
    # using cross product & dot product functions directly:
    for xhat in (pc.XHAT, pc.YHAT, pc.ZHAT):
        for yhat in (pc.XHAT, pc.YHAT, pc.ZHAT):
            assert np.all(pc.dot_product(xhat, yhat).item() == (xhat is yhat))
    assert np.all(pc.cross_product(pc.XHAT, pc.YHAT) == pc.ZHAT)
    assert np.all(pc.cross_product(pc.YHAT, pc.ZHAT) == pc.XHAT)
    assert np.all(pc.cross_product(pc.ZHAT, pc.XHAT) == pc.YHAT)
    assert np.all(pc.cross_product(pc.YHAT, pc.XHAT) == -pc.ZHAT)
    assert np.all(pc.cross_product(pc.ZHAT, pc.YHAT) == -pc.XHAT)
    assert np.all(pc.cross_product(pc.XHAT, pc.ZHAT) == -pc.YHAT)
