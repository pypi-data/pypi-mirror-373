"""
File Purpose: the most basic of tests - import & initialize.

Also, clears global artifacts folder if it exists.
"""
import os

# BASIC TESTS
def test_import():
    '''ensure can import PlasmaCalcs'''
    import PlasmaCalcs as pc

def test_init():
    '''ensure can initialize some objects from PlasmaCalcs'''
    import PlasmaCalcs as pc
    p = pc.PlasmaCalculator()
    