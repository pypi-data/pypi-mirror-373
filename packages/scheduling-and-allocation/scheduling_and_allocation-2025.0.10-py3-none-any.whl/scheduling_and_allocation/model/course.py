from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .exceptions import InvalidSectionNumberForCourseError
from .enums import SemesterType
from .section import Section

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .block import Block
    from .teacher import Teacher
    from .stream import Stream
    from .lab import Lab

DEFAULT_HOURS: float = 3.0

OptionalId = Optional[int]


class Course:
    """Describes a distinct course."""

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
    def __init__(self, number: str = "",
                 name: str = "New Course",
                 semester: SemesterType = SemesterType.any,
                 hours_per_week: float = 3.0,
                 needs_allocation: bool = True):
        """Creates and returns a course object.
        :param number: Course number
        :param name: Course name
        :param semester: Which semester is it taught in
        :param needs_allocation: This requires someone to teach it
        :course_id: if not specified, will create one as required
        """

        self._number: str = number
        self.name: str = name
        self.needs_allocation: bool = needs_allocation
        self.hours_per_week = float(hours_per_week)
        self._sections: set[Section] = set()
        self.semester: SemesterType = semester

    # =================================================================
    # unique identifier
    # =================================================================
    @property
    def number(self) -> str:
        """Returns the unique ID for this Course object."""
        return self._number

    # =================================================================
    # title
    # =================================================================
    @property
    def title(self) -> str:
        """Returns text string that describes this Block."""
        return f"{self.number}: {self.name}"

    # =================================================================
    # sections
    # =================================================================
    def add_section(self, number: str = "",  name: str = "",
                    section_id: int = None) -> Section:
        """Assign a Section to this Course."""

        if number in (s.number for s in self.sections()):
            raise InvalidSectionNumberForCourseError(
                f"<{number}>: section number is not unique for this Course.")

        if number == "":
            max_number = 0
            for sec_number in (s.number for s in self.sections()):
                try:
                    max_number = max(int(sec_number), max_number)
                except ValueError:
                    pass
            number = str(max_number + 1)

        section = Section(self, number, name, section_id)
        self._sections.add(section)

        return section

    def get_section_by_number(self, number: str) -> Optional[Section]:
        """Gets the Section from this Course that has the passed section number, if it exists.
        Otherwise, returns None. """
        found = [section for section in self.sections() if section.number == number]
        return found[0] if found else None

    def get_section_by_id(self, sect_id: int) -> Optional[Section]:
        """Gets the Section from this Course that matches the passed section ID, if it exists.
        Returns the Section if found, or None otherwise."""
        found = [section for section in self.sections() if section.id == sect_id]
        return found[0] if found else None

    def get_sections_by_name(self, name: str) -> tuple[Section, ...]:
        """Gets the Section from this Course that has the passed section name, if it exists.
        Returns a list containing the Section if found, or an empty list otherwise."""
        found = (section for section in self.sections() if section.name == name)
        return tuple(found)

    def remove_section(self, section: Section):
        """Removes the passed Section from this Course, if it exists."""
        self._sections.discard(section)

    def sections(self) -> tuple[Section, ...]:
        """Returns a list of all the Sections assigned to this Course."""
        return tuple(sorted(self._sections))

    def number_of_sections(self) -> int:
        """Returns the number of Sections assigned to this Course."""
        return len(self.sections())

    def get_sections_for_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections():
            if teacher in section.teachers():
                sections.append(section)

        return tuple(sorted(set(sections)))

    def get_sections_for_allocated_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections():
            if section.has_allocated_teacher(teacher):
                sections.append(section)

        return tuple(sorted(set(sections)))

    def max_section_number(self) -> int:
        """Returns the maximum Section number from the Sections assigned to this Course."""
        sections = sorted(self.sections(), key=lambda s: s.number)
        return sections[-1].number if len(sections) > 0 else 0

    def remove_all_sections(self):
        """remove all sections in this course"""
        for section in self.sections():
            self.remove_section(section)

    # =================================================================
    # blocks
    # =================================================================
    def blocks(self) -> tuple[Block, ...]:
        """Returns a tuple of the Blocks assigned to this Course."""
        blocks = []
        for section in self.sections():
            blocks.extend(section.blocks())
        return tuple(sorted(set(blocks)))

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self) -> tuple[Teacher, ...]:
        """Returns a list of the Teachers assigned to all Sections of this Course."""

        teachers: list[Teacher] = list()
        for section in self.sections():
            teachers.extend(section.teachers())
        return tuple(sorted(set(teachers), key=lambda x: (x.lastname, x.firstname)))

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the passed Teacher is assigned to this Course."""
        return teacher in self.teachers()

    def has_allocated_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the passed Teacher is assigned to this Course."""
        if teacher in self.teachers():
            return True
        for section in self.sections():
            if section.has_allocated_teacher(teacher):
                return True
        return False

    def add_teacher(self, teacher: Teacher) -> Teacher:
        """Assigns a Teacher to all Sections of this Course."""

        for section in self.sections():
            section.add_teacher(teacher)
        return teacher

    def remove_teacher(self, teacher: Teacher):
        """Removes the passed Teacher from all Sections/Blocks in this Course."""
        for section in self.sections():
            section.remove_teacher(teacher)

    def remove_all_teachers(self):
        """Removes all Teachers from all Sections/Blocks in this Course."""
        for teacher in self.teachers():
            self.remove_teacher(teacher)


    # =================================================================
    # stream
    # =================================================================
    def streams(self) -> tuple[Stream, ...]:
        """Returns a list of Streams assigned to all Sections of this Course."""

        streams: list[Stream] = list()
        for section in self.sections():
            streams.extend(section.streams())
        return tuple(sorted(set(streams)))

    def has_stream(self, stream: Stream) -> bool:
        """Returns true if this Course has the specified Stream."""
        return stream in self.streams()

    def add_stream(self, stream: Stream) -> Stream:
        """Assigns a Stream to all Sections of this Course."""
        if stream:
            for section in self.sections():
                section.add_stream(stream)

        return stream

    def remove_stream(self, stream: Stream):
        """Removes the specified Stream from this Course."""
        for section in self.sections():
            section.remove_stream(stream)

    def remove_all_streams(self):
        """Removes all Streams from all Sections of this Course."""
        for stream in self.streams():
            self.remove_stream(stream)



    # =================================================================
    # labs
    # =================================================================
    def labs(self) -> tuple[Lab, ...]:
        """Returns a list of Labs assigned to all Sections of this Course."""

        lab_list: list[Lab] = []

        for section in self.sections():
            for block in section.blocks():
                lab_list.extend(block.labs())
        return tuple(sorted(set(lab_list)))

    def add_lab(self, lab: Lab) -> Lab:
        """Assigns a Lab to all Sections of this Course."""

        for section in self.sections():
            section.add_lab(lab)
        return lab

    def has_lab(self, lab: Lab):
        """Does this course have this lab in any of its sections/blocks?"""
        return lab in self.labs()

    def remove_lab(self, lab: Lab):
        for section in self.sections():
            section.remove_lab(lab)

    def remove_all_labs(self):
        for lab in self.labs():
            self.remove_lab(lab)

    # =================================================================
    # Get unused section number
    # =================================================================
    def get_new_number(self, number: int = 1) -> int:
        """Returns the first unused Section Number."""
        while self.get_section_by_number(str(number)):
            number += 1
        return number

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number

    def __hash__(self):
        return hash(self._number)

    def __eq__(self, other):
        return self.number == other.number

    # =================================================================
    # string representation of the object
    # =================================================================
    def __str__(self) -> str:
        """Returns a text string that describes the Course, its Sections, its Blocks,
        its Teachers, and its Labs. """
        text = ''

        # Header
        text += "\n\n"
        text += '=' * 50 + "\n"
        text += f"{self._number} {self.name}\n"
        text += '=' * 50 + "\n"

        # Sections
        for s in sorted(self.sections(), key=lambda x: x.number):
            text += f"\n{s}\n"
            text += "-" * 50 + "\n"

            # Blocks
            for b in sorted(s.blocks()):
                text += f"{b}\n"
                text += "\tlab_ids: " + ", ".join([str(lab) for lab in b.labs()]) + "\n"
                text += "\tteacher_ids: "
                text += ", ".join([str(t) for t in b.teachers()])
                text += "\n"

        return text

    def __repr__(self) -> str:
        return f"{self.title}  ({self.hours_per_week} hrs/wk)"

