import json
import logging
from collections import namedtuple
from enum import Enum
from uuid import UUID

from teklia_toolbox.requests import download_file

logger = logging.getLogger(__name__)

BoundingBox = namedtuple("BoundingBox", ["x", "y", "width", "height"])


class Ordering(Enum):
    Position = "position"
    Name = "name"


MANUAL_SOURCE = "manual"


def uuid_or_manual(value: str | None) -> str | None:
    if not value:
        return None

    try:
        UUID(value)
    except (TypeError, ValueError):
        if value != MANUAL_SOURCE:
            raise ValueError(
                f"You must provide either a valid UUID or the string '{MANUAL_SOURCE}'."
            )

    return value


def parse_polygon(polygon):
    # getting polygon coordinates
    x_coords, y_coords = zip(*json.loads(polygon))

    # determining line box dimensions
    min_x, min_y = min(x_coords), min(y_coords)
    max_x, max_y = max(x_coords), max(y_coords)
    width, height = max_x - min_x, max_y - min_y
    return min_x, max_x, min_y, max_y, width, height


def bounding_box(polygon, offset_x=0, offset_y=0) -> BoundingBox | None:
    """
    Gets the coordinates of the a polygon and sets the coordinates of the lower
    left point at which box starts, third value is the width of the box, the last
    one is the height,
    the y axis is switched in arkindex coordinates, starting from top left corner
    to the bottom whereas for reportlab the y axis starts from bottom left corner
    to the top,
    implies reportlab first point corresponds to arkindex (min_x,max_y)
    """

    min_x, _, _, max_y, width, height = parse_polygon(polygon)
    return BoundingBox(min_x - offset_x, max_y - offset_y, width, height)


def bounding_box_arkindex(polygon) -> BoundingBox | None:
    """
    Get a bounding box with (min_x, min_y, width, height)
    """
    min_x, _, min_y, _, width, height = parse_polygon(polygon)
    return BoundingBox(min_x, min_y, width, height)


def image_download(image_url: str, image_name: str, temp_dir: str) -> str:
    """
    Gets an url and download the requested image in a temporary directory
    """

    image_path = temp_dir / f"{image_name}.jpg"
    # case where image_path already exists
    if image_path.is_file():
        return image_path

    flavoured_url = image_url + "/full/full/0/default.jpg"
    logger.info(f"downloading {flavoured_url} and saving image at {image_path}")
    download_file(flavoured_url, image_path)

    return image_path
