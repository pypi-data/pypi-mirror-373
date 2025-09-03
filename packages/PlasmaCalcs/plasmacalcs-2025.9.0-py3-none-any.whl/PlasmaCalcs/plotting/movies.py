"""
File Purpose: working on movies
"""

import os
import matplotlib as mpl
import matplotlib.animation as mpl_animation
import matplotlib.pyplot as plt

from .plot_settings import PlotSettings, PlotSettingsMixin
from ..tools import (
    alias, alias_child, simple_property,
    using_attrs,
    format_docstring,
    UNSET, NO_VALUE,
    repr_simple,
    ProgressUpdater,
    Tree,
)
from ..errors import (
    PlottingNotImplementedError, PlottingAmbiguityError, PlottingNframesUnknownError,
    InputError, InputConflictError,
)

from ..defaults import DEFAULTS


### --------------------- FuncAnimation --------------------- ###

@PlotSettings.format_docstring(doc_super=mpl_animation.FuncAnimation.__doc__)
class FuncAnimation(PlotSettingsMixin, mpl_animation.FuncAnimation):
    '''matplotlib.animation.FuncAnimation class with more methods / convenience.

    verbose: bool
        verbosity, e.g. during self.save.
    progress_callback: {progress_callback}
    fps: {fps}

    All other args and kwargs go to super(), probably mpl.animation.FuncAnimation.
    For reference, docs for mpl.animation.FuncAnimation:
    ----------------------------------------------------
    {doc_super}
    '''
    def __init__(self, fig, func, *args_super, fps=UNSET, verbose=True, **kw_super):
        if fig is None:
            raise InputError('cannot make animation when fig=None! Maybe you forgot to init_plot()?')
        super().__init__(fig, func, *args_super, fps=fps, mpl_super=['mpl.animation.FuncAnimation'], **kw_super)
        self.verbose = verbose
        # fps
        _nframes = self.plot_settings.get('frames')
        _is_small = _nframes is not UNSET and _nframes <= DEFAULTS.PLOT.NFRAMES_SMALL
        _default_fps = DEFAULTS.PLOT.FPS_SMALL if _is_small else NO_VALUE  # NO_VALUE --> use plot_settings default.
        fps = self.plot_settings.get('fps', default=_default_fps)
        if fps is not None:
            self._interval = 1000/fps   # _interval is used by some matplotlib methods.

    # # # SAVING # # #
    def get_savefile(self, filename, ext=UNSET):
        '''return abspath of filename, with ext appended if not already there.
        if ext not provided, use DEFAULTS.PLOT.MOVIE_EXT.
        '''
        if ext is UNSET: ext = DEFAULTS.PLOT.MOVIE_EXT
        if ext is not None:
            filename_has_no_ext = (os.path.splitext(filename)[1] == '')
            if filename_has_no_ext:
                if not ext.startswith('.'): ext = '.' + ext
                filename = filename + ext
        return os.path.abspath(filename)

    @PlotSettings.format_docstring(ntab=2, doc_super=mpl_animation.FuncAnimation.save.__doc__)
    def save(self, filename, writer=None, *args_super, fps=UNSET, progress_callback=UNSET, **kw_super):
        '''Save the animation as a movie file by drawing every frame.

        filename: str
            output filename, e.g. 'example_movie.mp4'.
            if no extension provided, append DEFAULTS.PLOT.MOVIE_EXT.
        writer: None, str, or MovieWriter
            writer to use. passed directly to super().save.
            if MovieWriter (i.e., not None or str), ignore any provided value for fps.
        fps: {fps}
        progress_callback: {progress_callback}

        returns abspath of the saved file.

        All other args and kwargs go to super().save, probably mpl.animation.FuncAnimation.save.
        For reference, docs for mpl.animation.FuncAnimation.save:
        ---------------------------------------------------------
        {doc_super}
        '''
        progress_callback = self.get_progress_callback(progress_callback)
        fps = self.plot_settings.get('fps', fps, default=None)
        filename_as_abspath = self.get_savefile(filename)
        if not (writer is None or isinstance(writer, str)):
            # set fps=None, to avoid RuntimeError crash (unless in DEBUG mode)
            if DEFAULTS.DEBUG >= 3:   # in debugging mode...
                pass
            else:
                fps = None
        super().save(filename_as_abspath, writer=writer, *args_super, fps=fps,
                     progress_callback=progress_callback, **kw_super)
        self._progress_updater_finalize(f'movie at {filename_as_abspath!r}')
        return filename_as_abspath

    # # # PROGRESS UPDATE / HOOK # # #
    def get_progress_callback(self, progress_callback=UNSET):
        '''return the progress_callback to use for self.save, based on input & self.verbose.
        also, first deletes self._progress_updater if it exists.
        '''
        if hasattr(self, '_progress_updater'):
            del self._progress_updater
        progress_callback = self.plot_settings.get('progress_callback', progress_callback)
        if progress_callback is UNSET:
            progress_callback = self._progress_callback_default() if self.verbose else None
        return progress_callback

    def _progress_callback_default(self):
        '''return the default progress_callback for self.save.
        also sets self._progress_updater to the new ProgressUpdater object.
        '''
        updater = ProgressUpdater(DEFAULTS.PLOT.MOVIE_PROGRESS_UPDATE_FREQ)
        self._progress_updater = updater
        return lambda i, n: updater.print(f'rendering frame {i+1} of {n}')

    def _progress_updater_finalize(self, message):
        '''finalize self._progress_updater, if it exists, with the given message.'''
        if hasattr(self, '_progress_updater'):
            self._progress_updater.finalize(message, always=self.verbose)

    # # # DISPLAY-RELATED # # #
    @format_docstring(doc_super=mpl_animation.FuncAnimation.to_jshtml.__doc__)
    def to_jshtml(self, fps=UNSET, *args_super, **kw_super):
        '''Generate HTML representation of the animation.
        fps: UNSET, None, or number
            frames per second. 
            UNSET --> default to DEFAULTS.PLOT.FPS.
                        (Or use value from self, if provided)
            None --> use matplotlib defaults.

        All other args and kwargs go to super().to_jshtml, probably mpl.animation.FuncAnimation.to_jshtml.
        For reference, docs for mpl.animation.FuncAnimation.to_jshtml:
        --------------------------------------------------------------
        {doc_super}
        '''
        fps = self.plot_settings.get('fps', fps, default=None)
        if hasattr(self, '_html_representation'):  # caching
            # delete cached representation if fps is different now.
            if (fps is not None) and (fps != getattr(self, '_fps_for_html', None)):
                del self._html_representation
        with using_attrs(self, fps=None): # temporarily set fps=None (super().save doesn't like fps when using to_jshtml)
            result = super().to_jshtml(fps=fps, *args_super, **kw_super)
        # # caching, then return result # #
        # self._html_representation = ...  # unnecessary; super().to_jshtml already caches this attr.
        self._fps_for_html = fps
        return result

    def _repr_html_(self):
        '''IPython display hook for rendering.'''
        displaying = plt.rcParams["animation.html"]
        if (displaying == 'none') and DEFAULTS.PLOT.MOVIE_REPR_INLINE_HELP:
            helpmsg = (f'Getting static _repr_html_ for {type(self)};'
                       '\nnote that you can instead view animations in-line,'
                       "\nby setting plt.rcParams['animation.html']='jshtml' (or 'html5')"
                       '\n(To disable this print statement, set DEFAULTS.PLOT.MOVIE_REPR_INLINE_HELP = False)')
            print(helpmsg)
        return super()._repr_html_()


