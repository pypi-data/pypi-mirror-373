"""
File Purpose: class to help with managing making plots.
[TODO] allow multiple people to have same-named plotting function.
[TODO] allow plotter patterns, e.g. 'subN' to do a movie but subsample to every Nth snapshot.
"""
import contextlib
import os

import matplotlib.pyplot as plt

from ..defaults import DEFAULTS
from ..errors import (
    InputError, InputConflictError, InputMissingError,
    PlottingNotImplementedError, PlottingAmbiguityError,
)
from ..quantities.quantity_loader import MetaQuantTracking
# ^ specified .quantity_loader to help avoid circular imports.
from ..tools import (
    format_docstring, UNSET,
    ProgressUpdater, code_snapshot_info,
)


### --------------------- Plotter --------------------- ###

_paramdocs = {
    'fname': '''str
        name of the callable used to make the plot,
        via getattr(obj,fname)(...), where obj is a PlotterManager.''',
    'who': '''str or list of str
        "person" or people associated with this plotter. Arbitrary strings.
        E.g. to only make plots for 'sam' person, use PlotterManager.standard_plots(..., who='sam').''',
    'kind': '''UNSET, str, or list of str
        "kind" or kinds associated with this plotter. Arbitrary strings.
        E.g. to only make plots for 'movie' kind, use PlotterManager.standard_plots(..., kind='movie').
        Internally, stored at Plotter.kinds (plural).''',
    'kinds': '''UNSET, str, or list of str
        alias for kwarg `kind`. Can provide `kinds` or `kind` but not both.''',
    'ani': '''UNSET or bool
        whether the plotter is for an animated plot.
        (commands to save/show an animated plot are different than those to save/show a static plot.)
        if UNSET, infer from kinds. True if kinds includes any of these (case insensitive):
            ['movie', 'gif', 'ani', 'animation', 'animated']''',
    'savename': '''None or str
        default filename when doing plotter.save() for this plot.
        None --> use plotter.name, which is fname after removing 'plot_' prefix.''',
    'cost': '''number
        some guess about the cost to make this plot. Default=20.
        when making multiple plots, go in cost order.
        Can also set cost thresholds and skip ones that are too expensive.''',
    'aliases': '''list of str
        self.known[(person, alias)] = self.known[(person, name)] for each alias provided.''',
}

_paramdocs_plot = {
    'save': '''bool, str, or dict.
        whether to save figure after calling plotter.
        str --> filename=save.format(name=name, savename=savename), instead of default filename=name.
        dict --> pass to saver as kwargs. Use kwarg 'dst' to also provide filename.
                if plotter.ani, saver is movie_obj.ani(), else saver is plt.savefig().''',
    'show': '''bool
        whether to plt.show() after making plot (and, after save).
        if show when ani==True, return movie_obj.ani() (so it will display in jupyter)''',
    'close': '''bool
        whether to plt.close() after making plot (and, after save/show).
        (ignored when show==True and ani==True)''',
}

