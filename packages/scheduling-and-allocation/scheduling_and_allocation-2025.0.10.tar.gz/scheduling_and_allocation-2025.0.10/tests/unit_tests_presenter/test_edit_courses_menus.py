from typing import Any, Optional

import pytest

from src.scheduling_and_allocation.gui_pages import EditCoursesTk
from src.scheduling_and_allocation.model import Schedule, SemesterType, WeekDay
from src.scheduling_and_allocation.presenter.edit_courses import EditCourses


class EditCoursesTkTest(EditCoursesTk):
        # ========================================================================
        # constructor
        # ========================================================================
        def __init__(self, frame):
            self.structure = dict()
            self.called_clear_tree_text = False
            self.called_update_tree_text_arguments = []
            self.called_update_tree_text = False
            self.called_remove_tree_item_children = False
            self.called_remove_tree_item_children_arguments = []
            self.called_remove_tree_item = False
            self.called_remove_tree_item_arguments = []
            self.called_add_tree_item = False
            self.called_add_tree_item_arguments = []
            self.called_update_resource_type = False
            self.called_update_resource_type_arguments = []
            self.called_clear_tree = False
            self.frame = frame

        def get_new_id(self, parent_id):
            # find all current ids with this parent, and then add 1
            kid_ids = [iid for iid in self.structure.keys() if
                       iid.startswith(parent_id) and len(parent_id) < len(iid) < len(parent_id) + 5]
            id_numbers = [int(iid[-3:]) for iid in kid_ids]

            if len(id_numbers) == 0:
                id_numbers = [0]
            new_id_number = max(id_numbers) + 1

            return f"{parent_id}.{new_id_number:03d}"

        def update_resource_type_objects(self, resource_type, objs):
            self.called_update_resource_type = True
            self.called_update_resource_type_arguments.append ([resource_type])

        def add_tree_item(self, parent_id: str, name: str, child: Any, hide: bool = True):
            self.called_add_tree_item = True
            self.called_add_tree_item_arguments.append( [parent_id, name, child, hide])
            iid = self.get_new_id(parent_id)
            self.structure[iid] = name
            return iid

        def remove_tree_item(self, tree_iid: str):
            self.called_remove_tree_item = True
            self.called_remove_tree_item_arguments.append( [tree_iid])
            if tree_iid in self.structure.keys():
                self.structure.pop(tree_iid)
            else:
                raise ValueError(f"could not remove {tree_iid} from tree because it doesn't exist")

        def remove_tree_item_children(self, tree_iid: str):
            self.called_remove_tree_item_children = True
            self.called_remove_tree_item_children_arguments.append([tree_iid])

            ids = list(self.structure.keys())
            for this_iid in ids:
                if this_iid.startswith(tree_iid) and len(this_iid) > len(tree_iid):
                    self.structure.pop(this_iid)


        def update_tree_text(self, tree_iid: str, text: str):
            self.called_update_tree_text = True
            self.called_update_tree_text_arguments.append([tree_iid, text])
            if tree_iid in self.structure.keys():
                self.structure[tree_iid] = text

        def get_iid_from_name(self, name) -> str:
            for iid, s_name in self.structure.items():
                if name == s_name:
                    return iid
            return ""

        def clear_tree(self):
            self.called_clear_tree_text = True
            self.structure.clear()

        def get_parent(self, tree_id):
            return tree_id[0:-4]

        def get_iid_from_name_with_parent_id(self, name, parent_id) -> str:
            for iid, s_name in self.structure.items():
                s_name = s_name.replace("teacher: ","")
                s_name = s_name.replace("lab: ","")
                if name == s_name and iid.startswith(parent_id):
                    return iid
            return ""



