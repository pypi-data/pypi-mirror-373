import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from uuid import UUID

from arkindex_cli.commands.export.utils import MANUAL_SOURCE, uuid_or_manual
from arkindex_export import Element, ElementPath, Image, Transcription, open_database
from arkindex_export.queries import list_children

logger = logging.getLogger(__name__)

# Namespaces for the PageXML structure
# https://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd
NAMESPACES = {
    "xmlns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xsi:schemaLocation": (
        "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15 "
        "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"
    ),
}

READING_DIRECTION = {
    "horizontal-lr": "left-to-right",
    "horizontal-rl": "right-to-left",
    "vertical-lr": "top-to-bottom",
    "vertical-rl": "top-to-bottom",
}
TEXT_LINE_ORDER = {
    "horizontal-lr": "top-to-bottom",
    "horizontal-rl": "top-to-bottom",
    "vertical-lr": "left-to-right",
    "vertical-rl": "right-to-left",
}


def add_pagexml_parser(subcommands):
    pagexml_parser = subcommands.add_parser(
        "pagexml",
        description="Read data from an exported database and generate PageXML files.",
        help="Generates PageXMLs from an Arkindex export.",
    )
    pagexml_parser.add_argument(
        "--parent",
        type=UUID,
        help="Limit the export to the children of a given element.",
    )
    pagexml_parser.add_argument(
        "--page-type",
        default="page",
        type=str,
        help="Slug of an element type to use for pages. Defaults to `page`.",
    )
    pagexml_parser.add_argument(
        "--paragraph-type",
        type=str,
        help="Slug of an element type to use for paragraphs.",
    )
    pagexml_parser.add_argument(
        "--line-type",
        default="text_line",
        type=str,
        help="Slug of an element type to use for lines. Defaults to `text_line`.",
    )
    pagexml_parser.add_argument(
        "--transcription-source",
        type=uuid_or_manual,
        help=f"Only retrieve the transcriptions created by a specific worker run (UUID) or manual transcriptions ('{MANUAL_SOURCE}').",
    )
    pagexml_parser.add_argument(
        "-o",
        "--output",
        default=Path.cwd(),
        type=Path,
        help="Path to a directory where files will be exported to. Defaults to the current directory.",
        dest="output_path",
    )
    pagexml_parser.set_defaults(func=run)


def _get_id_attribute(element: Element) -> str:
    return f"{element.type}-{element.name}"


def _get_points_attribute(element: Element) -> str:
    return " ".join(f"{x},{y}" for x, y in json.loads(element.polygon)[:4])


def create_text_region(element: Element, page_node: ET.Element) -> ET.Element:
    # PageXML orientation ranges from -179° (anti-clockwise) to 180° (clockwise)
    orientation = element.rotation_angle
    if orientation > 180:
        orientation = 360 - orientation

    region_node = ET.SubElement(
        page_node,
        "TextRegion",
        attrib={
            "id": _get_id_attribute(element),
            "type": "paragraph",
            "orientation": str(orientation),
        },
    )
    ET.SubElement(
        region_node, "Coords", attrib={"points": _get_points_attribute(element)}
    )

    return region_node


def find_page_lines(
    element: Element, line_type: str, region_node: ET.Element
) -> list[tuple[Element, ET.Element]]:
    # The current child is a simple line
    if element.type == line_type:
        return [(element, region_node)]

    # The current child is a paragraph, we iterate over its child lines
    lines = []
    for line in (
        Element.select()
        .join(ElementPath, on=ElementPath.child)
        .where(ElementPath.parent_id == element.id, Element.type == line_type)
        .order_by(ElementPath.ordering)
    ):
        # When lines are grouped in a paragraph, we also output their coordinates in a <TextLine> node
        line_node = ET.SubElement(
            region_node, "TextLine", attrib={"id": _get_id_attribute(line)}
        )
        ET.SubElement(
            line_node, "Coords", attrib={"points": _get_points_attribute(line)}
        )
        lines.append((line, line_node))

    return lines


