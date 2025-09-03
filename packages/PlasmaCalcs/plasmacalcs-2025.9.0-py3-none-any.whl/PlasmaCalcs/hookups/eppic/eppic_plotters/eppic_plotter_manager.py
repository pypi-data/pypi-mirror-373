"""
File Purpose: EppicPlotterManager which inherits from all the other EppicPlotterManagers here.
"""

from .eppic_plotters_sam import EppicPlotterManagerSam
from .eppic_plotters_save import EppicPlotterManagerSave

class EppicPlotterManager(EppicPlotterManagerSam, EppicPlotterManagerSave):
    '''PlotterManager inheriting from everyone's plotter manager codes here.'''
    # all functionality inherited from parents.
    pass
