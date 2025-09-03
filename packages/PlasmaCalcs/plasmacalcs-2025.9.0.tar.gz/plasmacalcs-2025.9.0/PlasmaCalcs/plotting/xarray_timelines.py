"""
File Purpose: plotting lines vs time for xarray.
"""
import itertools
#import warnings

import cycler
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .plot_settings import PlotSettings, PlotSettingsMixin
from .plot_tools import (
    current_axes_has_data,
    calculate_vlims, plt_zoomy,
)
from ..errors import (
    InputError, InputConflictError,
    PlottingAmbiguityError, TooManyPlottablesError,
    DimensionKeyError, DimensionError,
)
from ..tools import (
    UNSET,
    product, rargmax,
    pcAccessor, xarray_fill_coords, xarray_is_sorted, xarray_werr2pmstd,
    xarray_nondim_coords,
)

from ..defaults import DEFAULTS


class IndexableCycler(cycler.Cycler):
    '''Cycler which can be indexed by integers.
    Uses infinite indexing, i.e. result will be the same as the i'th value from itertools.cycle().
        [EFF] uses i % len(self), so the indexing time complexity doesn't scale with i.
    '''
    def __getitem__(self, i):
        '''return the ith element of the cycler, if i is an int.
        Otherwise use super().__getitem__.'''
        if isinstance(i, int):
            return list(self)[i % len(self)]
        else:
            return super().__getitem__(i)
        

### --------------------- XarrayTimelines --------------------- ###

@pcAccessor.register('timelines')
@PlotSettings.format_docstring(
        default_cycles=[DEFAULTS.PLOT.TIMELINES_CYCLE0, DEFAULTS.PLOT.TIMELINES_CYCLE1],
        default_dmax=DEFAULTS.PLOT.TIMELINES_DMAX,)
