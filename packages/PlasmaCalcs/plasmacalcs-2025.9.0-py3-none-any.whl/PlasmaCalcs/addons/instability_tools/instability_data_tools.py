"""
File Purpose: helpful tools for processing data with physical instability in it

E.g. "get t when linear growth ends", "measure growth rate"
"""

import numpy as np

from .instability_xarray_accessor import itAccessor
from ...tools import (
    format_docstring,
    alias,
    XarrayCurveFitter,
)

### --------------------- fitting --------------------- ###
# (instead of managing theory & theoretical solutions)
# e.g. measure growth rate, t_turb when turbulence begins, saturation level.


def pwl2_flatend(xx, b0, m0, end0):
    '''evaluate xx at piecewise linear function with 2 pieces, with final piece slope=0.
    
    xx: 1D array. Assumed to be monotonically increasing.
    b0: y-intercept of piece 0
    m0: slope of piece 0
    end0: "index" of end of piece 0
        if end0 is not an int, does weighted averaging of xx[int(end0)] and xx[int(end0)+1].
        E.g. end0 = 10.25 --> extend piece 0 to xx[10] + 0.25 * (xx[11] - xx[10])

    b1 is computed based on the other inputs.

    This is a decent approx. for ln(val) with linear growth then saturation.
        xx <--> time
        b0 <--> pre-growth noise level
        m0 <--> growth rate
        end0 <--> "saturation index" when linear growth stops.
        x0 <--> "saturation time" when linear growth stops, where:
                x0 = xx[i0] + (end0 - i0) * (xx[i0+1] - xx[i0], where i0 = int(end0).
        y0  <--> "saturation level"; value when saturated, where:
                y0 = m0 * x0 + b0.
    '''
    # assumptions
    m1 = 0
    # piecewise linear math
    yy0 = m0 * xx + b0
    iend0 = int(end0)
    rounded = end0 - iend0
    x0 = xx[iend0] + rounded * (xx[iend0+1] - xx[iend0])
    y0 = m0 * x0 + b0  # evaluate piece 0 at endpoint.
    b1 = y0 - m1 * x0
    yy1 = m1 * xx + b1
    # add yy * (1 if xindex in section else 0)
    sec0 = np.zeros_like(xx)
    sec0[:iend0+1] = 1  # piece 0 includes the iend0 point
    sec1 = np.zeros_like(xx)
    sec1[iend0+1:] = 1
    return yy0 * sec0 + yy1 * sec1

def pwl3_flatend(xx, b0, m0, end0, m1, end1add):
    '''evaluate xx at piecewise linear function with 3 pieces, with final piece slope=0.

    xx: 1D array. Assumed to be monotonically increasing.
    b0: y-intercept of piece 0
    m0: slope of piece 0
    end0: "index" of end of piece 0
        if end0 is not an int, does weighted averaging of xx[floor(end0)] and xx[ceil(end0)].
        E.g. end0 = 10.25 --> extend piece 0 to xx[10] + 0.25 * (xx[11] - xx[10])
    m1: slope of piece 1
    end1add: "index" of end of piece 1, minus end0.
        end1 = end0 + end1add.  (max=len(xx)-1)
        if end1 is not an int, handle similarly to end0 (see above).

    b2 is computed based on the other inputs.

    This is a decent approx. for ln(val) with linear growth, then damped linear growth, then saturation.
        xx <--> time
        b0 <--> pre-growth noise level
        m0 <--> growth rate of linear growth
        end0 <--> "damped index" when linear growth stops.
        x0 <--> "damped time" when linear growth stops, where:
                x0 = xx[i0] + (end0 - i0) * (xx[i0+1] - xx[i0], where i0 = int(end0).
        y0 <--> pre-damped-growth level, where:
                y0 = m0 * x0 + b0.
                (--> damped growth piece has y-intercept b1 = y0 - m1 * x0.)
        m1 <--> growth rate of damped linear growth
        end1 <--> "saturation index" when damped growth stops, where:
                end1 = end0 + end1add
        x1 <--> "saturation time" when damped growth stops, where:
                x1 = xx[i1] + (end1 - i1) * (xx[i1+1] - xx[i1], where i1 = int(end1).
        y1 <--> "saturation level"; value when saturated, where:
                y21= m1 * x1 + b1.
    '''
    # assumptions
    m2 = 0
    end1 = end0 + end1add
    if end1 > len(xx)-2:
        end1 = len(xx)-2
    # piecewise linear math
    yy0 = m0 * xx + b0
    iend0 = int(end0)
    rounded0 = end0 - iend0
    x0 = xx[iend0] + rounded0 * (xx[iend0+1] - xx[iend0])
    y0 = m0 * x0 + b0  # evaluate piece 0 at endpoint.
    b1 = y0 - m1 * x0
    yy1 = m1 * xx + b1
    iend1 = int(end1)
    rounded1 = end1 - iend1
    x1 = xx[iend1] + rounded1 * (xx[iend1+1] - xx[iend1])
    y1 = m1 * x1 + b1  # evaluate piece 1 at endpoint.
    b2 = y1 - m2 * x1
    yy2 = m2 * xx + b2
    # add yy * (1 if xindex in section else 0)
    sec0 = np.zeros_like(xx)
    sec0[:iend0+1] = 1  # piece 0 includes the iend0 point
    sec1 = np.zeros_like(xx)
    sec1[iend0+1:iend1+1] = 1  # piece 1 includes the iend1 point
    sec2 = np.zeros_like(xx)
    sec2[iend1+1:] = 1
    return yy0 * sec0 + yy1 * sec1 + yy2 * sec2


