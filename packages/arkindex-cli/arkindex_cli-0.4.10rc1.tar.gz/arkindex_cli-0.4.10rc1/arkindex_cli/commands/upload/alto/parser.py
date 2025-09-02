import json
import logging
from dataclasses import dataclass
from functools import cached_property
from itertools import chain, pairwise
from math import floor
from statistics import mean

from lxml import etree as ET

from arkindex_cli.commands.upload import db
from arkindex_cli.commands.upload.exceptions import UploadProcessingError

logger = logging.getLogger(__name__)


DEFAULT_CONFIDENCE = 1.0

# XPath to retrieve (grand) parent nodes of type `TextBlock`
XPATH_TEXTBLOCK_PARENT = './ancestor::*[local-name()="TextBlock"]'


def _is_alto_namespace(namespace: str) -> bool:
    return (
        namespace.startswith("http://www.loc.gov/standards/alto/")
        # Older URLs for ALTO≤2.0
        or namespace.startswith("http://schema.ccs-gmbh.com/docworks/")
    )


@dataclass
class AltoMetadata:
    target: str
    # Mapping of expected value of the ``target`` attribute => Arkindex metadata list
    metadata_list: dict

    def get_metadata_list(self, node: ET._Element) -> list[dict]:
        return chain.from_iterable(
            self.metadata_list.get(key, [])
            for key in node.attrib.get(self.target, "").split(" ")
        )


