import logging
from pathlib import Path
from uuid import UUID

from arkindex.exceptions import ErrorResponse
from rich.progress import Progress

from arkindex_cli.auth import Profiles
from teklia_toolbox.pagexml import PageXmlPage

logger = logging.getLogger(__name__)


class PageXmlParser:
    def __init__(self, client, path_or_xml, worker_run_id):
        self.pagexml_page = PageXmlPage(path_or_xml)
        self.client = client
        self.worker_run = str(worker_run_id)

        self.corpus_types = None

    def fetch_corpus_types(self, corpus_id):
        """
        fetches the element types which are available in the destination corpus
        """
        corpus = self.client.request("RetrieveCorpus", id=corpus_id)
        self.corpus_types = [elt_type["slug"] for elt_type in corpus["types"]]

    def check_element(self, region):
        """
        checks if the element's polygon contains enough points to create a transcription on it
        and returns the points
        check if all coordinates are positive, clip to 0 otherwise
        """
        points = region.points
        region_id = region.id
        if points is None:
            logger.warning(f"No points in region {region_id}")
            return

        if len(points) < 3:
            logger.warning(
                f"Ignoring region {region_id} (not enough points in polygon)"
            )
            return

        return [(max(0, x), max(0, y)) for x, y in points]

    def save_metadata(self, element_id, attributes):
        metadata_list = [
            {
                "type": "text",
                "name": attribute,
                "value": value,
            }
            for attribute, value in attributes.items()
            if attribute != "id"
        ]
        if not metadata_list:
            return

        try:
            self.client.request(
                "CreateMetaDataBulk",
                id=element_id,
                body={
                    "worker_run_id": self.worker_run,
                    "metadata_list": metadata_list,
                },
            )
        except ErrorResponse as e:
            logger.error(
                f"Failed in creating metadata on element {element_id}: {e.status_code} - {e.content}"
            )

    def save_element(
        self, corpus_id, parent_id, image_id, name, points, elt_type, attributes
    ):
        """
        creates an element for a given region
        a transcription will be created on text region elements
        """
        try:
            element = self.client.request(
                "CreateElement",
                body={
                    "type": elt_type,
                    "name": name,
                    "corpus": corpus_id,
                    "parent": parent_id,
                    "image": image_id,
                    "polygon": points,
                    "worker_run_id": self.worker_run,
                },
            )

            if attributes:
                self.save_metadata(element["id"], attributes)

            return element
        except ErrorResponse as e:
            logger.error(f"Failed in creating element: {e.status_code} - {e.content}")
            return None

    def save_transcription(self, region, element):
        """
        create a transcription on an element
        """
        logger.debug(f"Creating transcription for element {element['name']}...")
        try:
            self.client.request(
                "CreateTranscription",
                id=element["id"],
                body={
                    "text": region.text,
                    "worker_run_id": self.worker_run,
                    "confidence": 1,
                },
            )
        except ErrorResponse as e:
            logger.error(
                f"Failed in creating transcription: {e.status_code} - {e.content}"
            )

    def save_transcriptions(
        self, parent_element: dict, element_type: str, transcriptions: list[dict]
    ) -> list[dict] | None:
        """
        Create elements and transcriptions on a parent element
        """
        logger.debug(
            f"Creating {element_type} elements and transcriptions on parent element {parent_element['name']}..."
        )
        try:
            return self.client.request(
                "CreateElementTranscriptions",
                id=parent_element["id"],
                body={
                    "element_type": element_type,
                    "worker_run_id": self.worker_run,
                    "transcriptions": transcriptions,
                    "return_elements": True,
                },
            )
        except ErrorResponse as e:
            logger.error(
                f"Failed creating {element_type} elements and transcriptions on parent element {parent_element['name']}: {e.status_code} - {e.content}"
            )

    def save(self, element, image_id):
        region_count, element_ts_count = 0, 0
        for region in self.pagexml_page.page.text_regions:
            points = self.check_element(region)
            if points is None:
                continue

            if region.type == "paragraph":
                elt_type = "paragraph"
            else:
                elt_type = "text_zone"

            try:
                region_element = self.save_element(
                    corpus_id=element["corpus"]["id"],
                    parent_id=element["id"],
                    image_id=image_id,
                    name=str(region_count),
                    points=points,
                    elt_type=elt_type,
                    attributes=region.element.attrib,
                )

                if region_element:
                    region_count += 1
                    self.save_transcription(region=region, element=region_element)
                    element_ts_count += 1
                    logger.info(
                        f"Created element {region_element['id']} and its transcription"
                    )
                else:
                    logger.error(
                        "Could not create a transcription on the element because element creation failed"
                    )
                    continue
            except ErrorResponse as e:
                logger.error(
                    f"Failed in creating element: {e.status_code} - {e.content}"
                )

            line_transcriptions = []
            line_metadata = []
            for line in region.lines:
                points = self.check_element(line)
                if points is None:
                    continue

                line_transcriptions.append(
                    {
                        "polygon": points,
                        "text": line.text,
                        "confidence": 1,
                        "element_confidence": 1,
                    }
                )
                line_metadata.append(line.element.attrib)

            created_elements = self.save_transcriptions(
                region_element, "text_line", line_transcriptions
            )
            if created_elements is None:
                continue

            element_ts_count += len(created_elements)

            for transcription_element, metadata in zip(created_elements, line_metadata):
                if not line_metadata:
                    continue
                try:
                    self.save_metadata(transcription_element["element_id"], metadata)
                except ErrorResponse as e:
                    logger.error(
                        f"Failed publishing metadata on element {transcription_element['element_id']}: {e.status_code} - {e.content}"
                    )

        logger.info(
            f"Parsed {region_count} text regions and created {element_ts_count} elements with a transcription."
        )

        # Fetch corpus types once when parsing the first XML file
        if self.corpus_types is None:
            self.fetch_corpus_types(element["corpus"]["id"])

        for region_type, regions in zip(
            ["graphic", "separator", "table", "music", "noise", "unknown"],
            [
                self.pagexml_page.page.graphic_regions,
                self.pagexml_page.page.separator_regions,
                self.pagexml_page.page.table_regions,
                self.pagexml_page.page.music_regions,
                self.pagexml_page.page.noise_regions,
                self.pagexml_page.page.unknown_regions,
            ],
            strict=True,
        ):
            region_count, element_count = 0, 0
            for region in regions:
                points = self.check_element(region)
                if points is None:
                    continue

                elt_type = region_type if region_type != "graphic" else region.type

                if elt_type not in self.corpus_types:
                    self.client.request(
                        "CreateElementType",
                        body={
                            "slug": elt_type,
                            "display_name": elt_type.capitalize(),
                            "folder": False,
                            "corpus": element["corpus"]["id"],
                        },
                    )
                    self.corpus_types.append(elt_type)

                try:
                    region_element = self.save_element(
                        corpus_id=element["corpus"]["id"],
                        parent_id=element["id"],
                        image_id=image_id,
                        name=str(region_count),
                        points=points,
                        elt_type=elt_type,
                        attributes=region.element.attrib,
                    )

                    if region_element:
                        region_count += 1
                        logger.info(
                            f"Created element {region_element['id']} without transcription"
                        )
                        element_count += 1
                except ErrorResponse as e:
                    logger.error(
                        f"Failed in creating element: {e.status_code} - {e.content}"
                    )

            logger.info(
                f"Parsed {region_count} {region_type} regions and created {element_count} elements."
            )