@format_docstring(**_paramdocs)
class Plotter():
    '''plotter which can be used by a PlotterManager.
    PlotterManager.KNOWN_PLOTTERS will be a dict of {{str: Plotter}} pairs.

    fname: {fname}
    f: None or callable
        the function to call (with PlotterManager as first arg) to make the plot.
        None --> get when needed, via getattr(plot_manager, plotter.fname).
    who: {who}
    kind: {kind}
    kinds: {kinds}
    ani: {ani}
    savename: {savename}
    cost: {cost}
    '''
    MOVIE_KINDS = ['movie', 'gif', 'ani', 'animation', 'animated']
    DEFAULT_COST = 20

    def __init__(self, fname, *, f=None, who=[], kind=UNSET, kinds=UNSET, ani=UNSET,
                 savename=None, cost=DEFAULT_COST, **kw_super):
        self.fname = fname
        self.f = f
        self.who = [who] if isinstance(who, str) else who
        if kind is not UNSET and kinds is not UNSET:
            raise InputConflictError(f'cannot provide both kind and kinds. Got kind={kind!r}, kinds={kinds!r}')
        if kinds is UNSET: kinds = kind
        if kinds is UNSET: kinds = []  # if still UNSET, then both kind and kinds were UNSET.
        self.kinds = [kinds] if isinstance(kinds, str) else kinds
        if ani is UNSET: ani = self._kinds_imply_ani()
        self.ani = ani
        self.savename = savename
        self.cost = cost
        super().__init__(**kw_super)

    @property
    def name(self):
        '''name of this plotter, assuming self.name looks like 'plot_name'.'''
        START = 'plot_'
        fname = self.fname
        assert fname.startswith(START), f'f.__name__ must start with {START!r}; got {fname!r}'
        return fname[len(START):]

    @property
    def savename(self):
        '''name of file to save this plot to, if not provided explicitly.
        self.savename = None --> use self.name.
        self.savename = other value --> use that value.
        '''
        return self.name if self._savename is None else self._savename
    @savename.setter
    def savename(self, value):
        self._savename = value

    # # # DETERMINE IF ANIMATED # # #
    def _kinds_imply_ani(self):
        '''infers value for self.ani, based on self.kinds.'''
        return any(k.lower() in self.MOVIE_KINDS for k in self.kinds)

    # # # PLOTTING # # #
    @format_docstring(**_paramdocs_plot, sub_ntab=1)
    def plot(self, plot_manager, *,
             save=False, show=False, close=False,
             **kw_plotter):
        '''actually call the plotter function (plot_manager.f) associated with this Plotter.
        returns plotter(**kw_plotter) (unless show=True and ani=True. Then return movie_obj.ani()).

        Might also save, show, and/or close the plot, depending on kwargs.

        save: {save}
        show: {show}
        close: {show}
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        # do the plotting
        if self.f is None:
            plotter = getattr(plot_manager, self.fname)
            result = plotter(**kw_plotter)
        else:
            result = self.f(plot_manager, **kw_plotter)
        if save != False:
            if save == True: save = dict()
            elif isinstance(save, str): save = dict(dst=save)
            else: save = save.copy()  # don't alter the user-input dict directly
            self.save(movie_obj=result, **save)
        if show:
            shown = self.show(movie_obj=result)
            if self.ani:
                return shown
        if close:
            plt.close()
        return result

    def save(self, movie_obj=None, dst=None, *args_save, bbox_inches=UNSET, **kw_save):
        '''saves the current figure. Default behaviors appropriate if current figure is self.plot().
        does movie_obj.save(...) if self.ani, else plt.savefig(...).
        returns abspath to the created file.
        
        movie_obj: None or object
            if self.ani, must provide movie_obj; will use movie_obj.ani(fname, *args, **kw)
        dst: None or str
            file name for where to save the figure. os.makedirs(exist_ok=True) as needed.
            None --> use self.savename
            str --> use dst.format(name=self.name, savename=self.savename)
        bbox_inches: UNSET or any value
            if provided, pass to plt.savefig(...) but NOT movie_obj.save(...)
        additional args and kwargs go to ani() or savefig().
        '''
        if self.ani and movie_obj is None:
            raise InputMissingError('must provide movie_obj if self.ani')
        if dst is None:
            dst = self.savename
        else:
            dst = dst.format(name=self.name, savename=self.savename)
        dst = os.path.abspath(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if self.ani:
            movie_obj.save(dst, *args_save, **kw_save)
        else:
            if bbox_inches is not UNSET: kw_save['bbox_inches'] = bbox_inches
            plt.savefig(dst, *args_save, **kw_save)
        return dst

    def show(self, movie_obj=None, **kw_ani):
        '''shows the current figure. Default behaviors appropriate if current figure is self.plot().
        does movie_obj.ani() if self.ani, else plt.show().
        additional kwargs go to ani() if calling ani().
        '''
        if self.ani and movie_obj is None:
            raise InputMissingError('must provide movie_obj if self.ani')
        if self.ani:
            return movie_obj.ani(**kw_ani)
        else:
            return plt.show()

    # # # HASHING # # #
    def __hash__(self):
        return hash((type(self), self.fname, self.f, tuple(self.who), tuple(self.kinds), self.ani, self.savename))

    # # # DISPLAY # # #
    def _repr_contents(self):
        '''return contents for __repr__'''
        result = [f'{self.fname!r}', f'who={self.who!r}', f'kinds={self.kinds!r}']
        if self.ani != self._kinds_imply_ani():
            result.append(f'ani={self.ani!r}')
        if self.cost != 20:
            result.append(f'cost={self.cost!r}')
        # f_module = self.f_module()
        # if f_module is not None:
        #     result.append(f'f_module={f_module!r}')
        return result
    
    def __repr__(self):
        return f'{type(self).__name__}({", ".join(self._repr_contents())})'


class DecoratingPlotters():
    '''Decorating functions to put plotters into a dict (self.known)

    known: None or dict
        will be a dict of {(name, person): Plotter} pairs.
        person will be None if it nobody was specified via `who`.

    self.unique will be a dict of {id(plotter): plotter} for all unique plotters.
    self.known_names will be a set of all names appearing in any plotter in self.known.
    self.known_kinds will be a set of all kinds appearing in any plotter in self.known.
    self.known_who will be a set of all people appearing in any plotter in self.known.

    Example: known_plotter = DecoratingPlotters(storage_dict)
        @known_plotter
        def plot_name1(...):
            ...
        @known_plotter(who='sam', kinds=['movie', 'density'])
        def plot_name2(...):
            ...
        # at this point, we have:
        #   known_plotter.known == {'name1': Plotter('plot_name1'),
        #                           'name2': Plotter('plot_name2', who='sam', kinds=['movie', 'density'])}
    '''
    plotter_cls = Plotter

    def __init__(self, known=None):
        if known is None: known = dict()
        self.known = known
        self._update_unique()

    def _update_unique(self):
        unique = {}
        for plotter in self.known.values():
            if id(plotter) not in unique:
                unique[id(plotter)] = plotter
        self.unique = unique

    @property
    def known_names(self):
        '''set of all names appearing in any plotter in self'''
        return {p.name for p in self.unique.values()}

    @property
    def known_kinds(self):
        '''set of all kinds appearing in any plotter in self'''
        return {k for p in self.unique.values() for k in p.kinds}

    @property
    def known_who(self):
        '''set of all people appearing in any plotter in self.'''
        return {w for p in self.unique.values() for w in p.who}

    @format_docstring(**_paramdocs, sub_ntab=1)
    def track_f(self, f, *,  who=[], kind=UNSET, kinds=UNSET, ani=UNSET, savename=None,
                cost=Plotter.DEFAULT_COST, aliases=[]):
        '''add f to self.known as a Plotter.
        f must look like 'plot_name' where name can be any string;
            will make self.known[(name, person)] = Plotter(f, ...)

        who: {who}
        kind: {kind}
        kinds: {kinds}
        ani: {ani}
        savename: {savename}
        cost: {cost}
        aliases: {aliases}
        '''
        fname = f.__name__
        START = 'plot_'
        assert fname.startswith(START), f'f.__name__ must start with {START!r}; got {fname!r}'
        name = fname[len(START):]
        plotter = self.plotter_cls(fname, f=f, who=who, kind=kind, kinds=kinds, ani=ani, savename=savename, cost=cost)
        if getattr(self, 'cls_associated_with', None) is not None:
            plotter.cls_where_defined = self.cls_associated_with
        for key in self._get_keys(name, who, aliases):
            self.known[key] = plotter
        # [EFF] might be inefficient to run _update_unique() every time,
        #  but this only occurs when defining new functions to track,
        #  not while running code, so hopefully it's not a big deal.
        self._update_unique()

    def _get_keys(self, name, who, aliases):
        '''get keys for where to store the plotter with this name, in self.known.'''
        if isinstance(who, str):
            who = [who]
        elif len(who)==0:
            who = [None]
        allnames = [name] + list(aliases)
        return [(n, w) for n in allnames for w in who]

    @format_docstring(**_paramdocs, sub_ntab=1)
    def decorator(self, *, who=[], kind=UNSET, kinds=UNSET, ani=UNSET, savename=None,
                  cost=Plotter.DEFAULT_COST, aliases=[]):
        '''returns decorator for plot manager's f(self, *args, **kw), which returns f, unchanged...
        but also sets self.known[name] = Plotter(f.__name__, ...).
        (requires f.__name__ looks like 'plot_name')

        who: {who}
        kind: {kind}
        kinds: {kinds}
        ani: {ani}
        savename: {savename}
        cost: {cost}
        aliases: {aliases}
        '''
        def return_f_after_some_bookkeeping(f):
            '''returns f, unchanged, after calling self.track_f(f, ...) to add it to self.known.'''
            self.track_f(f, who=who, kind=kind, kinds=kinds, ani=ani, savename=savename, cost=cost, aliases=aliases)
            return f
        return return_f_after_some_bookkeeping

    def __call__(self, f=None, *, who=[], kind=UNSET, kinds=UNSET, ani=UNSET,
                 savename=None, cost=Plotter.DEFAULT_COST, aliases=[], **kw_decorator):
        '''if f is provided, return self.decorator(**kw)(f). Otherwise, return self.decorator(**kw).
        This enables instances to be used as decorators directly, i.e. "@self",
            or used as decorators after providing kwargs, e.g. "@self(who='sam', kind='movie')".
        See help(type(self)) for examples.
        See help(self.decorator) for parameter descriptions.
        '''
        kw = dict(who=who, kind=kind, kinds=kinds, ani=ani, savename=savename, cost=cost,
                  aliases=aliases, **kw_decorator)
        if f is None:
            return self.decorator(**kw)
        else:
            return self.decorator(**kw)(f)

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'known_names={self.known_names}',
                    f'known_who={self.known_who}',
                    f'known_kinds={self.known_kinds!r}']
        contents_str = ',\n'.join(contents)
        return f'{type(self).__name__}({contents_str})'


### --------------------- MetaPlotterManager --------------------- ###

class MetaPlotterManager(MetaQuantTracking):
    '''metclass which predefines some things for registering plotters, in the class namespace:
        KNOWN_PLOTTERS - dict of {(var, who): Plotter} for all f decorated with @known_plotter
        known_plotter - use @known_plotter to decorate functions.
        UNIQUE_PLOTTERS - list of unique Plotter objects in this class
                (KNOWN_PLOTTERS.values() lists any Plotter with len(who)>=2 multiple times;
                UNIQUE_PLOTTERS includes each Plotter only once.)
    '''
    # note: inheriting from MetaQuantTracking is required in order to be compatible with QuantityLoader;
    #  the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases.
    @classmethod
    def __prepare__(_metacls, _name, bases):
        super_result = super().__prepare__(_name, bases)
        KNOWN_PLOTTERS = dict()
        for base in bases:
            # So that keys appear in __mro__ order, must iterate through bases in order.
            # So, the first time a key appears, it points to the earliest (in __mro__ order)
            # implementation, so it should not be overwritten if it appears again.
            #    Hence, avoid dict.update; use dict.setdefault instead.
            #
            # [TODO] double-check these docs. Adapted directly from MetaQuantTracking.
            # Additionally, need to avoid the following:
            #    'vv' defined in Class0.
            #    Class1 subclasses Class0 but does NOT also define 'vv'.
            #    Class2 subclasses Class0 and defines 'vv' too.
            #    class Class3(Class1, Class2): ...
            #    now, Class3.mro() has [Class1, Class2, Class0], so:
            #      Class3.plot_vv uses Class2.plot_vv.
            #        (This is good; should use the earliest-in-mro() plot_vv to get value.)
            #      Class3.KNOWN_PLOTTERS['vv'] uses Class1.KNOWN_PLOTTERS['vv'].
            #        (This is bad; should use the KNOWN_PLOTTERS attached to plot_vv.)
            # To avoid this, below checks where key was defined if it appears in dict already;
            #    if it was defined in a subclass, don't overwrite.
            base_kplots = getattr(base, 'KNOWN_PLOTTERS', {})
            for k, v in base_kplots.items():
                try:
                    existing = KNOWN_PLOTTERS[k]
                except KeyError:  # didn't exist yet
                    KNOWN_PLOTTERS[k] = v
                else:  # existed already
                    # only overwrite if this base is a subclass of where the existing value was defined.
                    if issubclass(base, existing.cls_where_defined):
                        KNOWN_PLOTTERS[k] = v
        known_plotter = DecoratingPlotters(KNOWN_PLOTTERS)
        return dict(**super_result,
                    KNOWN_PLOTTERS=KNOWN_PLOTTERS,
                    known_plotter=known_plotter)

    def __init__(cls, *args, **kw):
        cls.known_plotter.cls_associated_with = cls
        for k, v in cls.KNOWN_PLOTTERS.items():
            if not hasattr(v, 'cls_where_defined'):
                v.cls_where_defined = cls
        unique = {}
        for plotter in cls.KNOWN_PLOTTERS.values():
            if id(plotter) not in unique:
                unique[id(plotter)] = plotter
        cls.UNIQUE_PLOTTERS = list(unique.values())
        super().__init__(*args, **kw)


### --------------------- PlotterManager --------------------- ###

_paramdocs_get_plotters = {
    'name': '''None or str
        plotter name. E.g. 'deltafrac_n'.
        None --> include all plotters regardless of 'name'.''',
    'who': '''UNSET, None, str, or list.
        person associated with the plotter.
        UNSET --> include plotters regardless of 'who'.
        None --> require len(plotter.who) == 0.
        str --> require this name to be in plotter.who.
        list --> require at least one of these to be in plotter.who
                (or, if None in list, allow len(plotter.who)==0, too)''',
    'kind': '''UNSET, str, or list.
        kind associated with the plotter.
        UNSET --> include plotters regardless of 'kind'.
        str --> require this kind to be in plotter.kinds.
        list --> require at least one of these to be in plotter.kinds.''',
    'all_whos': '''UNSET or list.
        include only plotters with ALL of these people in plotter.who.''',
    'all_kinds': '''UNSET or str.
        include only plotters with ALL of these kinds in plotter.kinds.''',
    'skip_who': '''list
        exclude plotters with any of these people in plotter.who.''',
    'skip_kinds': '''list
        exclude plotters with any of these kinds in plotter.kinds.''',
    'min_cost': '''None or number
        exclude plotters with cost < min_cost.
        None --> no minimum.''',
    'max_cost': '''None or number
        exclude plotters with cost > max_cost.
        None --> no maximum.''',
}


class PlotterManager(metaclass=MetaPlotterManager):
    '''class to help with managing plotters.'''

    def get_plotter(self, name, who=UNSET):
        '''gets the Plotter associated with this name and who.
        Roughly equivalent: self.KNOWN_PLOTTERS[(name, who)]

        name: str or Plotter
            name of the plotter to use, or a Plotter instance.
        who: UNSET, None, or str
            person associated with the plotter.
            UNSET --> use the plotter with this name; crash if found multiple same-named plotters.

        see also: self.get_plotters(), which is good if you don't know 'who', or want multiple plotters.
        '''
        if isinstance(name, Plotter):
            return name
        elif who is UNSET:
            plotters = self.get_plotters(name=name, who=who)
            if len(plotters) == 0:
                raise PlottingNotImplementedError(f'no KNOWN_PLOTTERS with name={name!r}.')
            elif len(plotters) >= 2:
                errmsg = f'multiple KNOWN_PLOTTERS with name={name!r}, and did not specify who. Found: {plotters}'
                raise PlottingAmbiguityError(errmsg)
            else:  # len(plotters) == 1
                return plotters[0]
        else:
            try:
                return self.KNOWN_PLOTTERS[(name, who)]
            except KeyError:
                errmsg = f'plotter (name={name!r}, who={who!r}) not found in KNOWN_PLOTTERS.'
                same_name_different_person = [k for k in self.KNOWN_PLOTTERS.keys() if k[0]==name]
                if len(same_name_different_person) > 0:
                    errmsg = errmsg + f'\n(maybe these plotters are relevant, though?: {same_name_different_person!r})'
                raise PlottingNotImplementedError(errmsg) from None

    @format_docstring(**_paramdocs_get_plotters, sub_ntab=1)
    def get_plotters(self, who=UNSET, kind=UNSET, *, name=None,
                     all_whos=UNSET, all_kinds=UNSET, skip_who=[], skip_kinds=[],
                     min_cost=None, max_cost=None, sortby=None,
                     returns='plotters'):
        '''return list of all plotters associated with these inputs.
        If called with no inputs, just returns a copy of self.UNIQUE_PLOTTERS.

        who: {who}
        kind: {kind}
        name: {name}
        all_whos: {all_whos}
        all_kinds: {all_kinds}
        skip_who: {skip_who}
        skip_kinds: {skip_kinds}
        min_cost: {min_cost}
        max_cost: {max_cost}

        sortby: None or 'cost'
            tells how to sort the result (if returns=='plotters').
            None --> keep in order they appear in self.UNIQUE_PLOTTERS.
            'cost' --> sort by plotter.cost values.

        returns: 'plotters', 'names', 'who', 'kind', or 'kinds'
            'plotters' --> returns list of plotters
            'names' --> returns set of all names associated with at least 1 plotter in result.
            'who' --> returns set of all people associated with at least 1 plotter in result.
            'kind' or 'kinds' --> returns set of all kinds associated with at least 1 plotter in result.
        '''
        result = list(self.UNIQUE_PLOTTERS)
        if name is not None:
            result = [p for p in result if p.name==name]
        if min_cost is not None:
            result = [p for p in result if p.cost >= min_cost]
        if max_cost is not None:
            result = [p for p in result if p.cost <= max_cost]
        if who is not UNSET:
            if who is None or isinstance(who, str):
                who = [who]
            new_result = []
            for p in result:
                if len(p.who)==0 and None in who:
                    new_result.append(p)
                elif any(w in p.who for w in who):
                    new_result.append(p)
            result = new_result
        if kind is not UNSET:
            if isinstance(kind, str):
                result = [p for p in result if kind in p.kinds]
            else:
                result = [p for p in result if any(k in p.kinds for k in kind)]
        if all_whos is not UNSET:
            result = [p for p in result if all(w in p.who for w in all_whos)]
        if all_kinds is not UNSET:
            result = [p for p in result if all(k in p.kinds for k in all_kinds)]
        if skip_who:
            result = [p for p in result if not any(w in p.who for w in skip_who)]
        if skip_kinds:
            result = [p for p in result if not any(k in p.kinds for k in skip_kinds)]
        # returning result
        if returns == 'names':
            result = set(p.name for p in result)
        elif returns == 'who':
            result = set(w for p in result for w in p.who)
        elif returns == 'kind' or returns == 'kinds':
            result = set(k for p in result for k in p.kinds)
        elif returns == 'plotters':
            if sortby == 'cost':
                result = sorted(result, key=lambda p: p.cost)
        else:
            raise InputError(f'returns={returns!r}. Expected "plotters", "names", "who", "kind", or "kinds".')
        return result
    
    @format_docstring(**_paramdocs_plot, sub_ntab=1)
    def plot(self, name, who=UNSET, *, save=False, show=False, close=False, **kw_plotter):
        '''makes a single plot using the relevant plotter.

        name: str or Plotter
            name of the plotter to use, or a Plotter instance.
            (if Plotter, use directly and ignore 'who' input.)
        who: UNSET, None, or str
            person associated with the plotter.
            UNSET --> use the plotter with this name; crash if found multiple same-named plotters.
        save: {save}
        show: {show}
        close: {show}
        additional kwargs go to plotter.plot(...)

        see also: self.get_plotters(), self.save_plots().
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        plotter = self.get_plotter(name)
        kw = dict(save=save, show=show, close=close, **kw_plotter)
        return plotter.plot(self, **kw)

    @format_docstring(**_paramdocs_get_plotters, **_paramdocs_plot, sub_ntab=2)
    def save_plots(self, kind=UNSET, who=UNSET, *, name=None, 
                   all_whos=UNSET, all_kinds=UNSET, skip_who=[], skip_kinds=[],
                   min_cost=None, max_cost=None,
                   dst='{savename}', save_log=True, log_extras=[],
                   kw_save=dict(), bbox_inches=UNSET, dpi=UNSET,
                   show=False, close=True,
                   print_freq=0, **kw_plotter):
        '''saves all plots from plotters associated with these inputs.
        returns dict of {{plotter: plotter result}} for all plotters called.
        Consider checking self.get_plotters() first to learn which plotters will be included.

        For choosing which plotters to include:
            kind: {kind}
            who: {who}
            name: {name}
            all_whos: {all_whos}
            all_kinds: {all_kinds}
            skip_who: {skip_who}
            skip_kinds: {skip_kinds}
            min_cost: {min_cost}
            max_cost: {max_cost}

        For plotting:
            dst: str
                where to save plots to. Hit by dst.format(name=plotter.name, savename=plotter.savename).
                if not abspath, save to os.path.join(self.unique_notes_dirname, dst) if possible,
                    else save to dst within current directory.
            save_log: bool or str
                whether to save a log of plot progress to _save_plots_log.txt file.
                str --> save to this file name. If not abspath, put it in dir implied by dst (see above).
                The log tells current datetime, version info about PlasmaCalcs, and plot timing updates.
            log_extras: list of str
                extra lines to put in the log "header", if doing save_log.
            kw_save: dict
                kwargs to pass to plotter.save(...)
            bbox_inches: UNSET or any value
                if provided, added to kw_save.
            dpi: UNSET or any value
                if provided, added to kw_save.
            show: {show}
            close: {show}

            additional kwargs go to plotter.plot(...)

        Misc:
            print_freq: number
                minimum seconds between printing progress updates.
                -1 --> never print; 0 --> always print.

        see also: self.get_plotters(), self.plot().
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        result = {}
        plotters = self.get_plotters(name=name, who=who, kind=kind,
                                     all_whos=all_whos, all_kinds=all_kinds,
                                     skip_who=skip_who, skip_kinds=skip_kinds,
                                     min_cost=min_cost, max_cost=max_cost, sortby='cost')
        kw_save = kw_save.copy()
        if bbox_inches is not UNSET: kw_save.setdefault('bbox_inches', bbox_inches)
        if dpi is not UNSET: kw_save.setdefault('dpi', dpi)
        if not os.path.isabs(dst):
            dst = os.path.join(getattr(self, 'unique_notes_dirname', os.getcwd()), dst)
        if save_log == True:
            save_log = '_save_plots_log.txt'
        if save_log and not os.path.isabs(save_log):
            save_log = os.path.join(os.path.dirname(dst), save_log)
        save = dict(dst=dst, **kw_save)
        updater = ProgressUpdater(print_freq=print_freq)
        with contextlib.ExitStack() as context_stack:
            logfile = None
            try:
                for i, plotter in enumerate(plotters):
                    # logging progress
                    message = f'plotting {i+1:2d} of {len(plotters):2d}: {plotter.savename} (cost={plotter.cost})'
                    message = f'{message:<60} | '
                    updater.print(message)
                    full_message = updater.message_to_print(message)  # includes info about time elapsed.
                    # >> actually plotting <<
                    plotted = self.plot(plotter, save=save, show=show, close=close, **kw_plotter)
                    result[plotter] = plotted
                    # logging progress (only start logging after at least 1 plot completes successfully.)
                    if save_log:  # [TODO] encapsulate some of this to put it elsewhere...
                        if i==0:  # first time! open file and make "header"
                            logfile = context_stack.enter_context(open(save_log, 'a'))
                            codeinfo = code_snapshot_info()
                            lines = ['----------',
                                    codeinfo.pop("datetime"),
                                    'Created by PlasmaCalcs save_plots().',
                                    str(codeinfo),
                                    *log_extras]
                            logfile.write('\n'.join(lines) + '\n')
                        logfile.write(full_message + '\n')
            except BaseException as err:  # BaseException is okay because we raise immediately after logging.
                if logfile is not None:
                    logfile.write(f'CRASHED DUE TO ERROR: {err!r}\n')
                raise err
            finally:
                # logging progress
                if save_log:
                    updater.finalize('save_plots', always=True, file=logfile)
                    logfile.write('\n----------\n')
                updater.finalize('save_plots')
        return result