class AltoElement:
    def __init__(
        self,
        node: ET._Element,
        page_width: int | None = None,
        page_height: int | None = None,
        alto_namespace: str | None = None,
        unit: str = "pixel",
        dpi_x: int | None = None,
        dpi_y: int | None = None,
    ):
        if alto_namespace:
            self.namespaces = {"alto": alto_namespace}
        else:
            alto_namespaces = set(filter(_is_alto_namespace, node.nsmap.values()))

            if len(alto_namespaces) == 1:
                self.namespaces = {"alto": alto_namespaces.pop()}
            elif len(alto_namespaces) > 1:
                logger.error(f"Multiple ALTO namespaces found: {alto_namespaces}")
                raise UploadProcessingError
            else:
                logger.error("ALTO namespace not found")
                raise UploadProcessingError

        if (dpi_x is None) ^ (dpi_y is None):
            logger.error(
                "The horizontal and vertical resolutions must be both set or both unset."
            )
            raise UploadProcessingError
        if dpi_x and dpi_x <= 0:
            logger.error(
                "The horizontal resolution must be a strictly positive integer."
            )
            raise UploadProcessingError
        if dpi_y and dpi_y <= 0:
            logger.error("The vertical resolution must be a strictly positive integer.")
            raise UploadProcessingError

        if unit not in ("pixel", "mm10"):
            logger.error(f"Unsupported measurement unit {unit}")
            raise UploadProcessingError
        if unit == "mm10" and (dpi_x is None or dpi_y is None):
            logger.error(
                "The horizontal and vertical resolutions must be set to import ALTO elements using the mm10 unit."
            )
            raise UploadProcessingError

        self.node_name = ET.QName(node).localname.lower()
        self.strings = node.findall("{*}String", namespaces=self.namespaces)
        self.page_width = page_width or self.get_width(node)
        self.page_height = page_height or self.get_height(node)
        self.unit = unit
        self.dpi_x = dpi_x
        self.dpi_y = dpi_y
        # If there are more than one Page node in the file, the image id required
        # to build the IIIF url for the images is retrieved from the Page's
        # PHYSICAL_IMG_NR attribute and stored as page_image_id.
        self.page_image_id = self.get_page_image_id(node)
        self.content = node
        self.children = []

        # List of the metadata associated with the element
        self.metadata_list = [
            {"name": "Alto ID", "value": self.id, "type": "reference"}
        ]

        if lang := self.content.get("LANG"):
            self.metadata_list.append({"name": "Lang", "value": lang, "type": "text"})

    def xml_int_value(self, node, attr_name, default: int | None = None) -> int:
        value = node.get(attr_name)
        if value is None:
            if default is not None:
                return default
            logger.error(f"Missing required value: {attr_name}")
            raise UploadProcessingError

        # The ALTO specification accepts float coordinates, but Arkindex only supports integers
        return round(float(value))

    def get_polygon_coordinates(self, node) -> dict:
        if not ("WIDTH" in node.attrib and "HEIGHT" in node.attrib):
            return

        # Skip elements with polygons with w or h <= 0 (invalid polygons)
        width = self.xml_int_value(node, "WIDTH")
        height = self.xml_int_value(node, "HEIGHT")
        if width <= 0 or height <= 0:
            return

        # Special case for nodes when hpos and vpos are set, use full size
        return {
            "x": self.xml_int_value(node, "HPOS", 0),
            "y": self.xml_int_value(node, "VPOS", 0),
            "width": width,
            "height": height,
        }

    def get_width(self, node):
        if "WIDTH" not in node.attrib:
            return
        return self.xml_int_value(node, "WIDTH")

    def get_height(self, node):
        if "HEIGHT" not in node.attrib:
            return
        return self.xml_int_value(node, "HEIGHT")

    def get_page_image_id(self, node):
        if "PHYSICAL_IMG_NR" not in node.attrib:
            return
        return node.get("PHYSICAL_IMG_NR")

    def ark_polygon(self, dict: dict) -> list[int]:
        """
        A polygon compatible with Arkindex.
        """
        if not dict:
            return None

        x, y, width, height = dict["x"], dict["y"], dict["width"], dict["height"]

        polygon = [
            [x, y],
            [x, y + height],
            [x + width, y + height],
            [x + width, y],
            [x, y],
        ]

        page_width, page_height = self.page_width, self.page_height

        # When using tenths of millimeters, we convert the coordinates to pixels
        if self.unit == "mm10":
            polygon = [
                [round(x * self.dpi_x / 254), round(y * self.dpi_y / 254)]
                for x, y in polygon
            ]
            # Also convert the page width and height, which also is in tenths of millimeters,
            # so we can trim the pixels properly and never go beyond the edges of the image
            page_width = floor(page_width * self.dpi_x / 254)
            page_height = floor(page_height * self.dpi_y / 254)

        # We trim the polygon of the element in the case where its dimensions are bigger than the dimensions of the image
        polygon = [
            [min(page_width, max(0, x)), min(page_height, max(0, y))]
            for x, y in polygon
        ]

        # We check there are always at least 4 different points
        if len(set(map(tuple, polygon))) < 4:
            return

        return polygon

    @property
    def has_children(self):
        return len(list(self.content)) > 0

    @property
    def polygon(self) -> list[tuple[int, int]] | str | None:
        """
        Build a valid Arkindex polygon if this Alto Element has one.
        Return a list of coordinates by default. The list is stringified
        if we are using a database upload.
        """
        coords = self.get_polygon_coordinates(self.content)

        polygon = self.ark_polygon(coords)
        # Polygon is stored as string in the SQLite database
        if polygon and db.is_available():
            polygon = json.dumps(polygon)
        return polygon

    @property
    def width(self):
        return self.get_width(self.content)

    @property
    def height(self):
        return self.get_height(self.content)

    @property
    def name(self):
        return self.content.get("LABEL", self.id)

    @property
    def id(self):
        return self.content.get("ID")

    def parse_children(self):
        if not self.has_children:
            return
        for child in self.content:
            child_element = AltoElement(
                child,
                page_width=self.page_width,
                page_height=self.page_height,
                alto_namespace=self.namespaces["alto"],
                unit=self.unit,
                dpi_x=self.dpi_x,
                dpi_y=self.dpi_y,
            )
            # String nodes are not sent to Arkindex as Elements, but their "CONTENT"
            # is sent as the transcription for their parent node.
            if child_element.node_name != "string":
                self.children.append(child_element)
                child_element.parse_children()

    @cached_property
    def all_strings(self) -> list[ET._Element]:
        """
        Easy access to the recursive strings
        """
        if self.strings:
            return self.strings

        all_strings = []
        for child in self.children:
            all_strings.extend(child.all_strings)

        return all_strings

    @cached_property
    def text(self):
        """
        Easy access to the node's transcription
        """

        def get_hyphen(string: ET._Element | None) -> str | None:
            """
            Returns the contents of the following sibling, if it is a `HYP` node
            """
            if string is None:
                return

            next_node = string.getnext()
            if next_node is None or ET.QName(next_node).localname != "HYP":
                return

            return next_node.attrib.get("CONTENT")

        full_text, hyphen = "", None
        for previous_strings, string in pairwise([None, *self.all_strings]):
            # Add separator:
            # - a space if `String`s are part of the same `TextBlock`
            # - two line breaks otherwise
            if not hyphen and previous_strings is not None:
                parents = string.xpath(XPATH_TEXTBLOCK_PARENT)
                previous_parents = previous_strings.xpath(XPATH_TEXTBLOCK_PARENT)
                full_text += (
                    " "
                    if (
                        parents
                        and previous_parents
                        and parents.pop() == previous_parents.pop()
                    )
                    else "\n\n"
                )

            full_text += string.attrib["CONTENT"]

            # If we have a hyphen after the last `String`, we collapse the next one
            hyphen = get_hyphen(string)
            if (
                hyphen
                # Only remove hyphen if it's not the last `String`
                and (string != self.all_strings[-1])
                # Only remove hyphen if it's correct
                and full_text.endswith(hyphen)
            ):
                full_text = full_text[: -len(hyphen)]

        return full_text.strip()

    @cached_property
    def confidence(self) -> float:
        """
        Easy access to the node's confidence.
        """

        def is_float(value) -> bool:
            try:
                float(value)
            except (TypeError, ValueError):
                return False
            return True

        def get_all_confidences():
            # If the node contains `String` then average the confidences
            # of each `String`, weighted by their number of characters.
            if len(self.strings):
                return list(
                    chain.from_iterable(
                        [float(string.attrib["WC"])] * len(string.attrib["CONTENT"])
                        for string in self.strings
                        if is_float(string.attrib.get("WC"))
                    )
                )

            # Else average the confidences of each child, weighted by
            # their number of characters.
            return list(
                chain.from_iterable(
                    [child.confidence] * len(child.text) for child in self.children
                )
            )

        all_confidences = get_all_confidences()
        if not all_confidences:
            return DEFAULT_CONFIDENCE

        return round(mean(all_confidences), 2)


