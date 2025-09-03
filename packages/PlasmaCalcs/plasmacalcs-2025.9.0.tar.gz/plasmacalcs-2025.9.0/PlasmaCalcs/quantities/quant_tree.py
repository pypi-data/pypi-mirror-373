"""
File Purpose: QuantTree - tree of LoadableQuantity objects.
"""
import contextlib

from .quantity_tools import MatchedQuantity, MatchedVar, MatchedPattern
from ..errors import InputError
from ..tools import Tree


### --------------------- QuantTree --------------------- ###

class QuantTree(Tree):
    '''Tree of MatchedQuantity objects.
    See QuantTree.display() for display options.
    Most common use-case:
        QuantTree.from_quantity_loader(quantity_loader, var)
    will tell the QuantTree associated with loading that var from quantity_loader.
    Result might depend on current values of quantity_loader attributes.
    '''
    _assert_type = MatchedQuantity  # assert isinstance(obj, _assert_type) when creating new nodes.

    @classmethod
    def from_quantity_loader(cls, quantity_loader, var, *, missing_ok=False, **kw_call_options):
        '''returns a QuantTree from a QuantityLoader and var name.
        This is the tree of MatchedQuantity objects which will all be loaded if loading var.
            (MatchedQuantity objects consist of a var, a LoadableQuantity, and possibly a _match.)

        quantity_loader: QuantityLoader instance or subclass
            the loader containing info about var dependencies.
            if class, might not be possible to get as many vars' dependencies
                (and will crash if need to know current values of attributes, to determine dependency list)
        missing_ok: bool
            whether to be lenient sometimes when missing details that would allow to fully determine deps.
            see help(MatchedQuantity.dep_vars) for more details.

        additional kwargs appearing in quantity_loader.kw_call_options()
            will be passed to quantity_loader.using(**kw_call_options), if quantity_loader is a QuantityLoader instance.
            If any additional kwargs don't appear in kw_call_options(), crash.
        '''
        if isinstance(quantity_loader, type):
            using = None
        else:
            using = quantity_loader._pop_kw_call_options(kw_call_options)
            if kw_call_options:
                errmsg = (f'unexpected kwargs: {kw_call_options!r}.\n'
                          f'See quantity_loader.kw_call_options() for allowed options.')
                raise InputError(errmsg)
        with contextlib.ExitStack() as context_stack:
            if using:
                context_stack.enter_context(quantity_loader.using(**using))
            matched_quant = quantity_loader.match_var(var)
            tree = cls(matched_quant)  # <-- root node of tree
            dep_vars = matched_quant.dep_vars(quantity_loader=quantity_loader, missing_ok=missing_ok)
            for dep_var in dep_vars:
                if isinstance(dep_var, str):
                    dep_tree = cls.from_quantity_loader(quantity_loader, dep_var)
                elif isinstance(dep_var, tuple):
                    var, using = dep_var
                    with quantity_loader.using(**using):
                        dep_tree = cls.from_quantity_loader(quantity_loader, var)
                else:
                    raise TypeError(f'expected dep_var to be str or tuple, but got {dep_var!r}.')
                tree.add_child(dep_tree)
        return tree
        
    def loading_dims(self):
        '''return a list of all the dims for loading across, as implied by this tree.

        This is the set of quantity.dims for all quantities in this tree (self and all descendants), but:
            - if quantity.ignores_dims is non-empty, exclude those dims for that node and all its descendants.
            - if quantity.reduces_dims is non-empty, exclude those dims for the result
                (even if a sybling node has a quantity that uses those dims).
        '''
        # maintain dims order by using a list instead of a set. (Not worried about speed here.)
        # dims from here
        dims = self.obj.dims
        if dims is None:
            result = []
        else:
            result = list(dims)  # copy of dims, as a list.
        # dims from children
        for child in self.children:
            child_dims = child.loading_dims()
            for dim in child_dims:
                if dim not in result:
                    result.append(dim)
        # remove dims from any ignores_dims here.
        #  (Descendants' ignores_dims were already excluded by their loading_dims())
        for dim in self.obj.ignores_dims:
            if dim in result:
                result.remove(dim)
        # remove dims from any reduces_dims anywhere in the whole tree.
        for node in self.flat(include_self=True):
            for dim in node.obj.reduces_dims:
                if dim in result:
                    result.remove(dim)
        # return result
        return result

    def result_dims(self):
        '''return a list of all the dims the result would have, as implied by this tree.

        This is the set of quantity.dims for all quantities in this tree (self and all descendants), but:
            - if quantity.ignores_dims is non-empty, exclude those dims for that node and all its descendants.
            - if quantity.reduces_dims is non-empty, exclude those dims for that node and all its descendants,
                (but not from the whole tree. See self.loading_dims() to exclude those from the whole tree.)
        '''
        # maintain dims order by using a list instead of a set. (Not worried about speed here.)
        # dims from here
        dims = self.obj.dims
        if dims is None:
            result = []
        else:
            result = list(dims)  # copy of dims, as a list.
        # dims from children
        for child in self.children:
            child_dims = child.result_dims()
            for dim in child_dims:
                if dim not in result:
                    result.append(dim)
        # remove dims from any ignores_dims or reduces_dims here.
        #  (Descendants' ignores_dims and reduces_dims were already excluded by their result_dims().)
        for dim in [*self.obj.ignores_dims, *self.obj.reduces_dims]:
            if dim in result:
                result.remove(dim)
        # return result
        return result

    def flat_branches_until_vars(self, *, include_self=False):
        '''iterator over self and all descendants, but no descendants of MatchedVar nodes.'''
        return self.flat_branches_until(lambda node: isinstance(node.obj, MatchedVar), include_self=include_self)
