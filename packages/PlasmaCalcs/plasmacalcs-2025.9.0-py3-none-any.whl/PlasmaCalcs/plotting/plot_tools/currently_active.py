"""
File Purpose: manage currently active figure, axs, etc.
"""

import matplotlib.pyplot as plt

from ...tools import NO_VALUE

### --------------------- as functions --------------------- ###

def current_figure_exists():
    '''tells whether there is a "current" figure.'''
    return len(plt.get_fignums()) > 0

def current_figure_or_None():
    '''returns current figure, or None if there is no "current figure".'''
    return plt.gcf() if current_figure_exists() else None

def current_axes_exists():
    '''tells whether there is a "current" axes.'''
    fig = current_figure_or_None()
    return False if fig is None else (len(fig.axes) > 0)

def current_axes_or_None():
    '''returns current axes, or None if there is no "current axes".'''
    return plt.gca() if current_axes_exists() else None

def current_axes_has_data():
    '''returns whether the current axes has any data plotted on it.'''
    ax = current_axes_or_None()
    return False if ax is None else ax.has_data()

def current_image_exists():
    '''tells whether there is a "current" image.'''
    return plt.gci() is not None

def current_image_or_None():
    '''returns current image, or None if there is no "current image".'''
    return plt.gci()


### --------------------- as context managers --------------------- ###

def maintaining_current_plt(*maintain, default=['all']):
    '''returns context manager which restores current figure, axes, image upon exit.
    If the original figure / axes / image was None, it will not be restored to None. [TODO] change this?
    maintain: strings from ('figure', 'axes', 'image', 'all')
        maintain (only) these values. E.g. ['figure'] --> maintain current figure and axes.
        'all' --> maintain all values.
    default: list of strings, default ['all']
        if len(maintain)==0, instead use maintain = default.

    see also: using_current_plt
    '''
    return MaintainingCurrentPlt(*maintain, default=default)

def using_current_plt(*, figure=NO_VALUE, axes=NO_VALUE, image=NO_VALUE):
    '''returns context manager which sets values for "current" figure, axes, image upon entry; restores upon exit.
    If the original figure / axes / image was None, it will not be restored to None. [TODO] change this?
    figure, axes, image: objects or NO_VALUE
        if provided, set that value as the current value, upon entry.

    see also: maintaining_current_plt
    '''
    return UsingCurrentPlt(figure=figure, axes=axes, image=image)

def maintaining_current_figure(enabled=True):
    '''returns context manager which (if enabled) restores current figure upon exit. See also: maintaining_current_plt'''
    return maintaining_current_plt(*(['figure'] if enabled else []), default=[])
def maintaining_current_axes(enabled=True):
    '''returns context manager which (if enabled) restores current axes upon exit. See also: maintaining_current_plt'''
    return maintaining_current_plt(*(['axes'] if enabled else []), default=[])
def maintaining_current_image(enabled=True):
    '''returns context manager which (if enabled) restores current image upon exit. See also: maintaining_current_plt'''
    return maintaining_current_plt(*(['axes'] if enabled else []), default=[])
def using_current_figure(figure):
    '''returns context manager which sets current figure upon entry; restores upon exit. See also: using_current_plt'''
    return using_current_plt(figure=figure)
def using_current_axes(axes):
    '''returns context manager which sets current axes upon entry; restores upon exit. See also: using_current_plt'''
    return using_current_plt(axes=axes)
def using_current_image(image):
    '''returns context manager which sets current image upon entry; restores upon exit. See also: using_current_plt'''
    return using_current_plt(image=image)

class MaintainingCurrentPlt():
    '''context manager which restores current figure, axes, image upon exit.
    If the original figure / axes / image was None, it will not be restored to None. [TODO] change this?
    maintain: strings from ('figure', 'axes', 'image', 'all')
        maintain (only) these values. E.g. ['figure'] --> maintain current figure and axes.
        'all' --> maintain all values.
    default: list of strings, default ['all']
        if len(maintain)==0, instead use maintain = default.
    '''
    def __init__(self, *maintain, default=['all']):
        if len(maintain)==0:
            maintain = default
        figure = axes = image = False
        if 'all' in maintain:
            figure = axes = image = True
        else:
            figure = ('figure' in maintain)
            axes = ('axes' in maintain)
            image = ('image' in maintain)
        self.maintain_figure = figure
        self.maintain_axes = axes
        self.maintain_image = image

    def __enter__(self):
        self.memory = dict()
        if self.maintain_figure:
            self.memory['figure'] = current_figure_or_None()
        if self.maintain_axes:
            self.memory['axes'] = current_axes_or_None()
        if self.maintain_image:
            self.memory['image'] = current_image_or_None()

    def __exit__(self, *args_unused):
        if self.maintain_figure and (self.memory['figure'] is not None):
            plt.figure(self.memory['figure'])
        if self.maintain_axes and (self.memory['axes'] is not None):
            plt.sca(self.memory['axes'])
        if self.maintain_image and (self.memory['image'] is not None):
            plt.sci(self.memory['image'])


class UsingCurrentPlt(MaintainingCurrentPlt):
    '''context manager which sets values for "current" figure, axes, image upon entry; restores upon exit.
    If the original figure / axes / image was None, it will not be restored to None. [TODO] change this?
    Only actually sets (restores) the values which are (were) provided, via kwargs.
    '''
    def __init__(self, *, figure=NO_VALUE, axes=NO_VALUE, image=NO_VALUE):
        self.figure = figure
        self.axes = axes
        self.image = image
        self.maintain_figure = (figure is not NO_VALUE)
        self.maintain_axes = (axes is not NO_VALUE)
        self.maintain_image = (image is not NO_VALUE)

    def __enter__(self):
        super().__enter__()
        if self.figure is not NO_VALUE:
            plt.figure(self.figure)
        if self.axes is not NO_VALUE:
            plt.sca(self.axes)
        if self.image is not NO_VALUE:
            plt.sci(self.image)
