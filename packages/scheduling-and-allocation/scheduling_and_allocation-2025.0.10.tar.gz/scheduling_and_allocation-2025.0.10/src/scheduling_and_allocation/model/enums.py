"""Enums for global use"""
from __future__ import annotations
from enum import Enum, Flag
from typing import TYPE_CHECKING

''' Not all the classes are enums, but this file contains data that is needed throughout the
program'''


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def validate(cls, user_input):
        # want to allow user to enter a value,  but also want to
        # allow it to be an enum, for interface reasons (forces the user to pass
        # the correct resource_type)
        if isinstance(user_input, cls):
            return user_input
        elif user_input in cls.names():
            return cls[user_input]
        elif user_input not in cls.values():
            raise ValueError(f"Error: input <{user_input}> is invalid")
        return user_input


class WeekDay(Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6

    def __lt__(self, other):
        return self.value < other.value

    @staticmethod
    def get_from_string(value) -> WeekDay:
        value = value[0:3].lower()
        return {"mon": WeekDay.Monday,
                "tue": WeekDay.Tuesday,
                "wed": WeekDay.Wednesday,
                "thu": WeekDay.Thursday,
                "fri": WeekDay.Friday,
                "sat": WeekDay.Saturday,
                "sun": WeekDay.Sunday}.get(value, None)


class SemesterType(ExtendedEnum):
    fall = 1
    winter = 2
    summer = 3
    any = 4



class ResourceType(ExtendedEnum):
    lab = "Lab"
    teacher = "Teacher"
    stream = "Stream"
    none = "None"

# =============================================================================
# ConflictType Enum
# =============================================================================
class ConflictType(Flag):
    """All types of Conflict types... note it is not an ENUM, but a FLAG
    which allows `or` and `len`, and `__contains__` built in"""
    NONE = 0
    TIME = 1
    LUNCH = 2
    MINIMUM_DAYS = 4
    AVAILABILITY = 8
    TIME_TEACHER = 16
    TIME_LAB = 32
    TIME_STREAM = 64

    @classmethod
    def colours(cls):
        """return a dictionary of colours to go with each conflict type"""
        return {
            cls.TIME: "indianred3",
            cls.LUNCH: "tan4",
            cls.MINIMUM_DAYS: "lightgoldenrod1",
            cls.AVAILABILITY: "mediumvioletred",
            cls.TIME_TEACHER: "red2",
            cls.TIME_LAB: "red2",
            cls.TIME_STREAM: "red2",
        }

    @classmethod
    def descriptions(cls) -> dict[ConflictType, str]:
        """returns a dictionary of descriptions to go with each conflict type"""
        return {
            cls.NONE: "no conflict",
            cls.TIME: "indirect time overlap",
            cls.LUNCH: "no lunch time",
            cls.MINIMUM_DAYS: "too few days",
            cls.TIME_TEACHER: "time overlap",
            cls.TIME_LAB: "time overlap",
            cls.TIME_STREAM: "time overlap",
            cls.AVAILABILITY: "not available",
        }

    def description(self) -> str:
        """ Returns the title of the provided conflict resource_type """
        return ConflictType.descriptions()[self]

    def is_conflicted(self) -> bool:
        """any conflicts?"""
        return len(self) != 0

    def is_time(self) -> bool:
        """does the conflict number include a time conflict?"""
        return ConflictType.TIME in self

    def is_time_lab(self) -> bool:
        """does the conflict number include a time - lab conflict?"""
        return ConflictType.TIME_LAB in self

    def is_time_teacher(self) -> bool:
        """does the conflict number include a time - teacher conflict?"""
        return ConflictType.TIME_TEACHER in self

    def is_time_stream(self) -> bool:
        """does the conflict number include a time - stream conflict?"""
        return ConflictType.TIME_STREAM in self

    def is_time_lunch(self) -> bool:
        """does the conflict number include a lunch conflict?"""
        return ConflictType.LUNCH in self

    def is_minimum_days(self) -> bool:
        """does the conflict number include a minimum days conflict?"""
        return ConflictType.MINIMUM_DAYS in self

    def is_availability(self) -> bool:
        """does the conflict number include a minimum days conflict?"""
        return ConflictType.AVAILABILITY in self

    def most_severe(self, view_type: ResourceType = ResourceType.none) -> ConflictType:
        """
        Identify the most severe conflict resource_type in a list of conflicts defined by
        the conflict number
        :param view_type: -> defines the user's current view. ResourceType (enum)
        """
        severest = ConflictType.NONE
        sorted_conflicts: list[ConflictType] = ORDER_OF_SEVERITY.copy()

        # based on the view, get_by_id the string version of the enum ConflictType
        if view_type is not None:
            conflict_key: str = f"time_{view_type.name}".upper()

            # if conflict key is a valid enum for ConflictType, insert this into
            # the sorted conflicts list
            if conflict_key in ConflictType.__members__:
                sorted_conflicts.insert(0, ConflictType[conflict_key])

        # look for the first match where the bit in conflict_number matches a possible
        # conflict resource_type
        for conflict in sorted_conflicts:
            if conflict in self:
                severest = conflict
                break

        # it doesn't make sense for labs or streams to have LUNCH, AVAILABILITY, or MINIMUM_DAYS
        # as valid conflicts
        if view_type == ResourceType.lab or view_type == ResourceType.stream:
            if severest == ConflictType.LUNCH or severest == ConflictType.AVAILABILITY or severest == ConflictType.MINIMUM_DAYS:
                severest = ConflictType.NONE


        return severest

ORDER_OF_SEVERITY = [ConflictType.TIME, ConflictType.LUNCH, ConflictType.MINIMUM_DAYS,
                     ConflictType.AVAILABILITY]