### --------------------- MoviePlotElement & MoviePlotNode --------------------- ###

@PlotSettings.format_docstring(ntab=1)
class MoviePlotElement(PlotSettingsMixin):
    '''updatable element in a plot. Put into an MoviePlotNode to connect update routines.

    Pneumonic:
        Element connects directly to matplotlib plotting routines;
        Node connects elements to matplotlib animation rountines.
    Element only needs to contain the minimal amount of info to plot the current data;
    Node may contain more info such as all data for the entire movie.

    Subclasses must define:
        update_data(dict) -> list of updated matplotlib Artist objects.

    INPUTS HERE:
        data: dict
            contains the data to be plotted.
            Subclasses might ask for data values as input instead of data dict,
                e.g. XarrayImagePlotElement.__init__ expects input array, not {{'array': array}}.
            But, all subclasses __init__ should define self.data = dict(...) appropriately.
            __init__ here makes a copy, to avoid unintentional changes.

        Additional kwargs can be any PlotSettings; see help(self.plot_settings) for details.
    '''
    def __init__(self, data=dict(), **kw_super):
        self.data = data.copy()
        super().__init__(**kw_super)

    # # # METHODS -- SUBCLASS SHOULD IMPLEMENT # # #
    def update_data(self, data):
        '''update the plot using relevant keys in data.
        return list of all updated matplotlib Artist objects.
        '''
        raise PlottingNotImplementedError(f'{type(self).__name__}.update_data()')