@pytest.fixture()
def valid_tree_structure():
    return {'.001': '001 BasketWeaving',
        '.001.001': 'Section 1  (1A calculus available)',
        '.001.001.001': 'Class Time: Monday: 8:00 (1.5 hrs)',
        '.001.001.001.001': 'teacher: Jane Doe',
        '.001.001.001.002': 'lab: P107: C-Lab',
        '.001.001.002': 'Class Time: Monday: 10:00 (1.5 hrs)',
        '.001.001.002.001': 'teacher: Jane Doe',
        '.001.001.002.002': 'lab: P107: C-Lab',
        '.001.002': 'Section 2  (1B no calculus)',
        '.001.002.001': 'Class Time: Tuesday: 8:00 (1.5 hrs)',
        '.001.002.001.002': 'lab: P322: Mac Lab',
        '.001.002.001.001': 'teacher: John Doe',
        '.001.002.002': 'Class Time: Tuesday: 10:00 (1.5 hrs)',
        '.001.002.002.002': 'lab: P325',
        '.001.002.002.001': 'teacher: Babe Ruth',
        '.002': '002 Thumb Twiddling',
        '.002.001': 'Section 1',
        '.002.001.001': 'Class Time: Monday: 8:00 (1.5 hrs)',
        '.002.001.002': 'Class Time: Monday: 10:00 (1.5 hrs)',
        '.002.002': 'Section 2',
        '.002.002.001': 'Class Time: Tuesday: 8:00 (1.5 hrs)',
        '.002.002.002': 'Class Time: Tuesday: 10:00 (1.5 hrs)'}


@pytest.fixture()
def schedule_obj():
    schedule = Schedule()

    # teachers
    t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
    t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
    t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
    t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id = "4")

    # labs
    l1 = schedule.add_update_lab("P107", "C-Lab")
    l2 = schedule.add_update_lab("P322", "Mac Lab")
    l3 = schedule.add_update_lab("P325")
    l4 = schedule.add_update_lab("BH311", "Britain Hall")

    # streams
    st1 = schedule.add_update_stream("1A", "calculus available")
    st2 = schedule.add_update_stream("1B", "no calculus")
    st3 = schedule.add_update_stream("2A")
    st4 = schedule.add_update_stream("2B")

    # courses
    c_001 = schedule.add_update_course("001","BasketWeaving", SemesterType.fall )
    s_001_1 = c_001.add_section("1", section_id=1)
    s_001_1.add_stream(st1)
    b_001_1_1 = s_001_1.add_block(WeekDay.Monday, 8 )
    b_001_1_2 = s_001_1.add_block(WeekDay.Monday,  10 )
    b_001_1_1.add_teacher(t1)
    b_001_1_2.add_teacher(t1)
    b_001_1_1.add_lab(l1)
    b_001_1_2.add_lab(l1)

    s_001_2 = c_001.add_section("2",section_id=2)
    s_001_2.add_stream(st2)
    b_001_2_1 = s_001_2.add_block(WeekDay.Tuesday,  8 )
    b_001_2_2 = s_001_2.add_block(WeekDay.Tuesday,  10 )
    b_001_2_1.add_teacher(t2)
    b_001_2_2.add_teacher(t3)
    b_001_2_1.add_lab(l2)
    b_001_2_2.add_lab(l3)


    c_002 = schedule.add_update_course("002","Thumb Twiddling", SemesterType.fall )
    s_002_1 = c_002.add_section("1",)
    b_002_1_1 = s_002_1.add_block(WeekDay.Monday,  8 )
    b_002_1_2 = s_002_1.add_block(WeekDay.Monday,  10 )
    s_002_2 = c_002.add_section("2",)
    b_002_2_1 = s_002_2.add_block(WeekDay.Tuesday,  8 )
    b_002_2_2 = s_002_2.add_block(WeekDay.Tuesday,  10 )



    return schedule

@pytest.fixture()
def gui():
    return EditCoursesTkTest(None)

dirty_flag = False


@pytest.fixture()
def dirty():
    global dirty_flag
    dirty_flag = False

    def set_dirty(value: Optional[bool] = None) -> bool:
        global dirty_flag
        if value is not None:
            dirty_flag = value
        return dirty_flag

    return set_dirty

# =============================================================================
# Tree created properly
# =============================================================================
def test_init_edit_course(gui, dirty, schedule_obj):
    """can initialize an instance of EditCourses"""

    # execute
    ec = EditCourses(dirty, None, schedule_obj, gui)

    # verify
    assert ec is not None
    assert isinstance(ec, EditCourses)

