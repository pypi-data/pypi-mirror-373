import logging
import shutil
import tempfile
from pathlib import Path
from uuid import UUID

from arkindex_cli.commands.export.utils import (
    bounding_box,
    bounding_box_arkindex,
    image_download,
)
from arkindex_export import Element, Image, Transcription, WorkerRun, open_database
from arkindex_export.queries import list_children
from peewee import JOIN

try:
    from reportlab.lib import colors
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    from PIL import Image as PILImage
except ImportError:
    DEPS_AVAILABLE = False
else:
    DEPS_AVAILABLE = True


logger = logging.getLogger(__name__)


def add_pdf_parser(subcommands):
    pdf_parser = subcommands.add_parser(
        "pdf",
        description=(
            "Read data from an exported database and generate a PDF with selectable text. "
            "Due to the PDF structure, only elements of type <page-type> are rendered for the specified folders."
        ),
        help="Generates a PDF from an Arkindex export.",
    )
    pdf_parser.add_argument(
        "--folder-ids",
        type=UUID,
        help="Limit the export to one or more folders. Exports all folders corresponding to FOLDER_TYPE by default.",
        action="append",
    )
    pdf_parser.add_argument(
        "--folder-type",
        default="folder",
        type=str,
        help="Slug of an element type to use for folders. Defaults to `folder`.",
    )
    pdf_parser.add_argument(
        "--page-type",
        default="page",
        type=str,
        help="Slug of an element type to use for pages. Defaults to `page`.",
    )
    text_source = pdf_parser.add_mutually_exclusive_group()
    text_source.add_argument(
        "--use-page-transcriptions",
        action="store_true",
        help="Export page-level transcriptions on the specified page-type elements. Cannot be used conjointly with --line-type.",
    )
    text_source.add_argument(
        "--line-type",
        default="text_line",
        type=str,
        help="Slug of an element type to use for lines. Defaults to `text_line`. Cannot be used conjointly with --use-page-transcriptions.",
    )
    pdf_parser.add_argument(
        "--debug",
        action="store_true",
        help="Make bounding boxes and transcriptions visible.",
    )
    pdf_parser.add_argument(
        "-o",
        "--output",
        default=Path.cwd(),
        type=Path,
        help="Path to a directory where files will be exported to. Defaults to the current directory.",
        dest="output_path",
    )
    pdf_parser.add_argument(
        "--order-by-name",
        action="store_true",
        help="Order exported elements by name instead of the internal position on Arkindex.",
    )
    pdf_parser.add_argument(
        "--transcription-worker-version",
        type=UUID,
        help="Filter transcriptions by worker version.",
    )
    pdf_parser.add_argument(
        "--name-pdf-with-id",
        action="store_true",
        help="Name exported PDF files after the folder Arkindex ID instead of its name.",
    )
    pdf_parser.set_defaults(func=run)


def list_folders(folder_type, folder_ids):
    folders = Element.select().where(Element.type == folder_type)
    if folder_ids is not None and len(folder_ids):
        folders = folders.where(Element.id.in_(folder_ids))
    return folders


def get_children_elements(
    parent_id,
    element_type,
    with_transcriptions=False,
    transcription_worker_version=None,
    order_by_name=False,
):
    children_elements = (
        list_children(parent_id)
        .select(Element, Image.url, Image.id)
        .join(Image, JOIN.LEFT_OUTER, on=[Image.id == Element.image_id])
        .where(Element.type == element_type)
    )
    # Ordering by ElementPath.ordering is the default in list_children
    if order_by_name:
        children_elements = children_elements.order_by(Element.name)
    # Prefetch transcriptions if with_transcriptions is true
    if with_transcriptions:
        transcriptions = Transcription.select()
        if transcription_worker_version:
            transcriptions = transcriptions.join(WorkerRun).where(
                WorkerRun.worker_version_id == transcription_worker_version
            )
        children_elements = children_elements.prefetch(transcriptions)

    return children_elements


def image_draw(page: Element, image_path: str, c: "canvas", temp_dir: str) -> tuple:
    """
    Draw suitable image depending on crop if it is necessary
    """
    assert DEPS_AVAILABLE, "Missing PDF export dependencies"

    # opens existing image with PIL to get its size
    image = PILImage.open(image_path)

    # page Element must have a polygon
    assert page.polygon is not None

    # set default imageDraw function parameters
    pdf_image_width, pdf_image_height = image.width, image.height

    # getting dimensions of page bounding box
    page_box_dim = bounding_box(page.polygon)

    if (page_box_dim.width, page_box_dim.height) != image.size:
        # handling case when to crop image
        # PIL coordinates start from top-left corner,
        # crop method gets 4-tuple defining the left, upper, right, and
        # lower pixel coordinate.
        crop_parameters = (
            page_box_dim.x,
            # absolute value is to prevent cases where bounding_box
            # y coordinate is higher than box height
            abs(page_box_dim.height - page_box_dim.y),
            page_box_dim.x + page_box_dim.width,
            page_box_dim.y,
        )

        # saving cropped file in temp_dir to be called by drawImage
        image_path = temp_dir / f"{page.id}.jpg"

        image = image.crop(crop_parameters)
        image.save(image_path, format="JPEG")

        logger.info(f"saved cropped image at: {image_path}")

        # updating drawImage and pagesize parameters to bounding box
        pdf_image_width, pdf_image_height = page_box_dim.width, page_box_dim.height

    # sizes page to fit relevant image
    c.setPageSize(image.size)

    # drawing suitable image
    c.drawImage(image_path, 0, 0, pdf_image_width, pdf_image_height, mask=None)

    return image.size


