from __future__ import annotations
from .time_slot import TimeSlot
from .enums import ResourceType


# =====================================================================================================================
# Lab (or resource
# =====================================================================================================================
class Lab:

    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, room_number: str = "P100", description: str = ''):
        """Creates and returns a new Lab object."""
        self._number = room_number
        self.description = description
        self._unavailable: list[TimeSlot] = list()
        self.resource_type = ResourceType.lab

    # -----------------------------------------------------------------------------------------------------------------
    # index
    # -----------------------------------------------------------------------------------------------------------------
    @property
    def number(self):
        """Returns lab number"""
        return self._number

    # -----------------------------------------------------------------------------------------------------------------
    # add_unavailable_slot
    # -----------------------------------------------------------------------------------------------------------------
    def add_unavailable_slot(self, slot: TimeSlot) -> TimeSlot:
        """Adds an existing time slot to this lab's unavailable times."""
        self._unavailable.append(slot)
        return slot

    # -----------------------------------------------------------------------------------------------------------------
    # remove_unavailable_slot
    # -----------------------------------------------------------------------------------------------------------------
    def remove_unavailable_slot(self, slot: TimeSlot):
        """Remove the unavailable time slot from this lab."""
        if slot in self._unavailable:
            self._unavailable.remove(slot)

    # -----------------------------------------------------------------------------------------------------------------
    # unavailable
    # -----------------------------------------------------------------------------------------------------------------
    def unavailable_slots(self) -> tuple[TimeSlot, ...]:
        """Returns all immutable list of unavailable time slot objects for this lab."""
        return tuple(set(self._unavailable))

    # -----------------------------------------------------------------------------------------------------------------
    # __str__
    # -----------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns a text string that describes the Lab."""
        if not self.description:
            return f"{self.number}"
        return f"{self.number}: {self.description}"

    def __repr__(self) -> str:
        return str(self)

    # -----------------------------------------------------------------------------------------------------------------
    # for sorting
    # -----------------------------------------------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)