def test_refresh_updates_tree(gui, dirty, schedule_obj, valid_tree_structure):
    """can create a pop-up menu for course and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)

    # execute
    ec.refresh()

    # verify
    for key in valid_tree_structure.keys():
        assert key in gui.structure
        assert gui.structure[key] == valid_tree_structure[key]



# =============================================================================
# Tests for LAB/TEACHER menu
# =============================================================================
def test_create_tree_menu_for_teacher(gui, dirty, schedule_obj):
    """can create a pop-up menu for teacher and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    teacher = block.teachers()[0]
    tree_id = ".001.001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(teacher, block, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Remove Teacher']) == 1

def test_create_tree_menu_for_teacher_remove_teacher(gui, dirty, schedule_obj):
    """remove teacher from parent"""
    # NOTE: teachers method returns sorted teachers by first name,
    # so  Babe Ruth comes before Jane Doe

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    block.add_teacher(schedule_obj.get_teacher_by_name("Babe","Ruth"))
    teacher = block.teachers()[0]
    ec.refresh()
    parent_id = ".001.001.001"
    tree_id = gui.get_iid_from_name_with_parent_id(f"{teacher.firstname} {teacher.lastname}", parent_id)


    menu = ec.tree_event_create_tree_popup(teacher, block, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Teacher'][0]

    # execute
    num_teachers = len(block.teachers())
    mi.command()

    # verify
    assert len(block.teachers()) == num_teachers - 1
    x=block.teachers()
    for iid in [iid for iid in gui.structure.keys() if iid.startswith(parent_id)]:
        assert not gui.structure[iid].startswith('teacher: Babe Ruth')
    assert gui.get_iid_from_name_with_parent_id("Jane Doe", parent_id)


# =============================================================================
# Tests for LAB/TEACHER menu
# =============================================================================
def test_create_tree_menu_for_lab(gui, dirty, schedule_obj):
    """can create a pop-up menu for lab and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    lab = block.labs()[0]
    tree_id = ".001.001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(lab, block, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Remove Lab']) == 1

def test_create_tree_menu_for_lab_remove_lab(gui, dirty, schedule_obj, valid_tree_structure):
    """remove lab from parent"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    ec.refresh()
    block.add_lab(schedule_obj.get_lab_by_number("P325"))
    lab = block.labs()[0]
    tree_id = gui.get_iid_from_name_with_parent_id(lab.number, ".001.001.001")
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(lab, block, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Lab'][0]


    # execute
    num_labs = len(block.labs())
    mi.command()

    # verify
    assert len(block.labs()) == num_labs - 1
    for iid in [iid for iid in gui.structure.keys() if iid.startswith(parent_id)]:
        assert not gui.structure[iid].startswith(lab.number)



# =============================================================================
# Tests for BLOCK menu
# =============================================================================

def test_create_tree_menu_for_block(gui, dirty, schedule_obj):
    """can create a pop-up menu for block and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Remove Class Time']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove All']) == 1


def test_tree_menu_for_section_remove_block(gui, dirty, schedule_obj):
    """run menu command for block: remove
    - dirty flag is set
    - tree is cleared of block
    - schedule has been updated
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Class Time'][0]
    assert gui.get_iid_from_name_with_parent_id("Class Time: Monday: 8:00 (1.5 hrs)", parent_id)

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert len(section.blocks()) == 1
    assert not gui.get_iid_from_name_with_parent_id("Class Time: Monday: 8:00 (1.5 hrs)", parent_id)

def test_tree_menu_for_block_add_teacher_sub_menu(gui, dirty, schedule_obj):
    """run menu command for block: add teachers
    - sub menu only contains teachers not already assigned to block
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Add Teacher'][0]
    assert len(mi.children) == 3
    assert mi.children[0].label == "Babe Ruth"
    assert mi.children[1].label == "Bugs Bunny"
    assert mi.children[2].label == "John Doe"

def test_tree_menu_for_block_add_teacher(gui, dirty, schedule_obj):
    """run menu command for block: add teachers - select teacher
    - teacher added to block/schedule (but only to this block, not the other one)
    - teacher added to block/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    block2 = section.blocks()[1]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    add_menu = mi[0].children[1]        # Bugs Bunny

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert block.has_teacher(schedule_obj.get_teacher_by_name("Bugs", "Bunny"))
    assert not block2.has_teacher(schedule_obj.get_teacher_by_name("Bugs", "Bunny"))
    assert gui.get_iid_from_name_with_parent_id("Bugs Bunny", tree_id)
    new_iid = gui.get_iid_from_name_with_parent_id("Bugs Bunny", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + teacher_id"
    assert not gui.get_iid_from_name_with_parent_id("John Doe", ".001.001.002")


def test_tree_menu_for_block_add_lab_sub_menu(gui, dirty, schedule_obj):
    """run menu command for block: add labs
    - sub menu only contains labs not already assigned to block
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Lab"]

    assert len(mi[0].children) == 3
    assert mi[0].children[0].label == "BH311: Britain Hall"
    assert mi[0].children[1].label == "P322: Mac Lab"
    assert mi[0].children[2].label == "P325"

def test_tree_menu_for_block_add_lab(gui, dirty, schedule_obj):
    """run menu command for block: add lab - select lab
    - lab added to section/schedule
    - lab added to section/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Lab"]
    add_menu = mi[0].children[0]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert section.has_lab(schedule_obj.get_lab_by_number("BH311"))
    assert gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", tree_id)
    new_iid = gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + teacher_id"
    assert not gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", ".001.001.002")


def test_tree_menu_for_block_remove_all_sub_menu(gui, dirty, schedule_obj):
    """create remove_all sub menu
    - sub menu for sections, streams, labs, and teachers"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children
    assert len(sub_menu) == 2
    assert sub_menu[0].label == "labs"
    assert sub_menu[1].label == "teachers"


def test_tree_menu_for_blocks_remove_all_labs(gui, dirty, schedule_obj):
    """run menu command for block: remove_all labs
    - dirty flag is set
    - all labs, etc have been removed from block/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'labs'][0]
    mi2.command()

    assert dirty_flag
    assert len(block.labs()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(tree_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("P107")
        assert not gui.structure[iid].startswith("P322")
        assert not gui.structure[iid].startswith("P325")


def test_tree_menu_for_block_remove_all_teachers(gui, dirty, schedule_obj):
    """run menu command for section: remove_all teacher
    - dirty flag is set
    - all teachers, etc have been removed from block/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    block = section.blocks()[0]
    tree_id = ".001.001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(block, section, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'teachers'][0]
    mi2.command()

    assert dirty_flag
    assert len(block.teachers()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(tree_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("Jane Doe")
        assert not gui.structure[iid].startswith("John Doe")
        assert not gui.structure[iid].startswith("Babe Ruth")
        assert not gui.structure[iid].startswith("Bugs Bunny")


# =============================================================================
# Tests for SECTION menu
# =============================================================================


def test_create_tree_menu_for_section(gui, dirty, schedule_obj):
    """can create a pop-up menu for section and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Edit Section']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Section']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Class Times']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Stream']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Stream']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove All']) == 1

