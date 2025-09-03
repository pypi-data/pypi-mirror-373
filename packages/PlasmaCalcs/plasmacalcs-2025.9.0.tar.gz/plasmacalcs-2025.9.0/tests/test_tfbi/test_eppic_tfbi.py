"""
File Purpose: test solving TFBI theory, from eppic inputs
TFBI = Thermal Farley-Buneman Instability.

See e.g.:
    - [Evans+2025](https://doi.org/10.3847/1538-4357/adcd70)
    - [Evans+2023](https://doi.org/10.3847/1538-4357/acc5e5)
    - [tfbi_theory](https://pypi.org/project/tfbi_theory)
    - PlasmaCalcs/examples/tfbi_theory.ipynb
"""
import os

import matplotlib.pyplot as plt
import numpy as np

import PlasmaCalcs as pc

HERE = os.path.dirname(__file__)
INPUT_DECKS = os.path.join(HERE, 'test_tfbi_inputs')
TESTS_DIR = os.path.dirname(HERE)
ARTIFACTS = os.path.join(TESTS_DIR, '_test_artifacts', 'tfbi')
if os.path.exists(ARTIFACTS):  # remove any xarray_io artifacts before running tests.
    import shutil; shutil.rmtree(ARTIFACTS)
os.makedirs(ARTIFACTS)

### --------------------- helper functions --------------------- ###

def get_ec(eppic_i, u_t=1, kw_units=dict(M=1), **kw_init):
    '''make an eppic calculator with SI units by default'''
    with pc.InDir(INPUT_DECKS):
        ec = pc.EppicCalculator.from_here(eppic_i, u_t=u_t, kw_units=kw_units, **kw_init)
    return ec

def get_ec_2a(**kw_ec):
    '''get_ec('eppic_2a_tinybox.i')'''
    return get_ec('eppic_2a_tinybox.i', **kw_ec)

def savefig_and_close(name, *, bbox_inches='tight', **kw):
    '''savefig to ARTIFACTS/name, then plt.close().'''
    plt.savefig(os.path.join(ARTIFACTS, name), bbox_inches=bbox_inches, **kw)
    plt.close()


### --------------------- ensure can import tfbi_theory --------------------- ###

def test_import_tfbi_theory():
    '''ensure that tfbi_theory can be imported'''
    import tfbi_theory


### --------------------- solve TFBI from eppic params --------------------- ###

def test_solve_tfbi_2a():
    '''solve TFBI theory directly from eppic params.'''
    ec = get_ec_2a()
    ec.snap = pc.INPUT_SNAP  # don't look for snapshot data; get vals from input deck.
    solver = ec.tfbi_solver()
    with pc.TimeLimit(20):  # (should only take ~5 seconds. Crash if taking way too long.)
        dsR = solver.solve()
    # make and save plot (auto test just ensures it doesn't crash; can inspect by eye later.)
    dsR.it.growthplot()
    savefig_and_close('tfbi_2a_growthplot.png')
    # compare with known solution:
    #  ("known" meaning: I checked it when originally making test)
    assert np.abs(dsR.it.growth_kmax() - 1353) < 10
    assert np.isclose(np.rad2deg(dsR.it.kang_at_growmax()), 60)


### --------------------- solve TFBI from "sort of" eppic params --------------------- ###

def test_solve_tfbi_2a_ish():
    '''solve TFBI theory from eppic params but varying some params artificially.'''
    ec = get_ec_2a()
    ec.snap = pc.INPUT_SNAP  # don't look for snapshot data; get vals from input deck.
    tfbivals0 = ec.tfbi_ds()   # other options include: ec('tfbi_inputs'), ec('tfbi_all')
    Etest = pc.xr1d([4, 6, 10, 20], 'E_test')
    tfbivals = tfbivals0.assign({'E_un0_perpmod_B': Etest})
    cc = pc.InstabilityCalculator(tfbivals)
    cc_tfbivals = cc.tfbi_ds()
    # ensure recomputing eqperp_ldebye using new E.
    #  (tfbivals0['eqperp_ldebye'] doesn't vary with E_test.)
    assert 'E_test' in cc_tfbivals['eqperp_ldebye'].dims
    # solve TFBI theory, use higher kres
    #   also use larger mod range so that more klines can be checked by eye.
    solver = cc.tfbi_solver(kres='mid', mod=dict(min=10**-1, max=10**3.5))
    with pc.TimeLimit(20):  # (should only take ~5 seconds. Crash if taking way too long.)
        dsR = solver.solve()
    # make and save plot (auto test just ensures it doesn't crash; can inspect by eye later.)
    dsR.it.growthplots(share_vlims='all')  # share_vlims to use same colorbar for all plots
    savefig_and_close('tfbi_2a_growthplots_Etest.png')
    # use InstabilityCalculator interface to compute some values, to ensure it works
    cc2 = pc.InstabilityCalculator(dsR)
    # compare with known solution:
    #  ("known" meaning: I checked it when originally making test)
    growthmax = cc2('growth_kmax')  # max growth rate (max taken across k) at each point
    assert growthmax.isel(E_test=0).item() < 0  # no growth at E==4
    assert np.allclose(growthmax.isel(E_test=slice(1,None)), [810,  2290,  3560], rtol=1e-2, atol=0)
    kang = cc2('rad2deg_kang_at_growmax').isel(E_test=slice(1,None))
    assert np.allclose(kang, [57., 63., 72.], rtol=1e-4, atol=2)
    kmod = cc2('kmod_at_growmax').isel(E_test=slice(1,None))
    assert np.allclose(kmod, [7.28, 5.09, 3.56], rtol=1e-2, atol=0)