class XarrayTimelines(PlotSettingsMixin):
    '''plotting lines vs time for an xarray.

    array: xarray.DataArray or xarray.Dataset
        the array to plot.
        Must have coord or dimension with name self.t (probably 't' or 'snap').
        if dataset, will be converted to DataArray with new dim named 'variable'.
    t: str
        name for the time coordinate (to be plotted along the x axis).
        if 'snap', use int(snap) for snap in array.coords['snap'].
        if 'snap_str', use int(str(snap)) for snap in array.coords['snap']
        if looks like '{{cname}}_index' or 'log_{{cname}}', and not in array yet,
            but cname in array, array.pc.fill_coords() to infer the t coord to use.
        if any other value, use array.coords[t].values.
        if array.coords[t].dtype==object, convert to strs when plotting.
            e.g. [Fluid('e'), Fluid('H+')] --> ticks with 'e', 'H+'.
    dims: None or list-like of str/None objects.
        the dimensions; plot one line for each combination of dimensions.
        None --> infer, based on array and t.
        list-like --> if any element is None, infer it based on the other dims.
    werr: bool, 'bar', or 'fill'
        if `array` is a Dataset with info about mean and std, use this to make plot with error bars.
            (else, werr=False is the only valid option.)
        True --> equivalent to 'bar'
        'bar' --> plt.errorbar. Expect `array` to have 'mean' and 'std' data_vars.
        'fill' --> plt.fill_between. Expect `array` to have one of the following pairs of data vars:
            ('mean' and 'std', 'mean+std' and 'mean-std', 'eval+std' and 'eval-std')
        Note: if using werr, can pass any kwargs here, (of plt.errorbar or plt.fill_between) for style.
        E.g. capsize=5, elinewidth=3, capthick=5
    fill_center: None, bool, or dict
        if True or provided, and werr='fill' and array has 'mean' (or 'eval') data_var, also make timeline at center,
        using kwargs from __init__ but overwriting some things for the internal call to timelines():
            anything provided in fill_center; werr=False, fill_center=False; alpha=1.
            (The alpha=1 prevents fill_center from appearing transparent if alpha<1 in __init__.)
    cycles: None or list-like of dict/Cycler/None objects.
        the styles to use for each dimension. Must have length >= len(dims).
        E.g. cycles=[dict(color=['r', 'b', 'g']), dict(linestyle=['-', '--'])]
            --> dims[0] will cycle through colors; dims[1] will cycle through linestyles.
        None --> use DEFAULTS.PLOT.TIMELINES_CYCLE0, and (if needed) DEFAULTS.PLOT.TIMELINES_CYCLE1.
                (default: {default_cycles})
                if len(dims) > 2, this will fail.
        list-like --> if any element is None, use plt.rcParams['axes.prop_cycle'] for that dimension;
                        and cannot have more than 1 None cycle.
    short_cycle_ok: bool
        whether it is okay for cycles to be shorter than the number of points in that dimension.
    dmax: UNSET, None, or int
        maximum length of a timelines dimension before crashing (with TooManyPlottablesError).
        This prevents accidentally asking to make plot with hundreds of lines or more,
            e.g. if array has maindims in it due to forgetting to use 'mean_'.
        Not applied to self.t dimension, which can be any length,
            since t goes along an axis instead of having 1 line for each.
        UNSET --> self.dmax = DEFAULTS.PLOT.TIMELINES_DMAX (default: {default_dmax})
        None --> no maximum. Use with caution.
        int --> maximum length.
    styles: None or list-like of dicts.
        the styles to use for each line. i'th line will use styles[i].
        if any value in styles dicts conflicts with cycles, use value from syles instead of cycle.
    plot: bool
        whether to call self.plot() immediately, during init.
    label: None, False, or str
        if provided, prepend this value to all lines' labels generated by this XarrayTimelines.
        (If it doesn't end with whitespace, add a single space. E.g. "myinfo" --> "myinfo ".)
        Useful if plotting timelines on the same axes as other information.
        False --> use label='' for all lines.
    custom_labels: None or str
        if provided, use this label instead of `label` + dim info;
        will be passed dict of nondim coord values for each line.
        E.g. custom_labels='u_{{fluid}},{{component}}' --> 'u_H+,x' when fluid='H+' and component='x'.
    add_legend: bool
        whether to plot a legend, by default.
    legend_cols_align: bool
        whether to align legend cols such that one of the dims (the longest one), is the same in each row.
        E.g. if True, and self.dims = ['fluid', 'component'], with more fluids than components,
            then 'fluid' will be the same across each row.
        Only applied if len(self) > legend_max_rows > (number of rows when cols aligned)
    legend_max_rows: None or int
        maximum number of rows in the legend. Add legend columns if len(self) > legend_max_rows.
        (For more precise control, make your own legend after plotting...)
        None --> no maximum.
    skipna: bool
        whether to drop NaN values before plotting each line of values.
    robust: {robust}
        Will consider minimum vmin and maximum vmax across all lines, to avoid fully-hiding lines.
    ymargin: {ymargin}
    ybounds: {ybounds}
    xincrease: None or bool
        whether the x-axis should increase from left to right.
        None --> False if monotonically nonincreasing. I.e., False if all(t[i+1] <= t[i]), else True.
                ("if t values are obviously inverted, take it as a hint from user to do xincrease=False")
    cstyles: None or dict of {{coordname: dict or list of tuples of (val, dict of kwargs for a line)}}
        if provided, pass these dicts to individual lines with corresponding scalar val for coord.
        use tuples of values to test equality instead of indexing a dict.
        E.g., styles={{'fluid': [('e', dict(ls='--')), ('H_II', dict(color='blue'))]}}
            would ensure dashed line when arr['fluid']=='e', blue line when arr['fluid']=='H_II',
            and have no effect whenever arr['fluid'] is not scalar, doesn't exist, or isn't 'e' or 'H_II'.
    cstyles_default: bool
        tells how to handle conflict between kwargs from cstyles and other kwargs.
        True --> treat cstyles as 'defaults'; kwargs from other sources override kwargs from cstyles.
        False --> kwargs from cstyles take precedence.

    Additional kwargs go to super().__init__, and eventually to a plotting routine. Options include:
        - self.plot_settings.get_mpl_kwargs('plt.legend')
        - self.plot_settings.get_mpl_kwargs('plt.plot')
        - self.plot_settings.get_mpl_kwargs('plt.errorbar')   # if werr=True or 'bar'
        - self.plot_settings.get_mpl_kwargs('plt.fill_between')   # if werr='fill'
        
        (Note that any plot settings which also appear in cycles will use the cycles values,
            e.g. if 'linestyle' appears in cycle but also in kwargs, use the cycle value instead.)

    --- Examples ---
        import PlasmaCalcs as pc

        # basic usage:
        array.pc.timelines()   # make timelines plot with default settings.

        # alternative call signature:
        pc.XarrayTimelines(array)   # same result as above ^

        # specify cycle:
        #   for dims[0], use plt.rcParams['axes.prop_cycle'];
        #   for dims[1], use a gradient in alpha (instead of the default, which is different linestyles):
        array.pc.timelines(cycles=[None, dict(alpha=np.linspace(1, 0.3, 10)])

        # use linewidth and linestyle in cycle for dims[1], use colors for dims[0]:
        array.pc.timelines(cycles=[None, dict(linewidth=[5, 4, 3, 2], linestyle=['-', '--', ':', '-.'])])

        # specify handlelength (for legend, ensure lines are long enough to see):
        array.pc.timelines(handlelength=5)
    '''
    def __init__(self, array, t='t', dims=None, *,
                 werr=False, fill_center=None,
                 cycles=None, short_cycle_ok=False, dmax=UNSET,
                 styles=None,
                 plot=True,
                 label=None,
                 custom_labels=None,
                 add_legend=True, legend_cols_align=True, legend_max_rows=20,
                 skipna=False,
                 robust=PlotSettings.default('robust'),
                 ymargin=PlotSettings.default('ymargin'),
                 ybounds=PlotSettings.default('ybounds'),
                 xincrease=None,
                 cstyles=None, cstyles_default=False,
                 **kw_super):
        self._kw_init = dict(t=t, dims=dims, werr=werr, fill_center=fill_center,
                             cycles=cycles, short_cycle_ok=short_cycle_ok, dmax=dmax,
                             styles=styles, plot=plot, label=label,
                             add_legend=add_legend, legend_cols_align=legend_cols_align,
                             legend_max_rows=legend_max_rows, skipna=skipna,
                             robust=robust, ymargin=ymargin, ybounds=ybounds,
                             xincrease=xincrease, cstyles=cstyles, cstyles_default=cstyles_default,
                             **kw_super)
        self.werr = werr
        self.fill_center = None if fill_center is False else dict() if fill_center is True else fill_center
        array = xarray_fill_coords(array, need=[t])
        if werr:
            self.werrarr = array
            if not isinstance(array, xr.Dataset):
                raise InputConflictError('werr=True is only valid for Dataset inputs.')
            if werr == True or werr == 'bar':
                if 'mean' not in array or 'std' not in array:
                    raise InputConflictError('werr=True is only valid for Dataset with "mean" and "std" data_vars.')
                self.array = array['mean']
                self.werr_std = array['std']
            elif werr == 'fill':
                # fillarr = array but formatted to have 'mean+std' and 'mean-std' values.
                if 'mean' in array and 'std' in array:
                    werrarr = xarray_werr2pmstd(array, keep_mean=True)
                elif 'mean+std' in array and 'mean-std' in array:
                    werrarr = array
                elif 'eval+std' in array and 'eval-std' in array:
                    werrarr = array.rename({'eval+std': 'mean+std', 'eval-std': 'mean-std'})
                    if 'eval' in array:
                        werrarr = werrarr.rename({'eval': 'mean'})
                else:
                    errmsg = ('werr="fill" is only valid for Dataset with one of these pairs of data_vars: '
                                '("mean" and "std", "mean+std" and "mean-std", or "eval+std" and "eval-std"), '
                                f'but got Dataset with data_vars: {list(array.data_vars)}')
                    raise InputConflictError(errmsg)
                if not (xarray_is_sorted(werrarr[t]) or xarray_is_sorted(werrarr[t], increasing=False)):
                    #warnings.warn(f'werr="fill" but array[{t!r}] not sorted! plt.fill_between might not work nicely.')
                    werrarr = werrarr.sortby(t)
                self.werrarr = werrarr
                self.array = werrarr['mean+std']  # used internally for coord & dim info
        else:
            if isinstance(array, xr.Dataset):
                array = array.to_array(dim='variable')
            self.array = xarray_fill_coords(array, need=[t])
        self.t = t
        self.dims = self._infer_dims(dims)
        self.short_cycle_ok = short_cycle_ok
        self.cycles = cycles   # after short_cycle_ok in case super() defines cycles as a property.
        self.dmax = DEFAULTS.PLOT.TIMELINES_DMAX if dmax is UNSET else dmax
        self.styles = styles
        self.label = label
        self.custom_labels = custom_labels
        self.add_legend = add_legend
        self.legend_cols_align = legend_cols_align
        self.legend_max_rows = legend_max_rows
        self.skipna = skipna
        self.cstyles = cstyles
        self.cstyles_default = cstyles_default
        super().__init__(robust=robust, ymargin=ymargin, ybounds=ybounds,
                         xincrease=xincrease, **kw_super)
        if plot:
            self.plot()

    def _infer_dims(self, dims):
        '''infer dims from self.array, as needed. return result.'''
        coords = self.array.coords
        if self.t == 'snap_str':
            raise NotImplementedError('[TODO] implement t == "snap_str" case.')
        tdim = coords[self.t].dims[0]
        rdims = [d for d in coords.dims if d != tdim]  # remaining dims (here, without tdim)
        if dims is None:
            return rdims
        else:
            dims = list(dims)  # editable copy of input dims.
            # first, ensure any non-None dims are in rdims, then remove them from rdims.
            for d in dims:
                if d is not None:
                    if d not in rdims:
                        raise DimensionKeyError(f'provided dim {d!r} not in remaining dims {rdims!r}')
                    else:
                        rdims.remove(d)
            # next, replace any None dims with values from rdims;
            #   and assert len(rdims) == number of None dims remaining.
            num_None = dims.count(None)
            if num_None != len(rdims):
                raise PlottingAmbiguityError(f'cannot infer dims {dims!r} from array with dims {coords.dims!r}')
            for i, d in enumerate(dims):
                if d is None:
                    dims[i] = rdims.pop(0)  # pop the 0th element from rdims.
            return dims

    def _get_cyclers(self, called=False, *, indexable=True):
        '''return list of Cycler objects. Get from self.cycles, or defaults if self.cycles is None.

        result must have length >= len(self.dims).

        Each cycle must have length >= number of points in the corresponding dimension,
            unless self.short_cycle_ok is True.

        called: bool
            if True, call each cycle before returning it. (Turning it into an itertools.cycle() result)
            Equivalent to [cycle() for cycle in self._get_cyclers(called=False)].
        indexable: bool
            if True, convert each result to IndexableCycler. Ignored if called=True.
        '''
        if self.cycles is None:
            cycles = [DEFAULTS.PLOT.TIMELINES_CYCLE0, DEFAULTS.PLOT.TIMELINES_CYCLE1]
        else:
            cycles = self.cycles
        cycles = list(cycles)   # make an editable copy
        if len(cycles) < len(self.dims):
            errmsg = f'len(cycles) < len(dims). ({len(cycles)} < {len(self.dims)})'
            raise PlottingAmbiguityError(errmsg)
        used_rcParams_cycle = False
        result = []
        for i, (cycle, dim) in enumerate(zip(cycles, self.dims)):
            if isinstance(cycle, cycler.Cycler):
                c_use = cycle
            else:
                if cycle is None:
                    if used_rcParams_cycle:
                        errmsg = 'cannot have more than 1 None cycle, otherwise plot will be ambiguous.'
                        raise PlottingAmbiguityError(errmsg)
                    c_use = plt.rcParams['axes.prop_cycle']
                else:
                    c_use = cycler.cycler(**cycle)
            assert isinstance(c_use, cycler.Cycler), "if False, probably made a coding error..."
            result.append(c_use)
            if (not self.short_cycle_ok) and (len(c_use) < len(self.array.coords[dim])):
                errmsg = (f'len(cycles[{i}]) < len(array.coords[{dim!r}]). ({len(result[i])} < {len(self.array.coords[dim])})'
                          f'\nUse short_cycle_ok=True to allow this, causing repeated line formats, instead of crashing.')
                raise PlottingAmbiguityError(errmsg)
        if called:
            result = [cycle() for cycle in result]
        elif indexable:
            result = [IndexableCycler(cycle) for cycle in result]
        return result

    def _get_t_values(self):
        '''return values for the time axis.'''
        if self.t == 'snap':
            return [int(snap) for snap in self.array.coords['snap']]
        elif self.t == 'snap_str':
            return [int(str(snap)) for snap in self.array.coords['snap']]
        else:
            cc = self.array.coords[self.t]
            if cc.dtype == object:
                result = [str(val) for val in cc.values]
                MAXLEN = DEFAULTS.PLOT.XTICKLABEL_MAXLEN
                result = [s if len(s)<MAXLEN else s[:MAXLEN-3]+'...' for s in result]
                return result
            else:
                return cc.values

    def _check_size(self):
        '''crash (with TooManyPlottablesError), if the number of lines to plot is too large.
        I.e., if any of the dims have length > self.dmax.
        '''
        for dim in self.dims:
            if len(self.array.coords[dim]) > self.dmax:
                errmsg = (f'len(array.coords[{dim!r}]) > self.dmax. '
                          f'(Got {len(self.array.coords[dim])} > {self.dmax})')
                raise TooManyPlottablesError(errmsg)

    def _get_label(self, dimsel, *, fmtn='{:.3g}', fmts='{!s:s}'):
        '''return labels given this dict of {dim: (i for this dim)} for dims in self.dims.
        This corresponds to 1 timeline in the plot.

        if custom_labels provided instead format it, by providing the dict of
            self.array.sel(dimsel).pc.nondims_coords(scalars_only=True, item=True).

        fmtn: str
            attempt to format values using this format string.
            if fails (with ValueError or TypeError), use fmts instead.
        fmts: str
            format string to use if fmtn fails.
            (default '{!s:s}'... '!s' converts to str; ':s' is the format specifier)
        '''
        if self.custom_labels is None:
            # prepend
            prepend0 = '' if self.label is None else self.label  # prepend without whitespace appended.
            if prepend0 is False:
                return ''  # don't provide any label at all.
            prepend = prepend0  # prepend, possibly with whitespace appended.
            if len(prepend) > 0:
                if prepend.rstrip() == prepend:   # i.e., doesn't end with any whitespace
                    prepend += ' '  # add a single space.
            # loop through dims
            coords = self.array.coords
            coords_dict = {}
            for dim, i in dimsel.items():
                coords_dict[dim] = coords[dim][i].item()  # item --> get single value
            dimlabels = []
            for dim, val in coords_dict.items():
                try:
                    valstr = fmtn.format(val)
                except (ValueError, TypeError):
                    valstr = fmts.format(val)
                dimlabels.append(f'{dim}={valstr}')
            if len(dimlabels) == 0:
                return prepend0
            else:
                return prepend + ', '.join(dimlabels)
        else:  # provided custom labels
            arr_here = self.array.isel(dimsel)
            nondim_coords = xarray_nondim_coords(arr_here, scalars_only=True, item=True)
            return self.custom_labels.format(**nondim_coords)

    def __len__(self):
        '''returns number lines which self would plot if plotted.'''
        dimlens = [len(self.array.coords[dim]) for dim in self.dims]
        return product(dimlens)

    def legend(self, ncols=None):
        '''plot the legend for the current plot, via plt.legend().
        legend anchored to upper right corner of plot, outside the axes.
            if self.legend_max_rows is not None:
                put a limit on nrows.
            if self.legend_cols_align is True:
                align the columns such that (the longest) one of the dims is the same in each row.
                Only applied if len(self) > legend_max_rows > (number of rows when cols aligned)
        ncols: None or int
            number of columns to use in the legend.
            None --> picks a decent-looking value, based on self.legend_max_rows.

        For more precise legend control, use plt.legend() instead.
        '''
        handles, labels = plt.gca().get_legend_handles_labels()
        if ncols is None:
            if self.legend_max_rows is None:
                ncols = 1
            else:
                L = len(self)
                nrow = self.legend_max_rows
                # align cols if necessary & possible
                if self.legend_cols_align and (L > nrow):
                    L_coords = [len(self.array.coords[dim]) for dim in self.dims]
                    i_longest = rargmax(L_coords)
                    L_longest = L_coords[i_longest]
                    if L_longest <= self.legend_max_rows:
                        nrow = L_longest
                        # also, re-sort handles and labels if needed:
                        if i_longest != len(self.dims) - 1:
                            labarr = np.array([handles, labels], dtype=object)
                            labarr = labarr.reshape(2, *L_coords)
                            transp = list(range(1, len(self.dims)+1))  # shape[0] will always be 2 for [handles,labels]
                            transp.remove(i_longest+1)
                            labarr = labarr.transpose(0, *transp, i_longest+1)  # put longest last.
                            labarr = labarr.reshape(2, -1)
                            handles, labels = labarr
                # 1 + ((x-1) // y) is equivalent to ceil(x/y), for positive x,y.
                ncols = 1 + ((len(self)-1) // nrow)
        # if ncols > 1, don't use any vertical padding from top right corner.
        bbox_to_anchor = (1.02, 0.95) if ncols == 1 else (1.02, 1)
        kw_legend_here = dict(loc='upper left', bbox_to_anchor=bbox_to_anchor, ncols=ncols)
        kw_legend = self.plot_settings.get_mpl_kwargs('plt.legend', **kw_legend_here)
        plt.legend(handles, labels, **kw_legend)

    def add_labels(self):
        '''add labels to plot, based on self.array.'''
        array = self.array
        units = array.attrs.get('units', None)
        units = '' if units is None else f' [{units}]'
        xunits = units if units and (self.t not in ('snap', 'snap_str')) else ''
        plt.xlabel(f'{self.t}{xunits}')
        name = getattr(self.array, 'name', None)
        if name is not None:
            plt.ylabel(f'{name}{units}')

    def _get_ith_style(self, i):
        '''returns style for ith line on the plot, inferred from self.styles.'''
        if self.styles is None:
            return dict()
        elif i < len(self.styles):
            return self.styles[i]
        else:
            return dict()

    def _get_idx_cstyle(self, idx):
        '''returns the cstyle for plot line at this dimpoint index (a dict).'''
        if self.cstyles is None:
            return dict()
        arr = self.array.isel(idx)
        result = {}
        for cname, csty in self.cstyles.items():
            if cname in arr.coords and arr[cname].size==1:
                if isinstance(csty, dict):
                    result.update(csty.get(arr[cname].item(), {}))
                else:  # csty must be an iterable of 2-tuples
                    for cval, cvalstyle in csty:
                        if arr[cname].item() == cval:
                            result.update(cvalstyle)
        return result

    def iter_dimpoints(self):
        '''iterates through points across all dimensions.
        Yields (dimsel, style) pairs, where:
            dimsel = dict of {dim: (i of dim at this point)} for dim in self.dims
            style = dict of {matplotlib kwarg: value} which are relevant at this point.
                    only includes relevant cstyles if not self.cstyles_default.
        '''
        dimranges = [range(len(self.array.coords[dim])) for dim in self.dims]
        cycles = self._get_cyclers(indexable=True)
        for ii, dimidx in enumerate(itertools.product(*dimranges)):
            # dimidx is a tuple of (i of dim here) for dim in self.dims.
            dimpoint = {dim: i for dim, i in zip(self.dims, dimidx)}
            # styles to use here
            styles = [cycle[j] for cycle, j in zip(cycles, dimidx)]
            style = {k: v for d in styles for k, v in d.items()}
            style.update(self._get_ith_style(ii))
            if not self.cstyles_default:
                cstyle_here = self._get_idx_cstyle(dimpoint)
                style = {**style, **cstyle_here}
            yield (dimpoint, style)

    @PlotSettings.format_docstring(ntab=2)
    def get_effective_data_interval(self, *, robust=UNSET):
        '''returns (vmin, vmax) taken across all lines in self.
        If robust, take min vmin(line) and max vmax(line) across all lines.

        robust: {robust}
            If UNSET, use self.plot_settings.get('robust'). (if still UNSET, use behavior described above.)
        '''
        self._check_size()
        array = self.werrarr if self.werr else self.array
        robust = self.plot_settings.get('robust', robust)
        yminmin, ymaxmax = None, None
        for dimsel, _style in self.iter_dimpoints():
            consider = array.isel(dimsel)
            ndim = consider.ndim if isinstance(consider, xr.DataArray) else len(consider.dims)
            if ndim != 1:
                raise DimensionError(f'expected 1D after indexing; got {consider.ndim}D')
            if self.werr:
                if self.werr == 'fill':
                    consider = xr.Dataset({'mean+std': consider['mean+std'], 'mean-std': consider['mean-std']})
                else:
                    consider = xarray_werr2pmstd(consider)
                consider = consider.to_array('__internal_dim_for_computing_data_interval__')
            vmin, vmax = calculate_vlims(consider, robust=robust)
            if yminmin is None:  # first time in loop.
                yminmin, ymaxmax = vmin, vmax
            else:
                yminmin = min(yminmin, vmin)
                ymaxmax = max(ymaxmax, vmax)
        return yminmin, ymaxmax

    @PlotSettings.format_docstring(ntab=2)
    def set_ylim(self, *, robust=UNSET, ymargin=None, ybounds=UNSET):
        '''sets plt.ylim() to a nice range for viewing all lines from self.
        robust: {robust}
            If robust, take min vmin(line) and max vmax(line) across all lines.
            If UNSET, use self.plot_settings.get('robust'). (if still UNSET, use behavior described above.)
        ymargin: {ymargin}
            If None, use self.plot_settings.get('ymargin') instead.
        ybounds: {ybounds}
            if UNSET, use self.plot_settings.get('ybounds') instead.
        '''
        data_interval = self.get_effective_data_interval(robust=robust)
        ymin, ymax = plt_zoomy(margin=ymargin, data_interval=data_interval, plot_settings=self.plot_settings)
        ybounds = self._get_ybounds(ybounds=ybounds)
        if ybounds is not False:
            ybmin, ybmax = ybounds
            if ybmin is not None: ymin = min(ymin, ybmin)
            if ybmax is not None: ymax = max(ymax, ybmax)
        plt.ylim(ymin, ymax)

    @PlotSettings.format_docstring(ntab=2)
    def _get_ybounds(self, *, ybounds=UNSET):
        '''get ybounds to use later; call before plotting, then pass to self.set_ylim after plotting
        to ensure any previous plots on this axes don't get cut off.
        robust: {robust}
            If robust, take min vmin(line) and max vmax(line) across all lines.
            If UNSET, use self.plot_settings.get('robust'). (if still UNSET, use behavior described above.)
        ymargin: {ymargin}
            If None, use self.plot_settings.get('ymargin') instead.
        ybounds: {ybounds}
            if UNSET, use self.plot_settings.get('ybounds') instead.
        '''
        if ybounds is UNSET:
            ybounds = self.plot_settings.get('ybounds')
        if ybounds is None:
            ybounds = plt.ylim() if current_axes_has_data() else False
        return ybounds

    def _plot_lines(self, **kw_plot):
        '''plot the lines vs time. Probably via plt.plot.
        (if self.werr, might instead use plt.errorbar or plt.fill_between.)

        Does not do any of the nice preprocessing or postprocessing to help with formatting.
        User should use self.plot() instead.

        returns dict of info, including 'any_legend_labels' telling whether any labels were added
            (if no labels were added, later functions should not add legend.)
        '''
        t_values_base = self._get_t_values()
        array = self.array
        any_legend_labels = False

        if self.werr == False:
            plotter_name = 'plt.plot'
        elif self.werr == True or self.werr == 'bar':
            plotter_name = 'plt.errorbar'
        elif self.werr == 'fill':
            plotter_name = 'plt.fill_between'
        else:
            raise InputError('invalid value for self.werr, expected bool, "bar" or "fill".')
        # plot lines
        for dimsel, style in self.iter_dimpoints():
            # get plottable values
            to_plot = array.isel(dimsel)
            if to_plot.ndim != 1:
                raise DimensionError(f'expected 1D array after indexing; got {to_plot.ndim}D array')
            if self.werr == True or self.werr == 'bar':
                yerr = self.werr_std.isel(dimsel)
            elif self.werr == 'fill':
                werrarr = self.werrarr.isel(dimsel)
            # account for nans
            t_values = t_values_base  # might be changed below
            if self.skipna:
                nans = np.isnan(to_plot)
                if np.any(nans):
                    to_plot = to_plot[~nans]
                    t_values = t_values_base[~nans]
                    if self.werr == True or self.werr == 'bar':
                        yerr = yerr[~nans]
                    elif self.werr == 'fill':
                        werrarr = werrarr.where(~nans, drop=True)
            # get label
            label = self._get_label(dimsel)
            if label != '':
                any_legend_labels = True
            # get kwargs to use for this line
            kw_plot_here = self.plot_settings.get_mpl_kwargs(plotter_name, **style, **kw_plot)
            if self.cstyles_default:  # put cstyle as defaults but allow plot_settings to override them
                cstyle_here = self._get_idx_cstyle(dimsel)
                kw_plot_here = {**cstyle_here, **kw_plot_here}
            # >> actually plot this line <<
            if self.werr == False:
                plt.plot(t_values, to_plot.values, label=label, **kw_plot_here)
            elif self.werr == True or self.werr == 'bar':
                plt.errorbar(t_values, to_plot.values, yerr=yerr.values, label=label, **kw_plot_here)
            else:
                lower, upper = werrarr['mean-std'].values, werrarr['mean+std'].values
                plt.fill_between(t_values, lower, upper, label=label, **kw_plot_here)
        return {'any_legend_labels': any_legend_labels}


    PlotSettings.format_docstring(ntab=2)
    def plot(self, *, legend=UNSET, add_labels=True, robust=UNSET, ymargin=None, ybounds=UNSET, **kw_plot):
        '''plot the lines vs time. Probably via plt.plot.
        (if self.werr, might instead use plt.errorbar or plt.fill_between.)

        legend: UNSET or bool
            whether to plt.legend().
            UNSET --> use legend = self.add_legend (default: True)
            note: if all labels are None or empty string, will never attempt to add legend.
        add_labels: bool
            whether to self.add_labels() to plot, based on self.array:
                xlabel (self.t), and ylabel if known (self.array.name).
                Also put units on those labels if self.array.attrs['units'] is provided.
        robust: {robust}
            If robust, take min vmin(line) and max vmax(line) across all lines.
            If UNSET, use self.plot_settings.get('robust'). (if still UNSET, use behavior described above.)
        ymargin: {ymargin}
            If None, use self.plot_settings.get('ymargin') instead.
        ybounds: {ybounds}
            if UNSET, use self.plot_settings.get('ybounds') instead.
        '''
        self._check_size()
        t_values_base = self._get_t_values()
        pre_ybounds = self._get_ybounds(ybounds=ybounds)
        # >> plot lines <<
        plotinfo = self._plot_lines()
        any_legend_labels = plotinfo.get('any_legend_labels', False)
        # formatting
        self.set_ylim(robust=robust, ymargin=ymargin, ybounds=pre_ybounds)
        xincrease = self.plot_settings.get('xincrease')
        if xincrease is None:
            if t_values_base[0] < t_values_base[-1]:  # [EFF] quick check with only 2 values
                xincrease = True
            else:  # False if all(t[i+1] <= t[i]), else True
                xincrease = not np.all(t_values_base[1:] <= t_values_base[:-1])
        xmin, xmax = plt.xlim()
        if (xincrease and (xmin > xmax)) or ((not xincrease) and (xmin < xmax)):
            plt.gca().invert_xaxis()
        if legend is UNSET: legend = self.add_legend
        if legend and any_legend_labels:
            self.legend()
        if add_labels:
            self.add_labels()
        # 'center' if fill_center
        if self.fill_center is not None:
            if self.werr != 'fill':
                raise InputConflictError(f'non-None fill_center when "fill"!=werr(=={self.werr}).')
            if 'mean' not in self.werrarr:
                raise InputConflictError('werrarr does not have "mean" data_var; cannot fill_center')
            timelines_cls = type(self)
            _default_center_kw = {'werr': False, 'fill_center': False, 'alpha': 1}
            center_kw = {**self._kw_init, **_default_center_kw, **self.fill_center}
            self.filled_center = timelines_cls(self.werrarr['mean'], **center_kw)