def test_tree_menu_for_section_edit_section(gui, dirty, schedule_obj):
    """click edit section
    - EditCourses.edit_section_dialog must be called"""

    called_edit_dialog = False
    def edit_dialog_test(section, tree_id):
        nonlocal called_edit_dialog
        called_edit_dialog = True


    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    ec.edit_section_dialog = edit_dialog_test
    mi = [mi for mi in menu if mi.label == 'Edit Section'][0]

    # execute
    mi.command()

    # verify
    assert called_edit_dialog

def test_tree_menu_for_section_remove_section(gui, dirty, schedule_obj):
    """run menu command for section: remove
    - dirty flag is set
    - tree is cleared of section
    - schedule has been updated
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Section'][0]
    assert gui.get_iid_from_name_with_parent_id("Section 1  (1A calculus available)", ".001")

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert len(course.sections()) == 1
    assert not gui.get_iid_from_name_with_parent_id("Section 1  (1A calculus available)", ".001")

def test_tree_menu_for_section_add_blocks(gui, dirty, schedule_obj):
    """click section/add blocks
    - EditCourses.add_blocks_dialog must be called"""

    called_add_dialog = False
    def add_dialog_test(course, tree_id):
        nonlocal called_add_dialog
        called_add_dialog = True


    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    ec.add_blocks_dialog = add_dialog_test
    mi = [mi for mi in menu if mi.label == 'Add Class Times'][0]

    # execute
    mi.command()

    # verify
    assert called_add_dialog

def test_tree_menu_for_section_add_teacher_sub_menu(gui, dirty, schedule_obj):
    """run menu command for section: add teachers
    - sub menu only contains teachers not already assigned to section
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Add Teacher'][0]
    assert len(mi.children) == 3
    assert mi.children[0].label == "Babe Ruth"
    assert mi.children[1].label == "Bugs Bunny"
    assert mi.children[2].label == "John Doe"

