import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import UUID
from xml.sax.saxutils import escape

from arkindex_cli.commands.export.utils import BoundingBox
from arkindex_export import (
    Element,
    Image,
    Transcription,
    WorkerRun,
    WorkerVersion,
    open_database,
)
from arkindex_export.queries import list_children
from peewee import JOIN

logger = logging.getLogger(__name__)

# Namespaces for the ALTO v4 structure
NAMESPACES = {
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xmlns": "http://www.loc.gov/standards/alto/ns-v4#",
    "xsi:schemaLocation": (
        "http://www.loc.gov/standards/alto/ns-v4# "
        "http://www.loc.gov/standards/alto/v4/alto-4-2.xsd"
    ),
    "xmlns:xlink": "http://www.w3.org/1999/xlink",
}


def add_alto_parser(subcommands):
    alto_parser = subcommands.add_parser(
        "alto",
        description="Read data from an exported database and generate ALTO pages grouped by folder.",
        help="Generates ALTO XMLs from an Arkindex export.",
    )
    alto_parser.add_argument(
        "--folder-ids",
        type=UUID,
        help="Limit the export to one or more folders. Exports all folders corresponding to FOLDER_TYPE by default.",
        action="append",
    )
    alto_parser.add_argument(
        "--mets",
        help="Generate a METS file linking the exported ALTO XML files and the IIIF images.",
        action="store_true",
    )
    alto_parser.add_argument(
        "--folder-type",
        default="folder",
        type=str,
        help="Slug of an element type to use for folders. Defaults to `folder`.",
    )
    alto_parser.add_argument(
        "--page-type",
        default="page",
        type=str,
        help="Slug of an element type to use for pages. Defaults to `page`.",
    )
    alto_parser.add_argument(
        "--layout-tag",
        type=str,
        help="Slug of an element type to export as GraphicalElement nodes.",
    )
    alto_parser.add_argument(
        "--line-type",
        default="text_line",
        type=str,
        help="Slug of an element type to use for lines. Defaults to `text_line`.",
    )
    alto_parser.add_argument(
        "-o",
        "--output",
        default=Path.cwd(),
        type=Path,
        help="Path to a directory where files will be exported to. Defaults to the current directory.",
        dest="output_path",
    )
    alto_parser.set_defaults(func=run)


def xml_bounding_box(polygon) -> BoundingBox:
    """
    Gets the coordinates of the a polygon and sets the coordinates of the lower
    left point at which box starts, third value is the width of the box, the last
    one is the height,
    contrary to reportlab coordinates system in alto format starts from the top
    left corner as for arkindex one
    """

    # getting polygon coordinates
    x_coords, y_coords = zip(*json.loads(polygon))

    # determining line box dimensions
    min_x, min_y = min(x_coords), min(y_coords)
    max_x, max_y = max(x_coords), max(y_coords)
    width, height = max_x - min_x, max_y - min_y

    return BoundingBox(min_x, min_y, width, height)


