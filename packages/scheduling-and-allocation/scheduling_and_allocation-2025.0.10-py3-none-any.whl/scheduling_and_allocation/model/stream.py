from __future__ import annotations
from .enums import ResourceType

# ============================================================================
# Stream
# ============================================================================
class Stream:
    """ Describes a group of students whose classes cannot overlap. """

    # -------------------------------------------------------------------------
    # CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self, number: str = "A", description: str = ""):
        """
        Creates an instance of the Stream class
        :param number: defines the stream number
        :param description:  defines the stream title
        """
        self._number = number
        self.description = description
        self.resource_type = ResourceType.stream

    # -------------------------------------------------------------------------
    # unique identifier
    # -------------------------------------------------------------------------
    @property
    def number(self) -> str:
        return self._number

    # -------------------------------------------------------------------------
    # conversion to string
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        return self.number + " " + self.description

    def __repl__(self) -> str:
        return str(self)

    # -------------------------------------------------------------------------
    # for sorting
    # -------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)