def test_tree_menu_for_section_add_teacher(gui, dirty, schedule_obj):
    """run menu command for section: add teachers - select teacher
    - teacher added to section/schedule
    - teacher added to section/tree in correct spot
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    add_menu = mi[0].children[1]        # Bugs Bunny

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert section.has_teacher(schedule_obj.get_teacher_by_name("Bugs", "Bunny"))
    assert gui.get_iid_from_name_with_parent_id("Bugs Bunny", tree_id)
    new_iid = gui.get_iid_from_name_with_parent_id("Bugs Bunny", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + teacher_id"


def test_tree_menu_for_section_add_stream_sub_menu(gui, dirty, schedule_obj):
    """run menu command for section: add streams
    - sub menu only contains streams not already assigned to section
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    assert len(mi[0].children) == 3
    assert mi[0].children[0].label == "1B no calculus"
    assert mi[0].children[1].label == "2A "
    assert mi[0].children[2].label == "2B "

def test_tree_menu_for_section_add_stream(gui, dirty, schedule_obj):
    """run menu command for section: add stream - select stream
    - stream added to section/schedule
    - stream added to section/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    add_menu = mi[0].children[1]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert section.has_stream(schedule_obj.get_stream_by_number("2A"))

def test_tree_menu_for_section_add_lab_sub_menu(gui, dirty, schedule_obj):
    """run menu command for section: add labs
    - sub menu only contains labs not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Lab"]

    assert len(mi[0].children) == 3
    assert mi[0].children[0].label == "BH311: Britain Hall"
    assert mi[0].children[1].label == "P322: Mac Lab"
    assert mi[0].children[2].label == "P325"

def test_tree_menu_for_section_add_lab(gui, dirty, schedule_obj):
    """run menu command for section: add lab - select lab
    - lab added to section/schedule
    - lab added to section/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Lab"]
    add_menu = mi[0].children[0]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert section.has_lab(schedule_obj.get_lab_by_number("BH311"))
    assert gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", tree_id)

    new_iid = gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + lab_id"

def test_tree_menu_for_section_remove_all_sub_menu(gui, dirty, schedule_obj):
    """create remove_all sub menu
    - sub menu for sections, streams, labs, and teachers"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children
    assert len(sub_menu) == 4
    assert sub_menu[0].label == "class times"
    assert sub_menu[1].label == "streams"
    assert sub_menu[2].label == "labs"
    assert sub_menu[3].label == "teachers"


def test_tree_menu_for_section_remove_all_blocks(gui, dirty, schedule_obj):
    """run menu command for section: remove_all block
    - dirty flag is set
    - all blocks, etc have been removed from section/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'class times'][0]
    mi2.command()

    assert dirty_flag
    assert len(section.blocks()) == 0
    assert ".001.001.001" not in gui.structure.keys()
    assert ".001.001.002" not in gui.structure.keys()

def test_tree_menu_for_section_remove_all_streams(gui, dirty, schedule_obj):
    """run menu command for section: remove_all streams
    - dirty flag is set
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'streams'][0]
    mi2.command()

    assert dirty_flag
    assert len(section.streams()) == 0

