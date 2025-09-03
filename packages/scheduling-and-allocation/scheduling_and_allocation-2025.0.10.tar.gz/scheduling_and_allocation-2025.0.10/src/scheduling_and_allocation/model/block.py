"""
Define a class time for teaching
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional
from ..Utilities.id_generator import IdGenerator
from .enums import WeekDay, ConflictType
from .time_slot import TimeSlot
OptionalId = Optional[int]

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .lab import Lab
    from .teacher import Teacher
    from .section import Section
    from .stream import Stream

DEFAULT_DAY = WeekDay.Monday
DEFAULT_START = 8.0
DEFAULT_DURATION = 1.5

# =====================================================================================================================
# Block - Class time
# =====================================================================================================================
class Block:
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # Class Variables
    block_ids = IdGenerator()

    # -----------------------------------------------------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, section: Section,
                 day: WeekDay | float = DEFAULT_DAY,
                 start: float = DEFAULT_START,
                 duration: float = DEFAULT_DURATION,
                 movable: bool = True,
                 block_id: OptionalId = None) -> None:
        """
        Creates a new block object (class time)
        :param section: a block must be part of a course/section
        :param day:
        :param start: when does the class start (float)
        :param duration: how long does the class last
        :param movable: can the time/day of this class be moved
        :param block_id:
        """
        self._sync: list[Block] = []
        self.section = section
        self._time_slot = TimeSlot(day, start, duration, movable)

        self._teachers: set[Teacher] = set()
        self._labs: set[Lab] = set()
        self.conflict = ConflictType.NONE
        self._block_id = Block.block_ids.get_new_id(block_id)

    # -----------------------------------------------------------------------------------------------------------------
    # generic properites
    # -----------------------------------------------------------------------------------------------------------------
    @property
    def id(self):
        """block id"""
        return self._block_id

    @property
    def number(self):
        """block id"""
        return str(self._block_id)

    def description(self) -> str:
        """Returns text string that describes this Block."""
        return str(self._time_slot)

    # -----------------------------------------------------------------------------------------------------------------
    # time slot properties and functions
    # -----------------------------------------------------------------------------------------------------------------
    @property
    def start(self) -> float:
        return self._time_slot.start

    @start.setter
    def start(self, value: float):
        self._time_slot.start = value

    @property
    def day(self) -> WeekDay:
        return self._time_slot.day

    @day.setter
    def day(self, value: WeekDay|float):
        if isinstance(value,int) or isinstance(value,float):
            self._time_slot.day = WeekDay(int(value))
        else:
            self._time_slot.day = value

    @property
    def end(self):
        return self._time_slot.end

    @property
    def duration(self)->float:
        return self._time_slot.duration

    @duration.setter
    def duration(self, value: float):
        self._time_slot.duration = value

    @property
    def movable(self)->bool:
        return self._time_slot.movable

    @movable.setter
    def movable(self, value: bool):
        self._time_slot.movable = value

    def snap_to_time(self):
        self._time_slot.snap_to_time()

    def snap_to_day(self, fractional_day: float) -> bool:
        return self._time_slot.snap_to_day(fractional_day)

    def conflicts_time(self, other: Block) -> bool:
        """
        Tests if the current Block conflicts with another TimeSlot.
        :param other: other Block
        """
        return self._time_slot.conflicts_time(other._time_slot)

    # -----------------------------------------------------------------------------------------------------------------
    # Conflicts
    # -----------------------------------------------------------------------------------------------------------------
    def add_conflict(self, conflict: ConflictType):
        """add a conflict to any pre-existing conflict"""
        self.conflict |= conflict

    def clear_conflicts(self):
        """remove any and all conflicts"""
        self.conflict = ConflictType.NONE

    # -----------------------------------------------------------------------------------------------------------------
    # All about streams
    # -----------------------------------------------------------------------------------------------------------------
    def streams(self) -> tuple[Stream, ...]:
        """Returns an immutable list of the assigned to the section that this block is part of."""
        return self.section.streams()

    # -----------------------------------------------------------------------------------------------------------------
    # All about labs
    # -----------------------------------------------------------------------------------------------------------------
    def labs(self) -> tuple[Lab, ...]:
        """Returns an immutable list of the labs assigned to this block."""
        return tuple(sorted(self._labs))

    def add_lab(self, lab: Lab):
        """Assign a new lab, to this block"""
        self._labs.add(lab)

    def remove_lab(self, lab: Lab):
        """Removes the specified Lab from this Block."""
        self._labs.discard(lab)

    def remove_all_labs(self):
        """Removes ALL Labs from this Block."""
        self._labs.clear()

    def has_lab(self, lab: Lab) -> bool:
        """Returns true if the Block has the specified Lab."""
        return lab in self._labs

    # -----------------------------------------------------------------------------------------------------------------
    # All about Teachers
    # -----------------------------------------------------------------------------------------------------------------
    def teachers(self) -> tuple[Teacher, ...]:
        """Returns an immutable list of the teachers assigned to this block."""
        return tuple(sorted(self._teachers))

    def add_teacher(self, teacher: Teacher):
        """Assign a new teacher, to this block"""
        self._teachers.add(teacher)

    def remove_teacher(self, teacher: Teacher):
        """Removes the specified teacher from this Block."""
        self._teachers.discard(teacher)

    def remove_all_teachers(self):
        """Removes ALL Teachers from this Block."""
        self._teachers.clear()

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the Block has the specified Lab."""
        return teacher in self._teachers

    # -----------------------------------------------------------------------------------------------------------------
    # All about syncing
    # -----------------------------------------------------------------------------------------------------------------
    def synced_blocks(self) -> tuple[Block, ...]:
        """Returns a tuple of the Blocks which are synced_blocks to this Block."""
        return tuple(self._sync)

    def sync_block(self, block: Block):
        """The new Block object will be synced_blocks with this one
        (i.e., changing the time_start time of this Block will change the time_start time of the
        synced_blocks block)."""
        self._sync.append(block)
        block._time_slot = self._time_slot
        for b in self._sync:
            b._sync.append(self)

    def unsync_block(self, block: Block):
        """Removes syncing of Block from this Block."""

        for b in self._sync:
            if self in b._sync:
                b._sync.remove(self)
        if block in self._sync:
            self._sync.remove(block)
            block._time_slot = copy.copy(block._time_slot)

    # -----------------------------------------------------------------------------------------------------------------
    # string representation of object
    # -----------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns a text string that describes the Block."""
        text = ""
        text += f"{self._time_slot} "
        text += ", ".join(str(lab.number) for lab in self.labs())
        text += f" for {self.section.title}"

        return text

    def __repr__(self) -> str:
        return f"{self.id} - {self.description()}"

    # -----------------------------------------------------------------------------------------------------------------
    # sorting properties
    # -----------------------------------------------------------------------------------------------------------------
    def __lt__(self,other):
        return self._time_slot < other._time_slot

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self._block_id)


