"""
File Purpose: labels, e.g. titles, suptitles
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from .movies import MoviePlotElement, MoviePlotNode
from .plot_settings import PlotSettings, PlotSettingsMixin
from .plot_tools import infer_movie_dim

from ..errors import PlottingNotImplementedError, DimensionKeyError
from ..tools import (
    UNSET,
    alias_child, alias_key_of, simple_property,
    join_strs_with_max_line_len,
    xarray_nondim_coords, xarray_fill_coords,
    pcAccessor, xarray_isel, xarray_dims_coords,
)


_paramdocs_labels = {
    'txt': '''Text object
        e.g., the result of plt.text(...) or plt.title(...)''',
    'frame_to_text': '''list, dict, or callable.
        map from frame number to title string. title for frame will be:
        callable --> frame_to_text(frame)
        list or dict --> frame_to_text[frame]''',
    'array': '''xarray.DataArray, probably ndim=3.
        the full DataArray which will be plotted throughout the movie.
        internally, store xarray_fill_coords(array), so that coordless dims' indices can be used.
            e.g. if "dim0" is a dimension with no coords, will use np.arange(dim0.size).''',
    'base_text': '''UNSET or str
        the base text string, to be formatted by array at each frame.
        UNSET --> will use array._title_for_slice() for array at each frame.
        str --> will be formatted by xarray_nondim_coords(array at frame).
                E.g., base_text='fluid={{fluid}}, time={{t:.2e}} seconds'.''',
    't': '''None or str
        the array dimension which frames will index. E.g. 'time'.
        None --> infer it via infer_movie_dim(array.dims, t)''',
}

### --------------------- TextPlotElement / MovieText / XarrayText --------------------- ###

@PlotSettings.format_docstring(**_paramdocs_labels)
class TextPlotElement(MoviePlotElement):
    '''MoviePlotElement for Text object. see MovieText for updating text over time.

    txt: {txt}
    '''
    def __init__(self, txt, **kw_super):
        super().__init__(**kw_super)
        if isinstance(txt, str):
            raise TypeError(f'Expected txt to be a matplotlib.text.Text object, not a string.')
        self.txt = txt
        self.text = txt.get_text()

    text = alias_key_of('data', 'text',
        doc='''current text string. Internally stored at self.data['text']''')
    txt = simple_property('_txt', default=None, doc='''matplotlib.text.Text object''')
    ax = alias_child('txt', 'axes', if_no_child=None, doc='''axes containing this Text.''')
    fig = alias_child('txt', 'figure', if_no_child=None, doc='''figure containing this Text.''')

    # # # UPDATING (REQUIRED BY PARENT) # # #
    def update_data(self, data):
        '''update the plot using data['text'].
        return list of all updated matplotlib Artist objects, for FuncAnimation(..., blit=True),
            i.e. [] if self.ax is None else [self.txt].
            (FuncAnimation fails to blit any artists not attached to axes,
            and self.txt is attached to axes if and only if self.ax is not None)
        '''
        self.text = data['text']
        self.txt.set_text(self.text)
        return [] if self.ax is None else [self.txt]

    # # # DISPLAY # # #
    REPR_TEXT_MAX_LEN = 30  # text longer than this will be abbreviated in repr.

    def __repr__(self):
        text = self.text
        if isinstance(text, str):
            if len(text) > self.REPR_TEXT_MAX_LEN:
                text = text[:self.REPR_TEXT_MAX_LEN] + '...'
        return f'{type(self).__name__}({text!r})'


@PlotSettings.format_docstring(**_paramdocs_labels)
class MovieText(MoviePlotNode):
    '''MoviePlotNode for a Text object.

    txt: {txt}
    frame_to_text: {frame_to_text}
    '''
    element_cls = TextPlotElement

    def __init__(self, txt, frame_to_text, **kw_super):
        self.txt = txt
        self.frame_to_text = frame_to_text
        super().__init__(**kw_super)

    # # # PROPERTIES # # #
    ax = alias_child('obj', 'ax', doc='''mpl.axes.Axes where this MovieText is plotted.''')
    @ax.getter
    def ax(self):  # ax=None if not self.plotted
        return self.obj.ax if self.plotted else None

    fig = alias_child('obj', 'fig', doc='''figure where this MovieText is plotted.''')
    @fig.getter
    def fig(self):  # fig=None if not self.plotted
        return self.obj.fig if self.plotted else None

    text = property(lambda self: self.obj.text if self.plotted else None,
        doc='''the text string stored in self.obj; use self.update_to_frame to update it.''')

    # # # PLOTTING METHODS (REQUIRED BY PARENT CLASS) # # #
    def init_plot(self):
        '''plot for the first time. Save the TitlePlotElement at self.obj.'''
        self._init_plot_checks()
        frame = self.plot_settings['init_plot_frame']
        data = self.get_data_at_frame(frame)
        # get settings for plot
        kw_plot = self.plot_settings.get_mpl_kwargs('pc.TextPlotElement')
        # >> actually plot the text <<
        self.obj = self.element_cls(self.txt, **kw_plot)
        self.obj.update_data(data)
        # bookkeeping
        self.frame = frame

    def get_data_at_frame(self, frame):
        '''returns {'text': text string for this frame}.'''
        if callable(self.frame_to_text):
            text = self.frame_to_text(frame)
        else:
            text = self.frame_to_text[frame]
        return {'text': text}

    def get_nframes_here(self):
        '''returns number of frames that could be in this movie, based on this node.'''
        if callable(self.frame_to_text):
            errmsg = (f'{type(self).__name__}.frame_to_text is callable, and frames not provided.\n'
                      'Debugging: provide self.frames=int, or, provide list or dict frame_to_text.')
            raise PlottingNotImplementedError(errmsg)
        return len(self.frame_to_text)


@pcAccessor.register('text', totype='array')
@PlotSettings.format_docstring(**_paramdocs_labels)
class XarrayText(MovieText):
    '''MoviePlotNode managing text associated with an xarray.DataArray.

    txt: {txt}
    array: {array}
    t: {t}
    base_text: None, {base_text}
        if None, infer from txt.

    --- Examples ---
        # simple example:
        import PlasmaCalcs as pc
        array = ...  # some array having fluid & t coords...
        txt = plt.text(0, 7, '{{fluid}}, t={{t:.2e}}')  # text at x=0, y=7 in data coords.
        xtext = pc.XarrayText(array, txt, t='t')
        xtext.save('text_movie.mp4')

        # slightly more complex: start like above, but attach to existing MoviePlotNode instead:
        xim = array.pc.image()
        xim.add_child(xtext, arr)
        xim.save('image_and_text_movie.mp4')  # movie of image & text, both updating in time!

        # one more notable option: instead of txt = plt.text(...),
        # could do txt = plt.title(...), plt.suptitle(...) or similar option.
        # also, if infer_movie_dim can figure out t, don't need to provide it explicitly:
        xtext = pc.XarrayText(array, plt.title('{{fluid}}, t={{t:.2e}}'))

        # finally, note that this can be accessed from array, e.g.:
        xtext = array.pc.text(plt.title('{{fluid}}, t={{t:.2e}}'))
    '''
    def __init__(self, array, txt, t=None, *, base_text=None, **kw_super):
        # text bookkeeping
        self.txt = txt
        if isinstance(txt, str):
            errmsg = (f'Expected txt = matplotlib.text.Text object, not a string (got txt={txt!r})\n'
                      'Maybe you forgot to use txt=plt.text(...), txt=plt.title(...), or similar.')
            raise TypeError(errmsg)
        if base_text is None:
            base_text = txt.get_text()
        self.base_text = base_text
        # array bookkeeping
        self.array = xarray_fill_coords(array)
        try:
            self.t = infer_movie_dim(array.dims, t)
        except DimensionKeyError:
            if t in array.coords:
                self.t = t  # movie will only have 1 frame, but it's fine...
            else:
                raise
        # plot stuff
        super(MovieText, self).__init__(**kw_super)

    def frame_to_text(self, frame):
        '''return the text string at this frame'''
        if self.t is None:
            arr_at_frame = self.array
        else:
            arr_at_frame = xarray_isel(self.array, {self.t: frame})
        if self.base_text is UNSET:
            result = arr_at_frame._title_for_slice()
        else:
            vals = xarray_nondim_coords(arr_at_frame, scalars_only=True)
            result = self.base_text.format(**vals)
        return result

    def get_nframes_here(self):
        '''returns number of frames that could be in this movie, based on this node.
        0 if self never updates (i.e., self.t is None).
        '''
        return 0 if self.t is None else self.array.coords[self.t].size


### --------------------- Titles & Suptitles --------------------- ###

@pcAccessor.register('title', totype='array')
@PlotSettings.format_docstring(**_paramdocs_labels)
def xarray_title_plot_node(array, base_text=UNSET, t=None, *, ax=None, parent=None, **kw):
    '''create a MoviePlotNode for a title associated with an xarray.DataArray.

    array: {array}
    base_text: {base_text}
    t: {t}

    parent: None or MoviePlotNode
        if provided, the parent of this node. None -> this node has no parent.

    title_font: {title_font}
    title_y: {title_y}
    title_kw: {title_kw}
    text_kw: {text_kw}

    Additional kwargs go directly to plt.title()
    '''
    # title settings
    ps = PlotSettings(**kw, pop=True)
    kw_text = ps.get('text_kw', default=dict()).copy()
    kw_title = {**kw_text, **ps.get('title_kw', default=dict())}
    kw_title.setdefault('y', ps.get('title_y', default=None))
    fontfamily = ps.get('title_font')
    if fontfamily is not None: kw_title.update(fontfamily=fontfamily)
    # ax
    if ax is None:
        ax = plt.gca()
    # make title Text object
    txt = ax.set_title(str(base_text), **kw_title)
    # make & return MoviePlotNode
    # (use array.pc.text, not XarrayText, in case other module attaches XarrayText subclass.)
    result = array.pc.text(txt, t=t, base_text=base_text, parent=parent, **ps.kw)
    return result


@pcAccessor.register('suptitle', totype='array')
@PlotSettings.format_docstring(**_paramdocs_labels)
def xarray_suptitle_plot_node(array, base_text=UNSET, t=None, *, fig=None, parent=None, **kw):
    '''create a MoviePlotNode for a suptitle associated with an xarray.DataArray.

    array: {array}
    base_text: {base_text}
    t: {t}

    parent: None or MoviePlotNode
        if provided, the parent of this node. None -> this node has no parent.

    suptitle_font: {suptitle_font}
    suptitle_y: {suptitle_y}
    suptitle_kw: {suptitle_kw}
    text_kw: {text_kw}

    Additional kwargs go directly to plt.suptitle()
    '''
    # suptitle settings
    ps = PlotSettings(pop_from=kw)  # pop setting from kwargs
    kw_text = ps.get('text_kw', default=dict()).copy()
    kw_suptitle = {**kw_text, **ps.get('suptitle_kw', default=dict())}
    kw_suptitle.setdefault('y', ps.get('suptitle_y', default=None))
    fontfamily = ps.get('suptitle_font')
    if fontfamily is not None: kw_suptitle.update(fontfamily=fontfamily)
    # fig
    if fig is None:
        fig = plt.gcf()
    # make suptitle Text object
    txt = fig.suptitle(str(base_text), **kw_suptitle)
    # make & return MoviePlotNode
    # (use array.pc.text, not XarrayText, in case other module attaches XarrayText subclass.)
    result = array.pc.text(txt, t=t, base_text=base_text, parent=parent, **ps.kw)
    return result


### --------------------- SUBPLOTS Titles & Suptitles --------------------- ###

def title_from_coords(array, cnames=None, *, width=None, formattable=False):
    '''return a decent title from scalar coords.
    cnames: None or list of str
        coords to include values of in the title.
        None --> include all scalar coords.
    width: None or int
        max number of characters per line, before putting a newline between coords.
    formattable: bool
        whether to return a formattable version of the title.
    '''
    if cnames is None:
        cnames = xarray_nondim_coords(array, scalars_only=True)
    # use pretty number formatting if possible, else just str().
    results = []  # strs for title, e.g. 'fluid={fluid:}' or 'z={z:.3g}'
    examples = dict()  # {result: str with example val plugged in}, e.g. 'fluid=e-' or 'z=3.14'
    for c in cnames:
        v_example = array.coords[c].values.flat[0]  # example value of this coord.
        if c.endswith('_index') and np.issubdtype(array.coords[c].dtype, np.integer):
            fstr = 'd'  # special rule for index: use full int
        else:
            fstr = '.3g'
        try:
            f'{v_example:{fstr}}'
        except Exception:  # pretty formatting failed (e.g. non-numeric data).
            fstr = ''
        # [TODO] use !r if str type
        tmp = f'{c}={{{c}:{fstr}}}'
        results.append(tmp)
        examples[tmp] = tmp.format(**{c: v_example})
    # join strs with commas and/or newlines while respecting max width.
    result = join_strs_with_max_line_len(results, sep=', ', max=width,
                                         key=lambda r: len(examples[r]))
    if formattable:
        return result
    else:
        return result.format(**{c: array.coords[c].item() for c in cnames})


@PlotSettings.format_docstring()
class XarraySubplotTitlesInferer(PlotSettingsMixin):
    '''infers base titles & suptitle to use for subplots.
    "Base" means before title.format(nondim coord values from the array)

    array: xarray.DataArray
        infer titles from this array, after filling any missing coords
            (e.g. if dim_1 has no coords, use np.range(dim_1.size))
    t: None or str
        dimension name for the time axis (for movies).
    row: None or str
        dimension to plot ACROSS rows.
        None --> not plotting anything across rows; ncols=1.
    col: None or str
        dimension to plot DOWN columns.
        None --> not plotting anything across columns; nrows=1.
    subplot_title_width: {subplot_title_width}
    suptitle_width: {suptitle_width}
    '''
    def __init__(self, array, t=None, *, row=None, col=None, **kw_super):
        self.array = xarray_fill_coords(array)
        self.t = t
        self.row = row
        self.col = col
        super().__init__(**kw_super)

    def title_from_coords(self, cnames=None, *, width=None, formattable=True):
        '''return a decent title from scalar coords.
        cnames: None or list of str
            coords to include values of in the title.
            None --> include all scalar coords.
        width: None or int
            max number of characters per line, before putting a newline between coords.
        formattable: bool
            whether to return a formattable version of the title.
        '''
        return title_from_coords(self.array, cnames=cnames, width=width, formattable=formattable)

    def infer_title(self):
        '''infers title to use for subplots.
        This will just include the row & col dims & any associated coords.
        (excluding coords which will still be multidimensional within each subplot.)
        (also excluding MultiIndex coords; they are ugly, and all their info
            is already in title, via the coords within the MultiIndex.)
        '''
        array = self.array
        dims_coords = xarray_dims_coords(array)
        cnames = set()  # names of coords to include in title
        if self.row is not None:
            cnames.update(dims_coords[self.row])
        if self.col is not None:
            cnames.update(dims_coords[self.col])
        # remove coords which will be multi-dimensional within each subplot,
        #  i.e. have at least 1 dim other than just row and/or col.
        multi_dim_coords = set()
        for c in cnames:
            if len(set(array[c].dims) - {self.row, self.col}) > 0:
                multi_dim_coords.add(c)
        cnames = cnames - multi_dim_coords
        # remove MultiIndex coords
        multi_index_coords = set()
        for (idx, _idict) in array.indexes.group_by_index():
            if isinstance(idx, pd.MultiIndex):
                multi_index_coords.add(idx.name)
        cnames = cnames - multi_index_coords
        # style formatting, then get result:
        cnames = [c for c in self.array.coords if c in cnames]  # style: same order as in array.
        result = self.title_from_coords(cnames,
                        width=self.plot_settings['subplot_title_width'])
        return result

    def infer_suptitle(self):
        r'''infers title to use for subplots.
        This may include the array name, units, t dim,
            and any scalar xarray_nondim_coords not associated with row or col.

        formatting will be nice depending on which pieces of info exist.
            name --> '{name} {units}\n{t}\n{nondim_coords}'
            no name --> '{t} {units}\n{nondim_coords}'
            no t --> '{nondim_coords} {units}'
            if no units info remove {units} part
            if no scalar nondim_coords_values remove \n{nondim_coords} part
        '''
        array = self.array
        name = array.name
        t = self.t
        infos = dict()
        # array.name info
        if name is not None:
            infos['name'] = name
        # t info
        if t is not None:
            t = str(t)
            if t in ('time', 't', 'x', 'y', 'z'):
                infos['t'] = 'dim = {dim:.2e}'.replace('dim', t)
            elif (t == 'snap') and ('t' in array.coords):
                infos['t'] = 'snap = {snap!s:6s}, t = {t:.2e}'
            else:
                infos['t'] = 'dim = {dim!s}'.replace('dim', t)
        # units info
        if 'units' in array.attrs:
            units = array.attrs['units']
            infos['u'] = f'[{units}]'
        # scalar nondim coords - use pretty number formatting if possible, else just str()
        ncoords = xarray_nondim_coords(array, scalars_only=True)
        if len(ncoords) > 0:
            infos['c'] = self.title_from_coords(ncoords,
                                width=self.plot_settings['suptitle_width'])
        # return result, formatted based on which pieces of info exist.
        if infos:
            if 'name' in infos:
                uinfo = f" {infos['u']}" if 'u' in infos else ''
                tinfo = f"\n{infos['t']}" if 't' in infos else ''
                cinfo = f"\n{infos['c']}" if 'c' in infos else ''
                return f"{infos['name']}{uinfo}{tinfo}{cinfo}"
            elif 't' in infos:
                uinfo = f" {infos['u']}" if 'u' in infos else ''
                cinfo = f"\n{infos['c']}" if 'c' in infos else ''
                return f"{infos['t']}{uinfo}{cinfo}"
            elif 'c' in infos:
                uinfo = f" {infos['u']}" if 'u' in infos else ''
                return f"{infos['c']}{uinfo}"
            elif 'u' in infos:
                return f"units={infos['u']}"
        return None  # no info to add.