def find_line_transcription(
    parent: Element, element: Element, transcription_source: str | None, **kwargs
) -> Transcription | None:
    transcriptions = Transcription.select().where(Transcription.element == element)
    if transcription_source and transcription_source == MANUAL_SOURCE:
        transcriptions = transcriptions.where(Transcription.worker_run_id.is_null())
    elif transcription_source:
        transcriptions = transcriptions.where(
            Transcription.worker_run_id == transcription_source
        )

    nb_transcriptions = transcriptions.count()
    if nb_transcriptions > 1:
        logger.error(
            f"Found {nb_transcriptions} transcriptions on {element.type} {element.name} ({element.id}) from {parent.type} {parent.name} ({parent.id})."
        )
        exit(1)

    return transcriptions.first()


def get_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def generate_pagexml(
    page: Element,
    output_path: str,
    paragraph_type: str | None,
    line_type: str,
    **kwargs,
) -> None:
    root_node = ET.Element("PcGts", NAMESPACES)

    # Adding some metadata to the root node
    metadata_node = ET.SubElement(root_node, "Metadata")
    ET.SubElement(metadata_node, "Creator").text = "Arkindex CLI"
    now = get_now()
    ET.SubElement(metadata_node, "Created").text = now
    ET.SubElement(metadata_node, "LastChange").text = now

    # Creating the <Page> element, there is one per file
    page_node = ET.SubElement(
        root_node,
        "Page",
        attrib={
            "imageFilename": page.name,
            "imageWidth": str(page.image.width),
            "imageHeight": str(page.image.height),
        },
    )

    # Iterating over all direct children of the page that are either paragraphs or lines
    children = (
        Element.select()
        .join(ElementPath, on=ElementPath.child)
        .where(
            ElementPath.parent_id == page.id,
            Element.type.in_([paragraph_type, line_type]),
        )
        .order_by(ElementPath.ordering)
    )
    for child in children:
        region_node = create_text_region(child, page_node)

        # Finding all lines on the page, even the ones in paragraphs
        flattened_lines = find_page_lines(child, line_type, region_node)
        for line, parent_node in flattened_lines:
            # Getting the transcription for the current line if it exists
            transcription = find_line_transcription(page, line, **kwargs)

            text_equiv_node = ET.SubElement(
                parent_node,
                "TextEquiv",
                attrib={
                    "conf": f"{transcription.confidence:.2f}"
                    if transcription and transcription.confidence is not None
                    else "1.0"
                },
            )
            ET.SubElement(text_equiv_node, "Unicode").text = (
                transcription.text if transcription else ""
            )

            # Updating the <TextRegion> node attributes when we find its first line transcription
            if (
                transcription
                and "readingDirection" not in region_node.attrib
                and "textLineOrder" not in region_node.attrib
            ):
                region_node.attrib["readingDirection"] = READING_DIRECTION[
                    transcription.orientation
                ]
                region_node.attrib["textLineOrder"] = TEXT_LINE_ORDER[
                    transcription.orientation
                ]

    # Creating the tree from the PageXML root node and saving it to a file
    xml_tree = ET.ElementTree(root_node)
    ET.indent(xml_tree, space="    ", level=0)
    xml_file = output_path / f"{page.id}.xml"
    xml_tree.write(xml_file, encoding="utf-8", method="xml")
    logger.info(f"Created PageXML file at {xml_file}")


def run(
    database_path: Path,
    output_path: Path,
    parent: UUID | None,
    page_type: str,
    **kwargs,
) -> None:
    database_path = database_path.absolute()
    assert database_path.is_file(), f"Database at {database_path} not found"

    output_path = output_path.absolute()
    assert output_path.is_dir(), f"Output path {output_path} is not a valid directory"

    open_database(database_path)

    # Preparing PageXML namespaces
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

    elements = list_children(parent) if parent else Element.select()
    pages = elements.join(Image, on=Element.image).where(Element.type == page_type)
    for page in pages:
        generate_pagexml(page, output_path, **kwargs)