@PlotSettings.format_docstring(ntab=1)
class MoviePlotNode(PlotSettingsMixin, Tree):
    '''tree node storing a MoviePlotElement (in self.obj).

    To update repeatedly & save resulting animation, see self.save() or self.get_animator().

    To register updatable sub-elements use self.add_child;
        when updating self will also update all children.

    Subclasses must define:
        get_data_at_frame(int) -> dict

    INPUTS HERE:
        obj: UNSET, None, or MoviePlotElement
            the plot element stored in this node.
            UNSET --> didn't call init_plot.
            None --> intentionally not storing an element in this node.
        parent: None or MoviePlotNode
            if provided, the parent of this node. None -> this node has no parent.
        init_plot: {init_plot}
            ignored if obj is None; when obj is None, never call init_plot during __init__.

        Additional kwargs can be any PlotSettings; see help(self.plot_settings) for details.
    '''
    def __init__(self, obj=UNSET, *, parent=None,
                 init_plot=PlotSettings.get_default('init_plot'),
                 **kw_plot_settings):
        super().__init__(obj=obj, parent=parent, init_plot=init_plot, **kw_plot_settings)
        if self.plot_settings['init_plot'] and obj is not None:
            self.init_plot()

    # # # METHODS -- SUBCLASS SHOULD IMPLEMENT # # #
    def init_plot(self):
        '''plot for the first time; save self.obj = result, which should be a MoviePlotElement.
        Should also set self.frame = self.plot_settings['init_plot_frame']  (default 0).
        '''
        raise PlottingNotImplementedError(f'{type(self).__name__}.init_plot()')
        # example code for what should appear in the subclass:
        # self._init_plot_checks()
        # frame = self.plot_settings['init_plot_frame']
        # data = self.get_data_at_frame(frame)
        # kw_plot = ...  # probably some subset of plot_settings; depends on subclass.
        # self.obj = MoviePlotElement(data, **kw_plot)
        # self.frame = frame

    def get_data_at_frame(self, frame):
        '''return dict of data for the given frame, to be used by the MoviePlotElement at self.obj.'''
        raise PlottingNotImplementedError(f'{type(self).__name__}.get_data_at_frame()')

    def get_nframes_here(self):
        '''return the number of frames that could be in the movie, based on this node.'''
        errmsg = (f'{type(self).__name__}.get_nframes_here() not implemented, and frames not provided.\n'
                  'Provide frames=int (as kwarg or set self.frames). Or, implement get_nframes_here().')
        raise PlottingNframesUnknownError(errmsg)

    # # # PROPERTIES # # #
    fig = simple_property('_fig', setdefault=plt.gcf, doc='''the Figure on which self is / will be plotted.''')
    frame = simple_property('_frame', doc='''the currently-plotted frame''', default=None)
    plotted_data = alias_child('obj', 'data', doc='''the currently plotted data.''')

    @property
    def plotted(self):
        '''whether this node's element has actually been plotted yet.
        False before init_plot; True after. Always None if self.obj is None.
        '''
        return None if (self.obj is None) else (self.obj is not UNSET)

    # # # CHECKS # # #
    def _init_plot_checks(self):
        '''checks to run before init_plot().
        Here, checks:
            - if self.plotted, raise PlottingAmbiguityError.
            - if self.obj is None, raise PlottingAmbiguityError.
        '''
        if self.plotted:
            raise PlottingAmbiguityError('init_plot was already created! Did you mean to update instead?')
        if self.obj is None:
            raise PlottingAmbiguityError('init_plot not allowed when obj=None! (node intentionally empty)')

    # # # NUMBER OF FRAMES # # #
    def get_nframes(self):
        '''return max of get_nframes_here() for self & all descendants of self.
        If any node throws PlottingNframesUnknownError, pretend they said nframes=0.
        If all nodes throw PlottingNframesUnknownError, raise the one from self.
        '''
        nframes = 0
        try:
            nframes = self.get_nframes_here()
        except PlottingNframesUnknownError as err:
            for descendant in self.flat():
                try:
                    nframes = max(nframes, descendant.get_nframes())
                except PlottingNframesUnknownError as err_child:
                    pass
            if nframes == 0:
                raise err
        return nframes

    @property
    def frames(self):
        '''the frames that could be in the movie.
        if set to None, will use self.get_nframes() instead.
        if set to a slice, will use range(self.get_nframes())[frames] instead.
        '''
        return self._get_frames(self.plot_settings.get('frames', default=None))
    @frames.setter
    def frames(self, value):
        self.plot_settings['frames'] = value

    def _get_frames(self, value):
        '''gets frames based on value and possibly self.get_nframes() if necessary.
        if result would be None, crash instead.
        '''
        if value is None:
            value = self.get_nframes()
        if isinstance(value, slice):
            nframes = self.get_nframes()
            value = range(nframes)[value]
        return value

    # # # UPDATING # # #
    def init_plots(self, *, plotted_ok=True):
        '''init_plot for self & all descendants with non-None obj.
        plotted_ok: bool
            True --> skip node if node.plotted.
            False --> call init_plot on all nodes with non-None obj.
        '''
        if (self.obj is not None) and not (plotted_ok and self.plotted):
            self.init_plot()
        for descendant in self.flat():
            if (descendant.obj is not None) and not (plotted_ok and descendant.plotted):
                descendant.init_plot()

    def update_to_frame(self, frame):
        '''update the plot for the given frame. set self.frame=frame.
        also calls update_to_frame for all children.
        return iterable of all updated artists.
        '''
        if self.plotted == False:  # equivalent: if (not self.plotted) and (self.plotted is not None)
            raise PlottingAmbiguityError('node not yet plotted! Did you forget to call init_plot?')
        artists = []
        if (self.obj is not None) and (frame < self.get_nframes_here()):
            data = self.get_data_at_frame(frame)
            artists.extend(self.obj.update_data(data))
        for child in self.children:
            artists.extend(child.update_to_frame(frame))
        self.frame = frame
        return artists

    def __call__(self, frame):
        '''update the plot for the given frame. return iterable of all updated artists.
        Defining __call__ in this way means self is compatible for direct use by FuncAnimation.
        '''
        return self.update_to_frame(frame)

    # # # SAVING / RENDERING # # #
    @PlotSettings.format_docstring(ntab=2)
    def save(self, filename, frames=UNSET, *, fps=UNSET, blit=UNSET, **kw):
        '''save the movie to filename.
        RECOMMENDED:
            first, self.save(..., frames=N), with small N (e.g. N=5), to test movie formatting.
            Troubleshooting: if movie getting cut off,
                try plt.subplots_adjust(bottom=0.2, left=0.2, right=0.8, top=0.8),
                or even more extreme values if necessary. (0 is bottom/left edge; 1 is top/right edge.)

        frames: {frames}
        fps: {fps}
        blit: {blit}

        additional kwargs passed to FuncAnimation() or FuncAnimation.save().
        returns abspath of the saved movie.
        '''
        kw_animator = self.plot_settings.pop_mpl_kwargs('mpl.animation.FuncAnimation', kw, blit=blit, frames=frames)
        kw_animator.update(fps=self.plot_settings.get('fps', fps))  # fps goes to FuncAnimation defined here
        animator = self.get_animator(**kw_animator)
        kw_save = self.plot_settings.pop_mpl_kwargs('mpl.animation.FuncAnimation.save', kw)
        return animator.save(filename, **kw_save)

    @PlotSettings.format_docstring(ntab=2)
    def get_animator(self, *, fps=UNSET, blit=UNSET, frames=UNSET, plt_close=True, **kw_func_animation):
        '''returns FuncAnimation instance using self as func.
        Use kwarg defaults from self.plot_settings, for any kwargs not provided here.

        fps: {fps}
        blit: {blit}
        frames: {frames}
        plt_close: bool
            whether to plt.close() before returning the result.
            This is useful in Jupyter, where commonly one cell might make a plot,
                then call get_animator() to display movie in-line, but not plt.close().
                In that case, plt_close=False would display animation & plot

        [TODO] use init_func kwarg to avoid calling self twice for frame 0?
        '''
        frames = self._get_frames(self.plot_settings.get('frames', frames, default=None))
        kw = self.plot_settings.get_mpl_kwargs('mpl.animation.FuncAnimation',
                                               blit=blit, frames=frames, **kw_func_animation)
        kw.update(fps=self.plot_settings.get('fps', fps))  # fps goes to FuncAnimation defined here
        result = FuncAnimation(self.fig, func=self, **kw)
        if plt_close:
            plt.close()
        return result

    ani = alias('get_animator')   # <-- ani is defined here. (str to help codebase searches: def ani(...))

    @classmethod
    def help(cls):
        '''prints a helpful message with examples for how to use this cls'''
        msg = f'''Help for {cls}:
        Typical example use-case of an object of this type:
            obj = {cls.__name__}(...)
            obj(0)   # plot frame 0
            obj(7)   # plot frame 7
            obj.save('example_movie', frames=5)   # make an example movie; only include first 5 frames.
            obj.save('example_with_all_frames')   # make a movie with all frames.

            # or, if you want to view the movie in-line:
            plt.rcParams['animation.html'] = 'jshtml'   # or 'html5'
            ani = obj.get_animator()
            ani   # if you put this at the end of a cell in Jupyter, it will display the movie.'''
        print(msg)


