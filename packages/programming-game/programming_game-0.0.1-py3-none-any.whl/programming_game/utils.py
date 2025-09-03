import math
import re
from functools import lru_cache

from .schema.other import Position


def get_distance(pos1: Position, pos2: Position) -> float:
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


def check_position_is_equal(
    pos1: dict[str, float], pos2: dict[str, float], tolerance: float = 0.01
) -> bool:
    """Checks if two positions are equal within a tolerance."""
    return (
        abs(pos1["x"] - pos2["x"]) <= tolerance
        and abs(pos1["y"] - pos2["y"]) <= tolerance
    )


@lru_cache
def to_snake_case(name: str) -> str:
    """
    Converts a string from CamelCase, PascalCase, etc., to snake_case.

    Handles acronyms and other complex cases.
    """
    # 1. Insert an underscore before any uppercase letter that is preceded by a lowercase letter or digit.
    #    e.g., "myHTTPRequest" -> "my_HTTP_Request"
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)

    # 2. Insert an underscore before any uppercase letter that is followed by a lowercase letter.
    #    This handles the start of words and acronyms.
    #    e.g., "HTTPRequest" -> "HTTP_Request"
    name = re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", name)

    return name.lower()
