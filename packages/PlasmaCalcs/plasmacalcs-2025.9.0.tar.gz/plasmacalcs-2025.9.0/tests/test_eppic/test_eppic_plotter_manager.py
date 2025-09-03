"""
File Purpose: test eppic PlotterManager.
NOTE: plot color scheme would look nicer if you first do: import colorcet
However, tests should still pass even if colorcet import fails.
"""
import os

import PlasmaCalcs as pc
pc.DEFAULTS.pic_ambiguous_unit = dict(u_t=1)  # must be defined before loading an EppicCalculator.

HERE = os.path.dirname(__file__)
TESTS_DIR = os.path.dirname(HERE)
ARTIFACTS = os.path.join(TESTS_DIR, '_test_artifacts', 'eppic_plotter_manager')
if os.path.exists(ARTIFACTS):  # remove any xarray_io artifacts before running tests.
    import shutil; shutil.rmtree(ARTIFACTS)
# <-- don't makedirs here; xarray_save should makedirs as needed.


def get_eppic_calculator(**kw_init):
    '''make an eppic calculator'''
    with pc.InDir(os.path.join(HERE, 'test_eppic_tinybox')):
        ec = pc.EppicCalculator.from_here(**kw_init)
    return ec

### --------------------- sam_plots --------------------- ###

# takes ~15 to 25 seconds
def test_eppic_sam_plots_lowres():
    '''ensures EppicCalculator.sam_plots_lowres doesn't crash.

    This tests a good chunk of PlotterManager functionality,
        by running the initial group of plotters sam uses for quick eppic analysis.

    [TODO] It would also be nice to add some sort of test for correctness too...
    '''
    ec = get_eppic_calculator()
    # for tinybox, the default fft_keep of 0.1 is too small to show anything!
    ec.sam_defaults['fft_calcs']['fft_keep'] = 0.8
    # mini-test: ensure that^ only changed the default for this instance, not all instances.
    assert pc.EppicCalculator.SAM_DEFAULTS['fft_calcs']['fft_keep'] < 0.8
    # we can reduce the dpi slightly (default 100 here); people usually won't look at these plots...
    dpi = 70
    # let's put the plots in ARTIFACTS/sam_plots_lowres
    # '{savename}' is recognized by the ec.sam_plots_lowres
    dst = os.path.join(ARTIFACTS, 'sam_plots_lowres', '{savename}')
    # here, just ensuring it doesn't crash!
    ec.sam_plots_lowres(dst=dst, dpi=dpi)