def test_tree_menu_for_section_remove_all_labs(gui, dirty, schedule_obj):
    """run menu command for section: remove_all section
    - dirty flag is set
    - all labs, etc have been removed from section/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'labs'][0]
    mi2.command()

    assert dirty_flag
    assert len(section.labs()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(tree_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("P107")
        assert not gui.structure[iid].startswith("P322")
        assert not gui.structure[iid].startswith("P325")


def test_tree_menu_for_section_remove_all_teachers(gui, dirty, schedule_obj):
    """run menu command for section: remove_all teacher
    - dirty flag is set
    - all teachers, etc have been removed from section/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    course = schedule_obj.get_course_by_number("001")
    section = course.get_section_by_id(1)
    tree_id = ".001.001"
    parent_id = gui.get_parent(tree_id)
    menu = ec.tree_event_create_tree_popup(section, course, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'teachers'][0]
    mi2.command()

    assert dirty_flag
    assert len(section.teachers()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(tree_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("Jane Doe")
        assert not gui.structure[iid].startswith("John Doe")
        assert not gui.structure[iid].startswith("Babe Ruth")
        assert not gui.structure[iid].startswith("Bugs Bunny")

# =============================================================================
# Tests for COURSE menu
# =============================================================================
def test_create_tree_menu_for_course(gui, dirty, schedule_obj):
    """can create a pop-up menu for course and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Edit Course']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Course']) == 1
    assert len([mi for mi in menu if 'needs allocation' in mi.label]) == 1
    assert len([mi for mi in menu if mi.label == 'Add Sections']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Stream']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove All']) == 1

def test_tree_menu_for_course_edit_course(gui, dirty, schedule_obj):
    """click edit course
    - EditCourses.edit_course_dialog must be called"""

    called_edit_dialog = False
    def edit_course_dialog_test(course, tree_id):
        nonlocal called_edit_dialog
        called_edit_dialog = True


    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, "001", "")
    ec.edit_course_dialog = edit_course_dialog_test
    mi = [mi for mi in menu if mi.label == 'Edit Course'][0]

    # execute
    mi.command()

    # verify
    assert called_edit_dialog

def test_tree_menu_for_course_remove_course(gui, dirty, schedule_obj):
    """run menu command for course: remove_course
    - dirty flag is set
    - tree is cleared of course
    - schedule has been update
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Course'][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001") is None
    assert schedule_obj.get_course_by_number("002") is not None
    assert gui.clear_tree
    assert not gui.get_iid_from_name("001 BasketWeaving")
    assert gui.get_iid_from_name("002 Thumb Twiddling")

def test_tree_menu_for_course_unset_needs_allocation(gui, dirty, schedule_obj):
    """run menu command for course: needs allocation
    - dirty flag is set
    - needs allocation is unset
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if "allocation" in mi.label and 'Unset' in mi.label][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert not schedule_obj.get_course_by_number("001").needs_allocation

def test_tree_menu_for_course_set_needs_allocation(gui, dirty, schedule_obj):
    """run menu command for course: needs allocation
    - dirty flag is set
    - needs allocation is unset
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    course = schedule_obj.get_course_by_number("001")
    course.needs_allocation = False
    assert not schedule_obj.get_course_by_number("001").needs_allocation

    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if "allocation" in mi.label and 'Set' in mi.label][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").needs_allocation

def test_tree_menu_for_course_add_sections(gui, dirty, schedule_obj):
    """click course/add sections
    - EditCourses.add_section_dialog must be called"""

    called_add_section_dialog = False
    def add_section_dialog_test(course, tree_id):
        nonlocal called_add_section_dialog
        called_add_section_dialog = True


    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, "001", "")
    ec.add_section_dialog = add_section_dialog_test
    mi = [mi for mi in menu if mi.label == 'Add Sections'][0]

    # execute
    mi.command()

    # verify
    assert called_add_section_dialog

def test_tree_menu_for_course_add_teacher_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add teachers
    - sub menu only contains teachers not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    schedule_obj.add_update_teacher("Mickey","Mouse")

    # execute
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    assert len(mi[0].children) == 2
    assert mi[0].children[0].label == "Bugs Bunny"
    assert mi[0].children[1].label == "Mickey Mouse"

def test_tree_menu_for_course_add_teacher(gui, dirty, schedule_obj):
    """run menu command for course: add teachers - select teacher
    - teacher added to course/schedule
    - teacher added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    schedule_obj.add_update_teacher("Mickey","Mouse")
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    add_menu = mi[0].children[1]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_teacher(schedule_obj.get_teacher_by_name("Mickey", "Mouse"))
    assert gui.get_iid_from_name_with_parent_id("Mickey Mouse", tree_id)
    new_iid = gui.get_iid_from_name_with_parent_id("Mickey Mouse", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + teacher_id"

def test_tree_menu_for_course_add_stream_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add streams
    - sub menu only contains streams not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    assert len(mi[0].children) == 2
    assert mi[0].children[0].label == "2A "
    assert mi[0].children[1].label == "2B "

def test_tree_menu_for_course_add_stream(gui, dirty, schedule_obj):
    """run menu command for course: add stream - select stream
    - stream added to course/schedule
    - stream added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    add_menu = mi[0].children[1]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_stream(schedule_obj.get_stream_by_number("2B"))

def test_tree_menu_for_course_add_lab_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add labs
    - sub menu only contains labs not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Lab"]

    assert len(mi[0].children) == 1
    assert mi[0].children[0].label == "BH311: Britain Hall"

def test_tree_menu_for_course_add_lab(gui, dirty, schedule_obj):
    """run menu command for course: add lab - select lab
    - lab added to course/schedule
    - lab added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Lab"]
    add_menu = mi[0].children[0]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_lab(schedule_obj.get_lab_by_number("BH311"))
    assert gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", parent_id)
    new_iid = gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", tree_id)
    assert len(new_iid) == 4*4, "course_id + section_id + block_id + lab_id"

def test_tree_menu_for_course_remove_all_sub_menu(gui, dirty, schedule_obj):
    """create remove_all sub menu
    - sub menu for sections, streams, labs, and teachers"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children
    assert len(sub_menu) == 4
    assert sub_menu[0].label == "sections"
    assert sub_menu[1].label == "streams"
    assert sub_menu[2].label == "labs"
    assert sub_menu[3].label == "teachers"


def test_tree_menu_for_course_remove_all_sections(gui, dirty, schedule_obj):
    """run menu command for course: remove_all section
    - dirty flag is set
    - all sections, etc have been removed from course/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'sections'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.sections()) == 0
    assert ".001.001" not in gui.structure.keys()
    assert ".001.002" not in gui.structure.keys()

def test_tree_menu_for_course_remove_all_streams(gui, dirty, schedule_obj):
    """run menu command for course: remove_all streams
    - dirty flag is set
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'streams'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.streams()) == 0

def test_tree_menu_for_course_remove_all_labs(gui, dirty, schedule_obj):
    """run menu command for course: remove_all lab
    - dirty flag is set
    - all labs, etc have been removed from course/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'labs'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.labs()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(parent_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("P107")
        assert not gui.structure[iid].startswith("P322")
        assert not gui.structure[iid].startswith("P325")

def test_tree_menu_for_course_remove_all_teachers(gui, dirty, schedule_obj):
    """run menu command for course: remove_all teacher
    - dirty flag is set
    - all teachers, etc have been removed from course/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.tree_event_create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'teachers'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.teachers()) == 0
    ids = [iid for iid in gui.structure.keys() if iid.startswith(tree_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("Jane Doe")
        assert not gui.structure[iid].startswith("John Doe")
        assert not gui.structure[iid].startswith("Babe Ruth")
        assert not gui.structure[iid].startswith("Bugs Bunny")



