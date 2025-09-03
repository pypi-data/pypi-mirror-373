"""
File Purpose: trees
"""

from IPython.display import display, HTML

from .display import repr_simple
from .properties import (
    weakref_property_simple, simple_property,
)
from ..defaults import DEFAULTS

### --------------------- Tree --------------------- ###

class Tree():
    '''node in a Tree. Might have any number of children, might have one parent.
    obj: any object.
        the object stored here, in this node.
    '''
    _assert_type=None  # if not None, assert isinstance(obj, _assert_type) when creating new nodes.

    def __init__(self, obj, parent=None):
        if self._assert_type is not None:
            if not isinstance(obj, self._assert_type):
                raise TypeError(f'obj must be an instance of {self._assert_type}, but got type(obj)={type(obj)}')
        self.obj = obj
        self.children = []
        self.parent = parent   # property; self.parent=parent calls self.set_parent(parent).

    # # # PROPERTIES # # #
    @property
    def parent(self):
        '''parent node of self. None if self is root.
        When set to a value, calls self.set_parent(value),
            which also updates tracking info appropriately, and updates parent's children.
        '''
        return self.parent_ref
    @parent.setter
    def parent(self, value):
        self.set_parent(value)

    parent_ref = weakref_property_simple('_parent_ref',
            doc='''stores parent value, but internally uses weakref to avoid circular references.
            Users should always use self.parent instead.''')

    depth = simple_property('_depth', default=0,
            doc='''number of layers above self. (parent, parent's parents, etc.)
            depth = 0 for the node with parent = None.''')
    height = simple_property('_height', default=0,
            doc='''number of layers below self. (children, children's children, etc.)
            height = 0 for a node with no children.''')
    size = simple_property('_size', default=1,
            doc='''number of nodes in this tree. (here and below)
            size = 1 for a node with no children.''')

    # # # TRACKING INFO WHEN ADDING CHILDREN OR PARENTS # # #
    def set_parent(self, parent, *, _internal=False):
        '''sets self.parent = parent. Also, parent.add_child(self), unless _internal=True.
        Users should use self.parent = parent instead of calling set_parent directly.
        '''
        self._on_setting_parent(parent)
        self.parent_ref = parent
        if (not _internal) and (parent is not None):
            parent.add_child(self)

    def add_child(self, child):
        '''adds this child (a Tree) to self.children. Also, child.set_parent(self).
        returns the added child.
        '''
        self.children.append(child)
        child.set_parent(self,
                _internal=True,  # avoids recursion from add_child inside set_parent.
                )
        self._on_added_child(child)
        return child

    def _on_setting_parent(self, parent):
        '''called immediately before setting self.parent = parent.
        Tracks depth, height, size. This method does not connect any parents or children.
        '''
        self_parent = getattr(self, 'parent', None)  # getattr -> even works before setting self.parent!
        if self_parent is parent:
            return  # don't need to do anything, didn't update parent at all!
        elif self_parent is not None:
            raise NotImplementedError('swapping parents (after setting parent = non-None value)!')
        self.depth = 0 if parent is None else parent.depth + 1
        for child in self.children:
            child._on_adding_ancestor(parent)

    def _on_adding_ancestor(self, ancestor):
        '''called immediately before adding an ancestor to self (i.e., self.parent, parent of self.parent, etc)
        Tracks depth, height, size. This method does not connect any parents or children.
        '''
        self.depth = self.parent.depth + 1
        for child in self.children:
            child._on_adding_ancestor(ancestor)
        
    def _on_added_child(self, child):
        '''called immediately after adding a child to self.
        Tracks depth, height, size. This method does not connect any parents or children.
        '''
        self._on_added_descendant(child)
    
    def _on_added_descendant(self, descendant):
        '''called immediately after adding a descendant to self (or any of self.children).
        Tracks depth, height, size. This method does not connect any parents or children.
        '''
        self.height = 1 + max(child.height for child in self.children)
        self.size += descendant.size
        if self.parent is not None:
            self.parent._on_added_descendant(descendant)

    # # # CHILDREN # # #
    def make_child(self, obj):
        '''makes a child of self, with obj as its stored object, and returns the child.'''
        child = type(self)(obj, parent=self)
        return child

    def make_children(self, objs):
        '''make_child(obj) for obj in objs; returns the list of newly made children.'''
        return [self.make_child(obj) for obj in objs]

    # # # ITERATION # # #
    def flat(self, *, include_self=False):
        '''returns a generator which iterates over all of self's descendants, in depth-first order.
        if include_self, yield self first.
        '''
        if include_self:
            yield self
        for child in self.children:
            yield child
            for descendant in child.flat():
                yield descendant

    def __iter__(self):
        '''iterates over self.children.'''
        return iter(self.children)

    def enumerate_flat(self, *, include_self=False):
        '''returns a generator which iterates over all of self's descendants, in depth-first order,
        yielding (index, node) pairs, such that self[index] == node.
            Note that index will be a tuple with length == node.depth.
        if include_self, yield self first, as: ((), self)).
        '''
        if include_self:
            yield (), self
        for i, child in enumerate(self.children):
            yield (i,), child
            for jtuple, descendant in child.enumerate_flat():
                yield (i,) + jtuple, descendant

    def flat_branches_until(self, branches_until, *, include_self=False):
        '''returns a generator which iterates over all of self's descendants, in depth-first order,
        but stop looking at descendants on a branch as soon as branches_until(node).
        E.g. self.flat_branches_until(lambda node: node.obj==7) will be similar to flat,
            but won't go to any descendants for any node with obj==7.

        if include self, yield self first, and check branches_until(self) before continuing.
        otherwise, never check branches_until(self).
        '''
        if include_self:
            yield self
            if branches_until(self):
                return  # stop iteration
        for child in self.children:
            yield child
            if not branches_until(child):
                for descendant in child.flat_branches_until(branches_until):
                    yield descendant

    # # # INDEXING # # #
    def __getitem__(self, i):
        '''returns self.children[i]. If i is a tuple, index repeatedly, e.g. self[i[0]][i[1]][i[2]]...'''
        if isinstance(i, tuple):
            result = self
            for j in i:
                result = result[j]
            return result
        else:
            return self.children[i]

    # # # DISPLAY # # #
    def __repr__(self):
        contents = [f'[depth={self.depth}, height={self.height}, size={self.size}]']
        contents.append(f'obj={repr_simple(self.obj)}')
        return f'{self.__class__.__name__}({", ".join(contents)})'

    def _shorthand_repr(self):
        '''returns shorthand repr for this node (without children): "((depth, height, size)) obj".'''
        return f'(({self.depth}, {self.height}, {self.size})) {repr_simple(self.obj)}'

    DEFAULT_TREE_SHOW_DEPTH = None
    DEFAULT_TREE_SHOW_MAX_DEPTH = None
    DEFAULT_TREE_SHORTHAND = None

    def html(self, show_depth=None, max_depth=None, *, shorthand=None):
        '''returns html for displaying self and all of self's children.
        show_depth: None or int
            max number of layers of tree to show by default (i.e. "not hidden" by default)
            None --> use self.DEFAULT_TREE_SHOW_DEPTH if defined else DEFAULTS.TREE_SHOW_DEPTH
        max_depth: None or int
            max number of layers of tree to render (even if all layers are "not hidden").
            Anything deeper will not be converted to html string.
            None --> use self.DEFAULT_TREE_SHOW_MAX_DEPTH if defined else DEFAULTS.TREE_SHOW_MAX_DEPTH
        shorthand: None or bool
            whether to use shorthand for the "Tree([depth=N, height=N, size=N], obj=...)" part of the repr.
            True --> use shorthand; replace that^ with: "((N, N, N)) ..."
            None --> use self.DEFAULT_TREE_SHORTHAND if defined else DEFAULTS.TREE_SHORTHAND
        '''
        if show_depth is None: show_depth = getattr(self, 'DEFAULT_TREE_SHOW_DEPTH', None)
        if show_depth is None: show_depth = DEFAULTS.TREE_SHOW_DEPTH
        if max_depth is None: max_depth = getattr(self, 'DEFAULT_TREE_SHOW_MAX_DEPTH', None)
        if max_depth is None: max_depth = DEFAULTS.TREE_SHOW_MAX_DEPTH
        if shorthand is None: shorthand = getattr(self, 'DEFAULT_TREE_SHORTHAND', None)
        if shorthand is None: shorthand = DEFAULTS.TREE_SHORTHAND
        open = (self.height == 0) or (self.depth < show_depth)  # height==0 always open, to reveal no children.
        open_str = ' open' if open else ''
        str_self = self._shorthand_repr() if shorthand else repr(self)
        str_self = str_self.replace('<', '&lt').replace('>', '&gt')  # escape '<' & '>' characters.
        result = f'<details{open_str}><summary>{str_self}</summary>'  # pre prevents html formatting.
        if self.depth < max_depth:
            for child in self.children:
                result += child.html(show_depth=show_depth, max_depth=max_depth, shorthand=shorthand)
        else:
            result += f'... hidden; max render depth={max_depth} ...</p>'
        result += '</details>'
        return result

    def _repr_html_(self):
        '''returns html string for displaying self. (this display hook is used by Jupyter automatically.).

        Includes self.html() and DEFAULTS.TREE_CSS.

        [TODO] apply the css to ONLY this output cell in Jupyter, instead of all output cells...
        '''
        result = f'{DEFAULTS.TREE_CSS}\n{self.html()}'
        return result

    def display(self, show_depth=None, max_depth=None, *, shorthand=None):
        '''display self in html. Includes self.html() and DEFAULTS.TREE_CSS.
        show_depth: None or int
            max number of layers of tree to show by default (i.e. "not hidden" by default)
            None --> use self.DEFAULT_TREE_SHOW_DEPTH if defined else DEFAULTS.TREE_SHOW_DEPTH
        max_depth: None or int
            max number of layers of tree to render (even if all layers are "not hidden").
            Anything deeper will not be converted to html string.
            None --> use self.DEFAULT_TREE_SHOW_MAX_DEPTH if defined else DEFAULTS.TREE_SHOW_MAX_DEPTH
        shorthand: None or bool
            whether to use shorthand for the "Tree([depth=N, height=N, size=N], obj=...)" part of the repr.
            True --> use shorthand; replace that^ with: "((N, N, N)) ..."
            None --> use self.DEFAULT_TREE_SHORTHAND if defined else DEFAULTS.TREE_SHORTHAND
        '''
        s = self.html(show_depth=show_depth, max_depth=max_depth, shorthand=shorthand)
        result = f'{DEFAULTS.TREE_CSS}\n{s}'
        display(HTML(s))
