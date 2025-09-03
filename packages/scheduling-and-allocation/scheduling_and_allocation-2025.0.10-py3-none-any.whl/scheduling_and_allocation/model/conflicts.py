"""
Provides classes for managing scheduling conflicts
"""
from __future__ import annotations
import itertools
from typing import TYPE_CHECKING
from .enums import ConflictType

if TYPE_CHECKING:
    from .block import Block



# =============================================================================
# Constants
# =============================================================================
LUNCH_START: float = 11
LUNCH_END: float = 14
MAX_HOURS_PER_WEEK = 32.5


# -----------------------------------------------------------------------------------------------------------------
# set lunch break conflicts on a per day basis
# -----------------------------------------------------------------------------------------------------------------
def set_lunch_break_conflicts(blocks: tuple[Block, ...]):
    """
    Is there a lunch break for a teacher on each day
    :param blocks:
    :return: A list of conflicts
    """

   # collect blocks by day
    blocks_by_day = itertools.groupby(
        sorted(blocks, key=lambda b: b.day), lambda b: b.day)

    for _, blocks_group in blocks_by_day:

        daily_blocks: tuple[Block,...] = tuple(blocks_group)
        conflict = ConflictType.LUNCH if has_lunch_break_conflict(daily_blocks) else ConflictType.NONE

        # if no lunch on this day, create a conflict obj and mark blocks as conflicted_number
        if conflict == ConflictType.LUNCH:

            # find blocks that are the culprit
            for b in daily_blocks:
                if LUNCH_START <= b.start <= LUNCH_END:
                    _mark_block_conflict(ConflictType.LUNCH, (b,))
                if LUNCH_START <= b.end <= LUNCH_END:
                    _mark_block_conflict(ConflictType.LUNCH, (b,))
                if b.start <= LUNCH_START and b.end >= LUNCH_END:
                    _mark_block_conflict(ConflictType.LUNCH, (b,))


# -----------------------------------------------------------------------------------------------------------------
# are there any days within the given blocks where there is no lunch break
# -----------------------------------------------------------------------------------------------------------------
def has_lunch_break_conflict(blocks: tuple[Block, ...]) -> bool:
    """
    For this teacher, are there ANY days which do not have a lunch break?
    :param blocks:
    :return: yes or no (bool)
    """
    all_days_lunch = True

    # collect blocks by day
    blocks_by_day = itertools.groupby(
        sorted(blocks, key=lambda b: b.day), lambda b: b.day)

    for _, blocks_group in blocks_by_day:
        lunch_time = False
        blocks: list[Block] = list(blocks_group)
        blocks.sort(key=lambda b: b.start)

        # verify the 1st and last block
        b1: Block = blocks[0]
        b2: Block = blocks[-1]
        if b1.start - LUNCH_START > 0.49:
            continue
        if LUNCH_END - b2.end > 0.49:
            continue

        # look for a 1/2 window in-between blocks
        for b1, b2 in itertools.pairwise(blocks):

            # break between block
            start_break = max(b1.end, LUNCH_START)
            end_break = min(b2.start, LUNCH_END)
            if end_break > start_break and end_break - start_break > 0.49:
                lunch_time = True
                break

        all_days_lunch = all_days_lunch and lunch_time

    # if no lunch on this day, create a conflict obj and mark blocks as conflicted_number
    return not all_days_lunch


# -----------------------------------------------------------------------------------------------------------------
# are blocks overlapping in time/stream/lab/teacher
# -----------------------------------------------------------------------------------------------------------------
def set_block_conflicts(blocks_for_week: tuple[Block, ...],
                        conflict_type: ConflictType):
    """
    calculate if any two blocks overlap each other in time, and then
    assigns the conflict to the blocks
    :param blocks_for_week: a list of blocks to check for time overlap
    :param conflict_type: existing conflict type
    """
    blocks_by_day = itertools.groupby(
        sorted(blocks_for_week, key=lambda a: a.day), lambda a: a.day)

    for _, blocks in blocks_by_day:
        pairs: itertools.combinations[tuple[Block, Block]] = itertools.combinations(blocks, 2)
        for b1, b2 in pairs:
            if b1.conflicts_time(b2):
                _mark_block_conflict(ConflictType.TIME, (b1, b2))
                _mark_block_conflict(conflict_type, (b1, b2))


# -----------------------------------------------------------------------------------------------------------------
# are blocks overlapping in time/stream/lab/teacher
# -----------------------------------------------------------------------------------------------------------------
def block_conflicts_time(blocks_for_week: tuple[Block, ...]) -> ConflictType:
    """
    calculate if any two blocks overlap each other in time
    :param blocks_for_week: a list of blocks to check for time overlap
    :return: conflict_type
    """
    blocks_by_day = itertools.groupby(
        sorted(blocks_for_week, key=lambda a: a.day), lambda a: a.day)

    conflict = ConflictType.NONE
    for _, blocks in blocks_by_day:
        pairs: itertools.combinations[tuple[Block, Block]] = itertools.combinations(blocks, 2)
        for b1, b2 in pairs:
            if b1.conflicts_time(b2):
                conflict = conflict.TIME
    return conflict

# -----------------------------------------------------------------------------------------------------------------
# not enough days per week for a teacher
# -----------------------------------------------------------------------------------------------------------------
def set_number_of_days_conflict(blocks: tuple[Block, ...]):
    if has_number_of_days_conflict(blocks):
        _mark_block_conflict(ConflictType.MINIMUM_DAYS, blocks)

def has_number_of_days_conflict(blocks: tuple[Block, ...]) -> bool:
    """ collect blocks by day"""
    blocks_by_day = itertools.groupby(sorted(
        blocks, key=lambda a: a.day), lambda a: a.day)

    # if < 4 days, create a conflict and mark the blocks as conflicted_number
    if len(tuple(blocks_by_day)) < 4:
        return True
    return False


# -----------------------------------------------------------------------------------------------------------------
# too many hours for a week availability for a teacher
# -----------------------------------------------------------------------------------------------------------------
def set_availability_hours_conflict(blocks_for_teacher: tuple[Block, ...]):
    if has_availability_hours_conflict(blocks_for_teacher):
        _mark_block_conflict(ConflictType.AVAILABILITY, tuple(blocks_for_teacher))

def has_availability_hours_conflict(blocks: tuple[Block, ...]) -> bool:
    # collect blocks by day
    blocks_by_day = itertools.groupby(
        sorted(blocks, key=lambda a: a.day), lambda a: a.day)

    # if they have more than 32 hours worth of classes
    availability = 0
    for _, blocks_iter in blocks_by_day:
        blocks = list(blocks_iter)
        day_start = min(map(lambda b1: b1.start, blocks))
        day_end = max(map(lambda b1: b1.end, blocks))
        if day_end <= day_start:
            continue
        availability += day_end - day_start - 0.5

    # if over limit, create conflict
    if availability > MAX_HOURS_PER_WEEK:
        return True
    return False



def _mark_block_conflict(conflict_type: ConflictType, conflict_blocks: tuple[Block, ...]):
    for cb in conflict_blocks:
        cb.conflict = cb.conflict | conflict_type


# -----------------------------------------------------------------------------------------------------------------
# colors
# -----------------------------------------------------------------------------------------------------------------
def colours() -> dict[ConflictType, str]:
    """ Returns the colors used by each conflict resource_type """
    return ConflictType.colours()