def alto_xml_gen(
    folder: Element,
    output_path: str,
    page_type,
    line_type,
    mets=False,
    **kwargs,
):
    """
    - Get the elements from the database path and create a folder for each
    folder element.
    - Write  each page and relative lines as an alto xml file into the parent
    newly created folder at the specified output_path.
    - Write a mets file in the relevant folder, if the option is used.
    """

    layout_tag = kwargs.get("layout_tag", None)
    page_list = (
        list_children(folder.id)
        .join(Image, on=Element.image)
        .switch(Element)
        .join(WorkerRun, JOIN.LEFT_OUTER)
        .select(Element, Image, WorkerRun)
        .where(Element.type == page_type)
    )

    # for the METS file
    alto_files = []
    image_files = []

    # validating the folder has pages, if not, no file is created
    if page_list.count():
        # folder path to be reused
        folder_path = Path(output_path) / folder.id
        # creating folder directory
        folder_path.mkdir()

        for count, page in enumerate(page_list, start=1):
            # defining root element of the alto doc as arkindex folder
            alto_root = ET.Element("alto", NAMESPACES)
            alto_description = ET.SubElement(alto_root, "Description")
            alto_unit = ET.SubElement(alto_description, "MeasurementUnit")
            # changed unit measure
            alto_unit.text = "pixel"

            # Layout markup alto subelement
            alto_layout = ET.SubElement(alto_root, "Layout")

            # initializing the set of worker ids for pages, lines and transcriptions to
            # fill description markup
            worker_set = set()

            # calling bounding_box on the page polygon to get the page dimensions
            # and fill the attributes dictionary
            page_box_dim = xml_bounding_box(page.polygon)

            # Page markup Layout subelement with specified attributes in the dictionary
            alto_page = ET.SubElement(
                alto_layout,
                "Page",
                attrib={
                    # any user-defined class but must start by a letter
                    "ID": f"page_{page.id}",
                    # PHYSICAL_IMG_NR is the number of the page within the document
                    "PHYSICAL_IMG_NR": str(count),
                    "WIDTH": str(page_box_dim.width),
                    "HEIGHT": str(page_box_dim.height),
                },
            )
            alto_print_space = ET.SubElement(alto_page, "PrintSpace")

            # adding page worker id in set and as page attribute if exists
            if page.worker_run_id is not None:
                worker_set.add(page.worker_run.worker_version_id)
                alto_page.set(
                    "PROCESSINGREFS", f"worker_{page.worker_run.worker_version_id}"
                )

            # getting the list of Transcriptions for each page
            page_transcriptions = (
                Transcription.select()
                .join(WorkerRun, JOIN.LEFT_OUTER)
                .select(Transcription, WorkerRun)
                .where(Transcription.element.in_(list_children(page.id)))
            )

            # creating GraphicalElement tags for layout_tag elements if specified
            if layout_tag:
                subelements = (
                    list_children(folder.id)
                    .join(WorkerRun, JOIN.LEFT_OUTER)
                    .select(Element, WorkerRun)
                    .where(Element.type == layout_tag)
                )
                # create the LayoutTag, if there are subelements in the document
                if subelements.count():
                    alto_tags = ET.SubElement(alto_root, "Tags")
                    ET.SubElement(
                        alto_tags,
                        "LayoutTag",
                        attrib={"ID": layout_tag, "LABEL": layout_tag},
                    )
                for item in subelements:
                    subelement_bb = xml_bounding_box(item.polygon)
                    alto_subelement = ET.SubElement(
                        alto_print_space,
                        "GraphicalElement",
                        attrib={
                            "HPOS": str(subelement_bb.x),
                            "VPOS": str(subelement_bb.y),
                            "WIDTH": str(subelement_bb.width),
                            "HEIGHT": str(subelement_bb.height),
                            "TAGREFS": layout_tag,
                        },
                    )
                    # adding worker id in set and as attribute if exists
                    if item.worker_run_id is not None:
                        worker_set.add(item.worker_run.worker_version_id)
                        alto_subelement.set(
                            "PROCESSINGREFS",
                            f"worker_{item.worker_run.worker_version_id}",
                        )

                    alto_subelement_shape = ET.SubElement(alto_subelement, "Shape")
                    alto_subelement_polygon = ET.SubElement(
                        alto_subelement_shape, "Polygon"
                    )

                    # creating the xml formatted string for the polygon
                    xml_pol_str = " ".join(
                        f"{x},{y}" for x, y in json.loads(item.polygon)
                    )
                    alto_subelement_polygon.set("POINTS", xml_pol_str)

            # adding textblock and textline subelements when page contains transcriptions
            if page_transcriptions.count():
                # creating a dictionary where keys are lines ids and values are
                # relative line transcriptions
                transcriptions_dict = {
                    transcription.element_id: transcription
                    for transcription in page_transcriptions
                }

                alto_text_block = ET.SubElement(alto_print_space, "TextBlock")

                # For now a page can have a single text block
                alto_text_block.set("ID", f"page_{page.id}_textblock_{count}")

                for line in (
                    list_children(page.id)
                    .join(WorkerRun, JOIN.LEFT_OUTER)
                    .select(Element, WorkerRun)
                    .where(Element.type == line_type)
                ):
                    # calling xml_bounding_box to fill textline attributes
                    line_box_dim = xml_bounding_box(line.polygon)

                    alto_line = ET.SubElement(
                        alto_text_block,
                        "TextLine",
                        attrib={
                            "HPOS": str(line_box_dim.x),
                            "VPOS": str(line_box_dim.y),
                            "WIDTH": str(line_box_dim.width),
                            "HEIGHT": str(line_box_dim.height),
                        },
                    )
                    # adding line worker id in set and as attribute if exists
                    if line.worker_run_id is not None:
                        worker_set.add(line.worker_run.worker_version_id)
                        alto_line.set(
                            "PROCESSINGREFS",
                            f"worker_{line.worker_run.worker_version_id}",
                        )

                    alto_shape = ET.SubElement(alto_line, "Shape")
                    alto_polygon = ET.SubElement(alto_shape, "Polygon")

                    # creating the xml formatted string for polygon
                    xml_pol_str = " ".join(
                        f"{x},{y}" for x, y in json.loads(line.polygon)
                    )

                    alto_polygon.set("POINTS", xml_pol_str)
                    alto_string = ET.SubElement(alto_line, "String")

                    # setting default attributes
                    if line.id not in transcriptions_dict.keys():
                        alto_string.set("WC", "0")
                        alto_string.set("CONTENT", "no_content_available")
                        alto_string.set("PROCESSINGREFS", "no_processing_refs")

                    # overwriting attribute would create a new string element
                    else:
                        alto_string.set(
                            "WC", str(transcriptions_dict[line.id].confidence)
                        )
                        # by default '&', '<', and '>' are escaped in a string of
                        # data additional entity '"' is escape as it leads to close
                        # the attribute string
                        alto_string.set(
                            "CONTENT",
                            escape(transcriptions_dict[line.id].text, {'"': "&quot;"}),
                        )
                        # adding transcription worker id in set
                        worker_run_id = transcriptions_dict[line.id].worker_run_id
                        if worker_run_id is not None:
                            alto_string.set(
                                "PROCESSINGREFS",
                                f"worker_{transcriptions_dict[line.id].worker_run.worker_version_id}",
                            )
                            worker_set.add(
                                transcriptions_dict[
                                    line.id
                                ].worker_run.worker_version_id
                            )

            image_url = page.image.url
            alto_image_info = ET.SubElement(alto_description, "sourceImageInformation")
            alto_filename = ET.SubElement(alto_image_info, "fileName")
            alto_filename.text = image_url.split("/")[-1]
            alto_file_id = ET.SubElement(alto_image_info, "fileIdentifier")
            alto_file_id.text = image_url
            alto_doc_id = ET.SubElement(alto_image_info, "documentIdentifier")
            # document identifier is the page id
            alto_doc_id.text = page.id

            for worker in WorkerVersion.select().where(
                WorkerVersion.id.in_(worker_set)
            ):
                alto_processing = ET.SubElement(alto_description, "Processing")
                alto_processing.set("ID", f"worker_{worker.id}")
                alto_category = ET.SubElement(alto_processing, "processingCategory")
                alto_category.text = "contentGeneration"
                alto_step_desc = ET.SubElement(
                    alto_processing, "processingStepDescription"
                )
                alto_step_desc.text = worker.type
                alto_soft = ET.SubElement(alto_processing, "processingSoftware")
                alto_soft_name = ET.SubElement(alto_soft, "softwareName")
                alto_soft_name.text = worker.name
                alto_soft_ver = ET.SubElement(alto_soft, "softwareVersion")
                alto_soft_ver.text = worker.revision

            # creating the tree from the alto_page root element
            alto_tree = ET.ElementTree(alto_root)

            # filepath for the tree to be written in
            alto_file = folder_path / f"{page.id}.xml"

            # writing the tree as xml file in alto_page_path
            alto_tree.write(alto_file, encoding="utf-8", method="xml")

            # for the METS file
            alto_files.append(
                {
                    "id": page.id,
                    "mime": "application/xml",
                    "location": str(alto_file),
                    "image_id": page.image.id,
                }
            )
            image_files.append(
                {
                    "id": page.image.id,
                    "mime": "image/jpeg",
                    "location": image_url,
                    "page_id": page.id,
                }
            )

            logger.info(f"created alto xml file at {alto_file}")

        if mets:
            ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

            mets_root = ET.Element(
                "mets",
                {
                    "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": (
                        "http://www.loc.gov/METS "
                        "http://www.loc.gov/standards/mets/mets.xsd"
                    ),
                    "OBJID": folder.id,
                },
            )

            # fileSec with the alto files and images info
            file_section = ET.SubElement(mets_root, "fileSec")
            alto_file_group = ET.SubElement(file_section, "fileGrp", {"ID": "ALTO"})
            for item in alto_files:
                file_item = ET.SubElement(
                    alto_file_group,
                    "file",
                    {"ID": item["id"], "MIMETYPE": item["mime"]},
                )
                ET.SubElement(
                    file_item,
                    "FLocat",
                    {
                        "LOCTYPE": "OTHER",
                        "OTHERLOCTYPE": "FILE",
                        "href": item["location"],
                    },
                )
            img_file_group = ET.SubElement(file_section, "fileGrp", {"ID": "IMAGES"})
            for item in image_files:
                img_item = ET.SubElement(
                    img_file_group, "file", {"ID": item["id"], "MIMETYPE": item["mime"]}
                )
                ET.SubElement(
                    img_item, "FLocat", {"LOCTYPE": "URL", "href": item["location"]}
                )

            # structMap linking alto files and images
            structure_map = ET.SubElement(mets_root, "structMap")
            div = ET.SubElement(structure_map, "div", {"TYPE": "folder"})
            for item in alto_files:
                page_div = ET.SubElement(div, "div", {"TYPE": "page"})
                ET.SubElement(page_div, "fptr", {"FILEID": item["id"]})
                ET.SubElement(page_div, "fptr", {"FILEID": item["image_id"]})

            # creating the tree from the mets_root element
            mets_tree = ET.ElementTree(mets_root)

            # filepath for the tree to be written in
            mets_file_path = folder_path / "mets_entrypoint.xml"

            # writing the tree as xml file in mets_file_path
            mets_tree.write(mets_file_path, encoding="utf-8", method="xml")

            logger.info(f"created METS file at {mets_file_path}")


def run(
    database_path: Path,
    output_path: Path,
    folder_type: str,
    folder_ids: list[UUID] = [],
    **kwargs,
):
    database_path = database_path.absolute()
    assert database_path.is_file(), f"Database at {database_path} not found"

    output_path = output_path.absolute()
    assert output_path.is_dir(), f"Output path {output_path} is not a valid directory"

    open_database(database_path)

    # Preparing ALTO v4 namespaces
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

    folders = Element.select().where(Element.type == folder_type)
    if folder_ids:
        folders = folders.where(Element.id.in_(folder_ids))

    assert folders.count(), f"No '{folder_type}' folders were found"

    for folder in folders:
        alto_xml_gen(
            folder,
            output_path=output_path,
            **kwargs,
        )
