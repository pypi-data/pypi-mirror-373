
from __future__ import annotations
import re
from typing import TYPE_CHECKING, Optional
from ..Utilities.id_generator import IdGenerator
from . import WeekDay
from .block import Block, DEFAULT_DURATION, DEFAULT_START, DEFAULT_DAY
from .model_exceptions import InvalidHoursForSectionError

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .teacher import Teacher
    from .lab import Lab
    from .stream import Stream
    from .course import Course

DEFAULT_HOURS = 3

section_ids = IdGenerator()


def _validate_hours(hours: float) -> float:
    if hours <= 0:
        raise InvalidHoursForSectionError(f"{hours}: hours must be larger than 0")
    return hours


# ============================================================================
# Section
# ============================================================================
class Section:
    """
    Describes a section (part of a course)
    """
    section_ids = IdGenerator()

    # -------------------------------------------------------------------------
    # CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self, course: Course, number: str = "", name: str = "",
                 section_id: Optional[int] = None):
        """
        Creates an instance of the Section class.
        :param number: The section's number.
        :param name:
        """

        self._streams: set[Stream] = set()
        self._allocation: dict[Teacher:float] = dict()
        self._blocks: set[Block] = set()

        self.name = name
        self.number = number
        self.num_students: int = 0
        self.course = course

        self._section_id = Section.section_ids.get_new_id(section_id)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def hours(self) -> float:
        """
        How many hours does the course have or how many hours does the blocks add up to?
        """
        if self.blocks():
            return sum((b.duration for b in self.blocks()))
        return self.course.hours_per_week

    @property
    def id(self) -> int:
        """ Gets the section's ID """
        return self._section_id

    @property
    def title(self) -> str:
        """ Gets name if defined, otherwise 'Section num' """
        return self.name if self.name else f"Section {self.number}"

    # -------------------------------------------------------------------------
    # conflicts
    # -------------------------------------------------------------------------
    def is_conflicted(self) -> bool:
        """ Checks if there is a conflict with this section """
        return any(map(lambda block: block.conflict.is_conflicted(), self.blocks()))

    # -------------------------------------------------------------------------
    # blocks
    # -------------------------------------------------------------------------
    def blocks(self) -> tuple[Block, ...]:
        """ Gets list of section's blocks """
        return tuple(sorted(self._blocks))

    def remove_block(self, block: Block):
        """ Remove a block from this section """
        self._blocks.discard(block)

    def remove_all_blocks(self):
        for block in self.blocks():
            self.remove_block(block)

    def add_block(self, day: WeekDay | float = DEFAULT_DAY, start: float = DEFAULT_START,
                  duration: float = DEFAULT_DURATION, movable=True, block_id=None) -> Block:
        """ Creates and Assign a block to this section"""
        block = Block(self, day, start, duration, movable=movable, block_id=block_id)
        self._blocks.add(block)
        return block

    def get_block_by_id(self, block_id: int) -> Optional[Block]:
        """ Gets block with given ID from this section """
        blocks = [b for b in self._blocks if b.id == block_id]
        if len(blocks) > 0:
            return blocks[0]
        return None

    def has_block(self, block: Block) -> bool:
        """Does this section have this block? """
        return block in self._blocks

    # -------------------------------------------------------------------------
    # labs
    # -------------------------------------------------------------------------
    def labs(self) -> tuple[Lab, ...]:
        """ Gets all labs assigned to all blocks in this section """
        labs: set[Lab] = set()
        for b in self.blocks():
            labs.update(b.labs())
        return tuple(sorted(labs))

    def add_lab(self, lab: Lab):
        """ Assign a lab to every block in the section """
        for b in self.blocks():
            b.add_lab(lab)
        return self

    def has_lab(self, lab: Lab):
        """Is this lab attached to any of the labs in the blocks? """
        return lab in self.labs()

    def remove_lab(self, lab: Lab):
        """ Remove a lab from every block in the section """
        for b in self.blocks():
            b.remove_lab(lab)

    def remove_all_labs(self):
        """Remove all labs from every block in the section"""
        for lab in self.labs():
            for b in self.blocks():
                b.remove_lab(lab)

    # -------------------------------------------------------------------------
    # teachers (exclusively for scheduler program)
    # -------------------------------------------------------------------------
    def teachers(self) -> tuple[Teacher, ...]:
        """ Gets all teachers assigned to all blocks in this section and
        any teachers that were explicitly assigned to this section"""
        teachers = set()
        for b in self.blocks():
            teachers.update(b.teachers())
        return tuple(sorted(teachers))

    def add_teacher(self, teacher: Teacher):
        """ Assign a teacher to the section """
        for b in self.blocks():
            b.add_teacher(teacher)

    def remove_teacher(self, teacher: Teacher):
        """ Removes teacher from all blocks in this section """
        for b in self.blocks():
            b.remove_teacher(teacher)

    def remove_all_teachers(self):
        """ Removes all teachers from all blocks in this section """
        for t in self.teachers():
            self.remove_teacher(t)

    def has_teacher(self, teacher: Teacher) -> bool:
        """ Checks if section has teacher """
        answer = False
        for b in self.blocks():
            answer = answer or b.has_teacher(teacher)
        return answer

    # -------------------------------------------------------------------------
    # teacher allocation (used for allocation program)
    # -------------------------------------------------------------------------
    def section_defined_teachers(self) -> tuple[Teacher, ...]:
        """gets only teachers that were explicitly assigned to this section in allocation manager"""
        teachers = set()
        teachers.update(self._allocation.keys())
        return tuple(sorted(teachers))

    def remove_allocation(self, teacher):
        self.remove_teacher(teacher)
        if teacher in self._allocation.keys():
            _ = self._allocation.pop(teacher)

    def set_teacher_allocation(self, teacher: Teacher, hours: float):
        """Assign number of hours to teacher for this section. Set hours to 0 to remove
        teacher from this section

        As best as can be done, add teacher to blocks to match the allocation,
        ... if it cannot be done, then set the allocation hours to the given hours
        """
        # clear before resetting
        self.remove_allocation(teacher)

        # don't do anything more if set to zero
        if hours == 0:
            return

        # add to all blocks
        if hours == self.hours and len(self.blocks()) != 0:
            self.add_teacher(teacher)
            return

        # if number of hours is not equal to the total hours of the section,
        # try to find blocks to assign the teacher to
        possible_paths = []
        blocks = self.blocks()
        self._find_block_fit_for_allocation(hours, blocks, "", possible_paths)

        if len(possible_paths) != 0:
            flag = False
            for pp in possible_paths:
                if all(len(b.teachers()) == 0 for tf, b in zip(pp, blocks) if tf == "T"):
                    for block in (b for tf, b in zip(pp, blocks) if tf == "T"):
                        block.add_teacher(teacher)
                    flag = True
                    break
            if not flag:
                for block in (b for tf, b in zip(possible_paths[0], blocks) if tf == "T"):
                    block.add_teacher(teacher)
        else:
            self._allocation[teacher] = hours

    def _find_block_fit_for_allocation(self, hours, blocks, path="", possible_paths=None):
        possible_paths = [] if possible_paths is None else possible_paths
        if hours == 0:
            possible_paths.append(path)
            return
        if len(blocks) == 0:
            return

        block, *blocks = blocks
        if hours >= block.duration:
            new_path = path + "T"
            self._find_block_fit_for_allocation(hours - block.duration, blocks, new_path, possible_paths)

        if hours <= sum((b.duration for b in blocks)):
            new_path = path + "F"
            self._find_block_fit_for_allocation(hours, blocks, new_path, possible_paths)

    def has_allocated_teacher(self, teacher):
        return self.has_teacher(teacher) or teacher in self._allocation.keys()

    def get_teacher_allocation(self, teacher: Teacher) -> float:
        """ Get the number of hours assigned to this teacher for this section """

        # teacher not teaching this section
        if not self.has_teacher(teacher) and teacher not in self._allocation.keys():
            return 0

        # allocation defined
        allocation = self._allocation.get(teacher, 0)

        if len(self.blocks()) != 0:
            allocation += sum((b.duration for b in self.blocks() if teacher in b.teachers()))
        return allocation

    # -------------------------------------------------------------------------
    # streams
    # -------------------------------------------------------------------------
    def streams(self) -> tuple[Stream, ...]:
        """ Gets all streams in this section """
        return tuple(sorted(self._streams))

    def add_stream(self, stream: Stream):
        """ Assign streams to this section. """
        self._streams.add(stream)

    def remove_stream(self, stream: Stream):
        """ Remove stream from this section. """
        self._streams.discard(stream)

    def has_stream(self, stream: Stream) -> bool:
        """Check if a section has a stream """
        return stream in self._streams

    def remove_all_streams(self):
        """ Removes all streams from this section """
        self._streams.clear()

    # -------------------------------------------------------------------------
    # clear everything from the stream
    # -------------------------------------------------------------------------
    def clear(self):
        self.remove_all_teachers()
        self.remove_all_streams()
        self.remove_all_labs()
        self.remove_all_blocks()

    # -------------------------------------------------------------------------
    # string representation
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string that describes the section """
        if self.name and not re.match(r"Section\s*\d*$", self.name):
            return f"Section {self.number}: {self.name}"
        else:
            return f"Section {self.number}"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        try:
            a = int(self.number) < int(other.number)
            return a
        except ValueError:
            return self.number < other.number

    def __hash__(self):
        return hash(self._section_id)

    def __eq__(self, other):
        return self.id == other.number