### --------------------- EmptyMovieNode & MovieOrganizerNode --------------------- ###

class EmptyMovieNode(MoviePlotNode):
    '''makes an empty MoviePlotNode; can be used to improve tree readability.
    E.g. if tree represents subplots but one has no animations on it,
        might store an EmptyMovieNode so that the indexing aligns with subplots.
    '''
    def __init__(self, **kw_super):
        super().__init__(obj=None, **kw_super)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'[depth={self.depth}, height={self.height}, size={self.size}]']
        return f'({self.__class__.__name__}({", ".join(contents)}))'

    def _shorthand_repr(self):
        '''returns shorthand repr for this node: "((depth, height, size)) ()".'''
        return f'(({self.depth}, {self.height}, {self.size})) ()'


class MovieOrganizerNode(EmptyMovieNode):
    '''makes an empty MoviePlotNode; can be used to improve tree readability.
    E.g. if there are 3 nodes for the same axis & of roughly equal importance,
        might want to have them all be children of a MovieOrganizerNode,
        instead of arbitrarily picking one of them to be the parent.

    name: str
        name for this node; to be displayed in __repr__.
    '''
    def __init__(self, name='', **kw_super):
        super().__init__(**kw_super)
        self.name = name

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'[depth={self.depth}, height={self.height}, size={self.size}]']
        if self.name: contents.append(f'{self.name!r}')
        return f'--- {self.__class__.__name__}({", ".join(contents)}) ---'

    def _shorthand_repr(self):
        '''returns shorthand repr for this node (without children).
        returns '--- name ---' if self.name provided, else "((depth, height, size))".
        '''
        if self.name:
            return f'--- {self.name} ---'
        else:
            return f'(({self.depth}, {self.height}, {self.size})) {repr_simple(self.obj)}'
