from __future__ import annotations
from tkinter import *
from tkinter import ttk
from typing import *
global img_open, img_close, img_empty



class AdvancedTreeview(ttk.Treeview):
    """
    A subclass of ttk.TreeView object that will keep track of which object belongs with
    which Treeview item.

    see: https://docs.python.org/3/library/tkinter.ttk.html#treeview
    """

    def __init__(self, root: Frame, **kwargs):
        self._item_to_obj_dict = dict()
        super().__init__(root, **kwargs)

    def open_branch(self, tree_id: str):
        """Opens all the leafs in this branch"""
        self.item(tree_id, open=True)
        for leaf in self.get_children(tree_id):
            self.open_branch(leaf)

    #
    def insert(self, parent_id: str,
               any_object: Optional[Any],
               *,
               index: int | Literal['end'] = 'end', obj_id: str = None,
               **options) -> str:
        """
        override the ttk.treeview.insert command, adding 'any_object' as a new parameter

        Creates a new item and return the item identifier of the newly created item.

        see: https://docs.python.org/3/library/tkinter.ttk.html#treeview

        """

        obj_id = super().insert(parent_id, index, obj_id, **options)
        self._item_to_obj_dict[obj_id] = any_object
        return obj_id

    def insert_sorted(self, parent_id: str, any_object: Optional[Any], **options):
        """
        If the child objects support sorting, and if all siblings are of the
        same resource_type, then insert in sorted order, else put at end of siblings

        For allowed options, see: https://docs.python.org/3/library/tkinter.ttk.html#treeview
        """

        siblings = self.get_children(parent_id)

        sortable: bool = hasattr(any_object, "__lt__")

        # find index where to insert
        # NOTE: Assumes that 'get_children' returns items in row order
        options['index'] = 'end'
        if sortable:
            # use try except because maybe siblings cannot be compared to one another
            try:
                for index, kid_id in enumerate(siblings):
                    if any_object < self._item_to_obj_dict[kid_id]:
                        options['index'] = index
                        break
            except AttributeError:
                pass
            except TypeError:
                pass

        # insert
        return self.insert(parent_id, any_object=any_object, **options)

    def get_obj_from_id(self, obj_id: str) -> Optional[Any]:
        """Gets and returns the object associated with the tree item, unless 'obj_id' is
        not valid, in which case it returns None"""
        if obj_id in self._item_to_obj_dict.keys():
            return self._item_to_obj_dict[obj_id]
        else:
            return None

    def delete(self, *item_ids):
        """Delete all specified items and all their descendants. The root item may not be deleted."""

        # remove item, and all its descendants from the dictionary of objects
        for obj_id in item_ids:
            if self.exists(obj_id):
                self._prune(obj_id)
                super().delete(obj_id)

    def expand_whole_branch(self, tree_id: str):
        """Opens all the twigs in this branch"""
        self.item(tree_id, open=True)
        for twig in self.get_children(tree_id):
            self.expand_whole_branch(twig)


    def _prune(self, obj_id: str):
        """Not only remove the tree branch, but remove the data from tree_objects as well"""
        if self.exists(obj_id):

            for twig in self.get_children(obj_id):
                self._prune(twig)
            self._item_to_obj_dict.pop(obj_id, None)


"""
# =================================================================
# footer
# =================================================================

=head1 AUTHOR

Sandy Bultena

=head1 COPYRIGHT

Copyright (c) 2023 Sandy Bultena 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
"""
