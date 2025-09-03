from __future__ import annotations
from .enums import ResourceType


class Teacher:
    """Describes a teacher."""

    # -------------------------------------------------------------------
    # constructor
    # --------------------------------------------------------------------
    def __init__(self, firstname: str, lastname: str, department: str = "", release: float = 0):
        """Creates a Teacher object.
        :param firstname:   first name of the teacher
        :param lastname:   last name of the teacher
        :param release: how much release does the teacher have in fractions of FTE
        :param department:  department that this teacher is associated with
        """
        self.firstname = firstname
        self.lastname = lastname
        self.department = department
        self.release = release
        self.resource_type = ResourceType.teacher
        self._id = f"{self.lastname}_{self.firstname}"
        self._id = self._id.replace(" ", "_")

    # -------------------------------------------------------------------------
    # unique identifier
    # -------------------------------------------------------------------------
    @property
    def teacher_id(self) -> str:
        return self._id

    @property
    def number(self) -> str:
        """Returns the unique ID for this Teacher."""
        return self.teacher_id

    # -------------------------------------------------------------------------
    # other
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __repr__(self):
        return str(self)

    def __lt__(self, other: Teacher) -> bool:
        return (self.firstname, self.lastname) < (other.firstname, other.lastname)

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)
