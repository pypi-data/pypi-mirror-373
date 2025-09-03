from __future__ import annotations
from tkinter import *

from src.scheduling_and_allocation.modified_tk import AdvancedTreeview

mw = Tk()
mw.geometry("500x300")

frame = Frame(mw, bg='blue')
frame.pack(expand=1, fill="both")
tree = AdvancedTreeview(frame)
tree.pack(expand=1, fill='both')


def clear_tree():
    for kid in tree.get_children(""):
        tree.delete(kid)


def test_saving_objs():
    clear_tree()
    assert len(tree._item_to_obj_dict) == 0
    o1 = 'hello'
    o2 = 'goodbye'
    o3 = 'death to all'
    id1 = tree.insert("", any_object=o1, text=str(o1))
    id2 = tree.insert("", any_object=o2, text=str(o2))
    id3 = tree.insert("", any_object=o3, text=str(o3))
    id4 = tree.insert("", any_object=o1, text=str(o1))

    assert len(tree._item_to_obj_dict) == 4
    assert tree.get_obj_from_id(id1) == o1
    assert tree.get_obj_from_id(id2) == o2
    assert tree.get_obj_from_id(id3) == o3
    assert tree.get_obj_from_id(id4) == o1

    kids = tree.get_children("")
    assert kids[0] == id1
    assert kids[1] == id2
    assert kids[2] == id3
    assert kids[3] == id4

def test_deleting_items():
    clear_tree()
    assert len(tree._item_to_obj_dict) == 0
    o1 = 'hello'
    o2 = 'goodbye'
    o3 = 'death to all'
    id1 = tree.insert("", any_object=o1, text=str(o1))
    id2 = tree.insert("", any_object=o2, text=str(o2))
    id3 = tree.insert("", any_object=o3, text=str(o3))
    id4 = tree.insert("", any_object=o1, text=str(o1))

    assert len(tree._item_to_obj_dict) == 4

    tree.delete(id2, id3)
    assert len(tree._item_to_obj_dict) == 2
    assert tree.get_obj_from_id(id1) == o1
    assert tree.get_obj_from_id(id4) == o1


def test_insert_sorted():
    clear_tree()
    assert len(tree._item_to_obj_dict) == 0
    o1 = 'hello'
    o2 = 'goodbye'
    o3 = 'death to all'

    id2 = tree.insert_sorted("", any_object=o2, text=str(o2))
    id1 = tree.insert_sorted("", any_object=o1, text=str(o1))
    id3 = tree.insert_sorted("", any_object=o3, text=str(o3))
    assert len(tree._item_to_obj_dict) == 3

    kids = tree.get_children("")
    assert kids[0] == id3
    assert kids[1] == id2
    assert kids[2] == id1


def test_insert_sorted_but_not_sortable():
    clear_tree()
    assert len(tree._item_to_obj_dict) == 0
    o1 = UnSortableObject('hello')
    o2 = UnSortableObject('goodbye')
    o3 = UnSortableObject('death to all')

    id2 = tree.insert_sorted("", any_object=o2, text=str(o2))
    id1 = tree.insert_sorted("", any_object=o1, text=str(o1))
    id3 = tree.insert_sorted("", any_object=o3, text=str(o3))

    assert len(tree._item_to_obj_dict) == 3

    kids = tree.get_children("")
    assert kids[0] == id2
    assert kids[1] == id1
    assert kids[2] == id3


class UnSortableObject:
    def __init__(self, a: str):
        self.a = a
    def __str__(self):
        return self.a

class SortableObject:
    def __init__(self, a: str):
        self.a = a

    def __lt__(self, other: SortableObject):
        return self.a < other.a

    def __str__(self):
        return self.a