def pdf_gen(
    folder: Element,
    output_path,
    page_type,
    use_page_transcriptions,
    line_type,
    debug,
    order_by_name,
    transcription_worker_version,
    name_pdf_with_id,
    **kwargs,
) -> None:
    """
    Gets the database path, argument from cli, path to the generated pdf and the
    temporary directory where to find downloaded images
    """

    assert DEPS_AVAILABLE, "Missing PDF export dependencies. Run `pip install arkindex-cli[export]` to install them."

    # creating temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    logger.info(f"created temporary directory: {temp_dir}")

    # chooses color depending on debug option
    selected_color = colors.transparent

    if debug:
        selected_color = colors.fuchsia

    try:
        # canvas requires the input path as string
        file_stem = folder.id if name_pdf_with_id else folder.name

        c = canvas.Canvas(str((Path(output_path) / file_stem).with_suffix(".pdf")))
        c.setTitle(folder.name)

        elements = get_children_elements(
            folder.id,
            page_type,
            use_page_transcriptions,
            transcription_worker_version,
            order_by_name,
        )
        for page in elements:
            logger.info(f"Processing page {page}")

            page_bbox = bounding_box_arkindex(page.polygon)
            if page.image.url is None:
                logger.warning(f"no image for page {page.name} ({page.id})")
                continue

            # downloading existing image
            existing_image = image_download(page.image.url, page.image.id, temp_dir)

            # running reportlab drawing actions through image_draw and
            # returning updated image dimensions for the next steps
            image_width, image_height = image_draw(page, existing_image, c, temp_dir)

            if use_page_transcriptions:
                # Only export page-level transcriptions
                page_transcriptions = page.transcription_set
                if not len(page_transcriptions):
                    logger.warning(
                        f"No page-level transcription for {page_type} {page.id}."
                    )
                for transcription in page_transcriptions:
                    c.setFillColor(selected_color)
                    textobject = c.beginText(0, image_height)
                    for line in transcription.text.splitlines(False):
                        textobject.textLine(line.rstrip())
                    c.drawText(textobject)

            else:
                # retrieve all the children elements of the given line_type of the page element,
                # with transcriptions if they have some
                lines = get_children_elements(
                    page.id,
                    line_type,
                    with_transcriptions=True,
                    transcription_worker_version=transcription_worker_version,
                )

                if not lines:
                    logger.warning(f"no {line_type!r} in page {page.name} ({page.id})")

                for line in lines:
                    # handling case where no polygon is returned
                    if line.polygon is None:
                        logger.warning(f"no polygon for line {line.name} ({line.id})")
                        continue
                    # getting bounding box dimensions
                    line_box_dim = bounding_box(
                        line.polygon, offset_x=page_bbox.x, offset_y=page_bbox.y
                    )

                    # drawing line polygon bounding box
                    # as the y axis is inverted, y origin point is "height - max_y"
                    c.rect(
                        # Remove page offset
                        line_box_dim.x,
                        image_height - line_box_dim.y,
                        line_box_dim.width,
                        line_box_dim.height,
                        # linebox visible according to debug value
                        stroke=debug,
                    )

                    # handling case where line image is different from page image
                    if line.image.url != page.image.url:
                        logger.warning(
                            f"""
                            {line.name} ({line.id}) image different from {page.name}
                            ({page.id}) image
                            """
                        )
                        continue

                    # skip to the next line if there are no transcriptions
                    if not len(line.transcription_set):
                        continue

                    else:
                        for tr in line.transcription_set:
                            text_to_draw = tr.text

                            c.setFillColor(selected_color)

                            # get the width of a single character, arbitrarily first one
                            # Font is set to MONOSPACE one such as Courier,
                            # fontsize is arbitrarily set to 10
                            char_width = stringWidth(text_to_draw[0], "Courier", 10)

                            # calculating ratio between character height and character
                            # width to adjust fontsize, character height has been set to
                            # 10
                            char_ratio = 10 / char_width

                            # character width so the fontsize match with the line_box_width
                            # corresponds to line box width divided by total number
                            # of characters in the string
                            font_width = line_box_dim.width / len(text_to_draw)

                            # adjusts the font size to match line box width
                            c.setFont("Courier", font_width * char_ratio)
                            # as the y axis is inverted, y origin point is "height - max_y"
                            c.drawString(
                                line_box_dim.x,
                                image_height - line_box_dim.y,
                                text_to_draw,
                            )

            # save state and prepared new possible insertion within a page
            # (force PageBreak)
            c.showPage()

        # saving the whole canvas
        c.save()
        logger.info(f"{file_stem}.pdf generated at {output_path}")
    finally:
        shutil.rmtree(temp_dir)


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

    folders = list_folders(folder_type, folder_ids)
    assert folders, f"No '{folder_type}' folders were found"

    for folder in folders:
        pdf_gen(
            folder,
            database_path=database_path,
            output_path=output_path,
            **kwargs,
        )