def add_pagexml_import_parser(subcommands):
    pagexml_import_parser = subcommands.add_parser(
        "pagexml",
        description="Upload PAGE-XML transcriptions to images on Arkindex.",
        help="Upload PAGE-XML transcriptions to images on Arkindex.",
    )
    pagexml_import_parser.add_argument(
        "--worker-run-id",
        help="Worker Run used to publish elements, transcriptions and metadata in bulk",
        type=UUID,
        required=True,
    )
    pagexml_import_parser.add_argument(
        "--xml-path",
        type=Path,
        help="the path of the folder containing the xml files or the file containing the paths to the xml files",
        required=True,
    )
    pagexml_import_parser.add_argument(
        "--parent",
        help="UUID of an existing parent element for all the imported data",
        type=UUID,
        required=True,
    )
    pagexml_import_parser.set_defaults(func=run)


def run(
    parent: UUID,
    worker_run_id: UUID,
    xml_path: Path | None = None,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    """
    Push PAGE-XML transcriptions on Arkindex
    """
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles(gitlab_secure_file)
        profile = profiles.get_or_exit(profile_slug)
        client = profiles.get_api_client(profile)

    if xml_path.is_dir():
        files = [f for f in xml_path.glob("*.xml")]
    elif xml_path.is_file():
        files = [f.strip() for f in xml_path.read_text().splitlines()]
    else:
        logger.error(f"path {xml_path} doesn't exist")

    if len(files) == 0:
        logger.error("No files are specified")
        return

    for f in files:
        parser = PageXmlParser(client, f, worker_run_id)
        arkindex_name = parser.pagexml_page.page.image_name

        if not arkindex_name:
            logger.error(f"No image name for file {f}")
            continue

        logger.info(f"pushing annotations for page {arkindex_name}")
        found = False
        try:
            for p in client.paginate(
                "ListElementChildren",
                id=parent,
                type="page",
                name=arkindex_name,
                recursive=True,
            ):
                if arkindex_name == p["name"]:
                    parser.save(element=p, image_id=p["zone"]["image"]["id"])
                    found = True
                    break

            if not found:
                logger.error(
                    f"a page with the name {arkindex_name} was not found on Arkindex"
                )

        except ErrorResponse as e:
            logger.error(f"Failed in retrieving page: {e.status_code} - {e.content}")