class RootAltoElement(AltoElement):
    def __init__(
        self,
        node: ET._Element,
        alto_namespace: str | None = None,
        dpi_x: int | None = None,
        dpi_y: int | None = None,
    ):
        super().__init__(node, alto_namespace=alto_namespace, dpi_x=dpi_x, dpi_y=dpi_y)

        # Retrieve the file's measurement unit, used to specify the image(s) and polygons
        # dimensions. We support tenths of millimeters only when the DPI are set, and pixels whenever.
        try:
            self.unit = node.find(
                "{*}Description/{*}MeasurementUnit", namespaces=self.namespaces
            ).text
        except AttributeError:
            logger.error("The MesurementUnit is missing.")
            raise UploadProcessingError

        try:
            # Retrieve the fileName node, which contains the identifier required to build the
            # IIIF url for the image (if there is only one Page node in the file.)
            self.filename = node.find(
                "{*}Description/{*}sourceImageInformation/{*}fileName",
                namespaces=self.namespaces,
            ).text
        except AttributeError:
            logger.error("The fileName node is missing.")
            raise UploadProcessingError

        if not self.filename:
            logger.error("Missing image file name")
            raise UploadProcessingError

        try:
            # Retrieve the fileIdentifier node, which contains the identifier required to build the
            # IIIF url for the image (if there is only one Page node in the file.)
            self.file_identifier = node.find(
                "{*}Description/{*}sourceImageInformation/{*}fileIdentifier",
                namespaces=self.namespaces,
            ).text
        except AttributeError:
            self.file_identifier = None