@itAccessor.register('pwl2_flatend_fitter', totype='array')
@format_docstring(pwl2_flatend_docs=pwl2_flatend.__doc__)
class Pwl2FlatendFitter(XarrayCurveFitter):
    '''CurveFitter with f = pwl2_flatend, for fitting data to piecewise linear with 2 pieces.
    When fitting, use bounds:
        m0 > 0.
        1 <= end0 <= len(xdata)-2

    pwl2_flatend docs copied below, for convenience:
    ------------------------------------------------
    {pwl2_flatend_docs}
    '''
    f = staticmethod(pwl2_flatend)
    pnames = ['b0', 'm0', 'end0']
    pbounds = [
        None,
        (0, None),
        (1, lambda arr, xdim: arr.sizes[xdim]-2)
    ]

    get_xsat = alias('get_x0', doc='''x value at start of saturation. alias to self.get_x0.''')

    def get_x0(self):
        '''return x0, the x value at the end of piece 0.
        (Crashes if run before self.fit())

        x0 = xx[i0] + (end0 - i0) * (xx[i0+1] - xx[i0], where i0 = int(end0).

        [TODO] option to get result +-1 stddev error bounds.
        '''
        xdata = self.xdata
        end0 = self.params.to_dataset('param')['end0']
        iend0 = end0.astype(int)
        round0 = end0 - iend0
        dim = self.dim
        x_at_iend0 = xdata.isel({dim: iend0})
        x_at_iend0_p1 = xdata.isel({dim: iend0+1})
        x0 = x_at_iend0 + round0 * (x_at_iend0_p1 - x_at_iend0)
        return x0

    get_ysat = alias('get_y0', doc='''saturation level (y-value). alias to self.get_y0.''')

    def get_y0(self):
        '''return y0, the y value at the end of piece 0.
        (Crashes if run before self.fit())

        y0 = m0 * x0 + b0.

        [TODO] option to get result +-1 stddev error bounds.
        '''
        x0 = self.get_x0()
        pds = self.params.to_dataset('param')
        m0 = pds['m0']
        b0 = pds['b0']
        y0 = m0 * x0 + b0
        return y0


@itAccessor.register('pwl3_flatend_fitter', totype='array')
@format_docstring(pwl3_flatend_docs=pwl3_flatend.__doc__)
class Pwl3FlatendFitter(XarrayCurveFitter):
    '''CurveFitter with f = pwl3_flatend, for fitting data to piecewise linear with 3 pieces.
    When fitting, use bounds:
        m0, m1 > 0
        1 <= end0 <= len(xdata)-3
        2 <= end1add <= len(xdata)-2

    # [TODO] It would be good to force end0 + end1add < len(xdata)-1. But I don't know how to.

    pwl3_flatend docs copied below, for convenience:
    ------------------------------------------------
    {pwl3_flatend_docs}
    '''
    f = staticmethod(pwl3_flatend)
    pnames = ['b0', 'm0', 'end0', 'm1', 'end1add']
    pbounds = [
        None,
        (0, None),
        (1, lambda arr, xdim: arr.sizes[xdim]-3),
        (0, None),
        (2, lambda arr, xdim: arr.sizes[xdim]-2),
    ]


    def get_x0(self):
        '''return x0, the x value at the end of piece 0.
        (Crashes if run before self.fit())

        x0 = xx[i0] + (end0 - i0) * (xx[i0+1] - xx[i0], where i0 = int(end0).

        [TODO] option to get result +-1 stddev error bounds.
        '''
        xdata = self.xdata
        end0 = self.params.to_dataset('param')['end0']
        iend0 = end0.astype(int)
        round0 = end0 - iend0
        dim = self.dim
        x_at_iend0 = xdata.isel({dim: iend0})
        x_at_iend0_p1 = xdata.isel({dim: iend0+1})
        x0 = x_at_iend0 + round0 * (x_at_iend0_p1 - x_at_iend0)
        return x0

    def get_y0(self):
        '''return y0, the y value at the end of piece 0.
        (Crashes if run before self.fit())

        y0 = m0 * x0 + b0.

        [TODO] option to get result +-1 stddev error bounds.
        '''
        x0 = self.get_x0()
        pds = self.params.to_dataset('param')
        m0 = pds['m0']
        b0 = pds['b0']
        y0 = m0 * x0 + b0
        return y0

    get_xsat = alias('get_x1', doc='''x value at start of saturation. alias to self.get_x1.''')

    def get_x1(self):
        '''return x1, the x value at the end of piece 1.
        (Crashes if run before self.fit())

        x1 = xx[i1] + (end1 - i1) * (xx[i1+1] - xx[i1], where i1 = int(end1),
        and end1 = end0 + end1add.

        [TODO] option to get result +-1 stddev error bounds.
        '''
        xdata = self.xdata
        pds = self.params.to_dataset('param')
        end0 = pds['end0']
        end1add = pds['end1add']
        end1 = end0 + end1add
        iend1 = end1.astype(int)
        round1 = end1 - iend1
        dim = self.dim
        x_at_iend1 = xdata.isel({dim: iend1})
        x_at_iend1_p1 = xdata.isel({dim: iend1+1})
        x1 = x_at_iend1 + round1 * (x_at_iend1_p1 - x_at_iend1)
        return x1

    get_ysat = alias('get_y1', doc='''saturation level (y-value). alias to self.get_y1.''')

    def get_y1(self):
        '''return y1, the y value at the end of piece 1.
        (Crashes if run before self.fit())

        y1 = m1 * x1 + b1.

        [TODO] option to get result +-1 stddev error bounds.
        '''
        x1 = self.get_x1()
        pds = self.params.to_dataset('param')
        m1 = pds['m1']
        b1 = pds['b1']
        y1 = m1 * x1 + b1
        return y1
