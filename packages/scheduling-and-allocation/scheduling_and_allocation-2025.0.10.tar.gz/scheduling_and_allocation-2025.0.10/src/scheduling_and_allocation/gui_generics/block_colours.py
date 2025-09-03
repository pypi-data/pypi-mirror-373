from ..Utilities import Colour
from ..model import ResourceType, ConflictType

# ==============================================================================================================
# some colours
# ==============================================================================================================
LIME_GREEN = "#ccffcc"
SKY_BLUE = "#b3e6ff"
TEAL = Colour.add(SKY_BLUE, LIME_GREEN)
IMMOVABLE_COLOUR: str = "#dddddd"

RESOURCE_COLOURS: dict[ResourceType, str] = {
    ResourceType.lab: "#cdefab",
    ResourceType.teacher: "#abcdef",
    ResourceType.stream: TEAL
}

# ==============================================================================================================
# return a list of colours with names, defining what colours go with what conflict types
# ==============================================================================================================
def get_conflict_colour_info(resource_type:ResourceType) -> list [dict[str, str]]:
    """
    :param resource_type: teacher/lab/stream
    :return: a list of dictionaries: bg = background colour, fg = foreground colour, text = conflict type
    """

    conflict_colour_info = []
    conflict_types = [ConflictType.TIME, ConflictType.LUNCH,
              ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY]

    match resource_type:
        case ResourceType.teacher:
            conflict_types.insert(0, ConflictType.TIME_TEACHER)
        case ResourceType.stream:
            conflict_types.insert(0, ConflictType.TIME_STREAM)
        case ResourceType.lab:
            conflict_types.insert(0, ConflictType.TIME_LAB)

    for c in conflict_types:
        bg = ConflictType.colours()[c]
        fg = "white"
        if Colour.is_light(bg):
            fg = "black"
        text = c.name
        conflict_colour_info.append({
            "bg": Colour.string(bg),
            "fg": Colour.string(fg),
            "text": text
        })
    return conflict_colour_info

