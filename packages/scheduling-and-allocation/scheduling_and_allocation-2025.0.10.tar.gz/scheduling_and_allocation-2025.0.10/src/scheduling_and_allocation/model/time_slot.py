""" SYNOPSIS/EXAMPLE:
    tbd
"""

from __future__ import annotations
from .enums import WeekDay

MINUTE_BLOCK_SIZE = 30
MINIMUM_DURATION = 0.5
DEFAULT_DAY = WeekDay.Monday
DEFAULT_START = 8.0
DEFAULT_HOURS = 8
DEFAULT_DURATION = 1.5
MIN_START_TIME = 8
MAX_END_TIME = 18
MAXIMUM_DURATION = 8

def get_hour_minutes_from_hours(hours: float) -> (int, int):
    """converts number of hours (as a float) to integer hour and integer minutes"""
    hour = int(hours)
    minute = (hours % 1) * 60
    return hour, int(minute)

def get_clock_string_from_hours(hours: float)->str:
    hour,minute = get_hour_minutes_from_hours(hours)
    return f"{hour}:{minute:02d}"

# ============================================================================
# TimeSlot
# ============================================================================
class TimeSlot:
    """
    A time slot is specified by a day of the week, time_start time, length (in hours), and whether
        it is allowed to move.
    """

    # ------------------------------------------------------------------------
    # constructor
    # ------------------------------------------------------------------------
    def __init__(self, day: WeekDay | float = DEFAULT_DAY ,
                 start: float = DEFAULT_START,
                 duration: float = DEFAULT_DURATION,
                 movable: bool = True):
        """
        :param day: Day of the week expressed as a string or as a Weekday
        :param start: Start time using the 24hr clock (i.e., 1PM is "13:00")
        :param duration: How long this class lasts, in hours.
        :param movable: Whether this time_slot can be moved or not.
        """
        if isinstance(day, float) or isinstance(day, int):
            day = WeekDay(round(day))
        self.day: WeekDay = day
        self.start: float = start
        self.duration: float = min(max(duration, MINIMUM_DURATION), MAXIMUM_DURATION)
        self.movable: bool = movable

    # ------------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------------
    @property
    def end(self) -> float:
        return self.start + self.duration

    # ------------------------------------------------------------------------
    # snap_to_time
    # ------------------------------------------------------------------------
    def snap_to_time(self):

        # it's not movable!
        if not self.movable:
            return

        hour_fraction = int(60/MINUTE_BLOCK_SIZE)

        # duration needs to be snapped to the same time span
        duration = max(MINIMUM_DURATION, round(self.duration * hour_fraction) / hour_fraction)
        self.duration = duration

        # snap to the number of minutes in the block size
        start = max(self.start, MIN_START_TIME)
        if start + duration > MAX_END_TIME:
            start = MAX_END_TIME - duration
        hour, minute = get_hour_minutes_from_hours(start)
        minute = round(minute / MINUTE_BLOCK_SIZE) * MINUTE_BLOCK_SIZE

        # update scheduled_time
        self.start = hour + minute/60


    # ------------------------------------------------------------------------
    # snap_to_day
    # ------------------------------------------------------------------------
    def snap_to_day(self, fractional_day: float,
                    min_day: WeekDay = WeekDay.Monday,
                    max_day: WeekDay = WeekDay.Friday) -> bool:
        """
        :param fractional_day: an FLOAT that indicates where the day should be
        :param min_day: first day of the workweek
        :param max_day: last day of the workweek
        :return: True if modifications were made
        """
        day = round(fractional_day)
        day = max(min(day, max_day.value), min_day.value)
        if self.day.value == day:
            return False
        self.day = WeekDay(day)
        return True

    # ------------------------------------------------------------------------
    # conflicts
    # ------------------------------------------------------------------------
    def conflicts_time(self, other: TimeSlot, delta: float = 0.05) -> bool:
        """
        Tests if the current Time_Slot conflicts with another TimeSlot.
        :param other: other timeslot
        :param delta: the amount of leeway that we are allowing for in floating pt arithmetic
        """

        # detect date collisions.
        if self.day != other.day:
            return False

        # Calculate the time_start/end for each blocks within error factor.
        self_start = self.start + delta
        self_end = self.start + self.duration - delta
        other_start = other.start + delta
        other_end = other.start + other.duration - delta

        conflict1 = other_start < self_start < other_end or other_start < self_end < other_end
        conflict2 = self_start >= other_start and self_end <= other_end
        conflict3 = other_start >= self_start and other_end <= self_end
        return conflict1 or conflict2 or conflict3

    # ------------------------------------------------------------------------
    # sorting, string representation, etc
    # ------------------------------------------------------------------------
    def __eq__(self, other):
        return (self.day == other.day
                and self.start == other.start
                and self.duration == other.duration)

    def __lt__(self, other):
        return ((self.day, self.start, self.duration) <
                (other.day, other.start, other.duration))

    def __str__(self):
        return (f"{self.day.name}: {get_clock_string_from_hours(self.start)} "
                f"({self.duration} hrs)")

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
