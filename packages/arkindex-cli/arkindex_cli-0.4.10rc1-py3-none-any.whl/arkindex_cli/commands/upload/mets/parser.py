import logging
import urllib.parse
import uuid
from operator import itemgetter
from pathlib import Path
from uuid import UUID

from arkindex import ArkindexClient
from arkindex.exceptions import ErrorResponse
from lxml import etree as ET
from lxml import objectify

from arkindex_cli.commands.upload import db
from arkindex_cli.commands.upload.alto import (
    create_element_parent,
    create_iiif_image,
    create_metadata,
    publish_nodes,
    upload_alto_file,
)
from arkindex_cli.commands.upload.alto.parser import (
    AltoElement,
    AltoMetadata,
    RootAltoElement,
)
from arkindex_cli.commands.upload.cache import Cache, save_cache
from arkindex_cli.commands.upload.exceptions import UploadProcessingError
from dateutil.parser import parse

logger = logging.getLogger(__name__)

# Only need METS base support here
METS_NS = {"mets": "http://www.loc.gov/METS/", "xlink": "http://www.w3.org/1999/xlink"}

IMAGE_SUFFIXES = (".jpeg", ".jpg", ".png", ".tiff", ".tif")
ALTO_SUFFIXES = (".xml",)


def get_metadata_type(value: str) -> str:
    def is_valid_number(value: str) -> bool:
        try:
            float(value)
        except Exception:
            return False
        return True

    def is_valid_date(value: str) -> bool:
        try:
            parse(value)
        except Exception:
            return False
        return True

    if value.startswith("http"):
        return "url"

    if is_valid_number(value):
        return "numeric"

    if is_valid_date(value):
        return "date"

    return "text"


class MetsImage:
    """
    A remote IIIF image
    """

    def __init__(self, image_relative_path: str, iiif_base_url: str, iiif_prefix: str):
        # Build IIIF url for the image
        # knowing only its relative path to the folder with METS file
        image_path = urllib.parse.urljoin(iiif_prefix, image_relative_path)
        self.url = iiif_base_url + urllib.parse.quote_plus(image_path)

        self.cache_key = f"image/{image_relative_path}"

    def publish(self, cache: Cache, arkindex_client: ArkindexClient):
        # Check cache
        self.arkindex_id = cache.get(self.cache_key)
        if self.arkindex_id is not None:
            return

        # Declare image on Arkindex
        self.arkindex_id = create_iiif_image(arkindex_client, self.url)
        logger.debug(f"Published image {self.arkindex_id}")

        # Store in cache
        cache.set(self.cache_key, self.arkindex_id)


class MetsAlto:
    """
    A local ALTO XML file
    """

    def __init__(self, path: Path, dpi_x: int | None = None, dpi_y: int | None = None):
        self.path = path

        with open(path) as file:
            # This ensures that comments in the XML files do not cause the
            # "no Alto namespace found" exception.
            parser = ET.XMLParser(remove_comments=True)
            tree = objectify.parse(file, parser=parser)
            self.root = RootAltoElement(tree.getroot(), dpi_x=dpi_x, dpi_y=dpi_y)

    def __eq__(self, other):
        # Used in unit tests to compare 2 instances
        return self.path.absolute() == other.path.absolute()

    def parse(self, target_id: str):
        self.target_id = target_id

        # Find element matching provided id
        xpath = f".//*[@ID='{target_id}']"
        xml_target = self.root.content.find(xpath)
        if xml_target is None:
            return

        # Retrieve its page size
        xpath = './ancestor::*[local-name()="Page"]'
        xml_page = xml_target.xpath(xpath)
        page = AltoElement(xml_page.pop()) if xml_page else None

        # Parse ALTO file down that element
        self.element = AltoElement(
            xml_target,
            page_width=page.width if page else None,
            page_height=page.height if page else None,
            unit=self.root.unit,
            dpi_x=self.root.dpi_x,
            dpi_y=self.root.dpi_y,
        )
        self.element.parse_children()

    def publish(
        self,
        arkindex_client: ArkindexClient,
        worker_run_id: UUID,
        parent_id: UUID | None = None,
        corpus_id: str | None = None,
        image: MetsImage | None = None,
        publish_metadata: bool = True,
        ignore_types: list[str] = [],
    ):
        # Check cache
        cache = Cache(self.path.with_suffix(".json"))
        arkindex_id = cache.get(self.target_id)
        if arkindex_id is not None:
            # Create parent link
            if parent_id is not None:
                create_element_parent(
                    client=arkindex_client, parent_id=parent_id, child_id=arkindex_id
                )
            return

        image_id = image.arkindex_id if image is not None else None
        publish_nodes(
            client=arkindex_client,
            nodes=[
                self.element,
            ],
            image_id=image_id,
            corpus_id=corpus_id,
            parent_id=parent_id,
            worker_run_id=worker_run_id,
            cache=cache,
            publish_metadata=publish_metadata,
            ignore_types=ignore_types,
        )


class MetsElement:
    def __init__(
        self, node: ET._Element | None, parent: "MetsElement | None" = None
    ) -> None:
        self.node = node
        self.parent = parent

        # Populated during publication on Arkindex
        self.arkindex_id = None

        # List of the metadata associated with the element
        self.metadata_list = [
            {"name": "METS ID", "value": self.id, "type": "reference"}
        ]
        if self.node is not None:
            self.metadata_list.extend(
                [
                    {
                        "name": key,
                        "value": value.strip(),
                        "type": get_metadata_type(value.strip()),
                    }
                    for key, value in self.node.attrib.items()
                    if (
                        key
                        and value.strip()
                        and key not in ["TYPE", "ID", "LABEL", "DMDID"]
                    )
                ]
            )

    @property
    def parent_id(self):
        if self.parent is None:
            return
        return self.parent.arkindex_id

    @property
    def type(self):
        if self.node is None:
            return "folder"
        return self.node.attrib["TYPE"]

    @property
    def id(self):
        if self.node is None:
            return "ROOT"
        return self.node.attrib["ID"]

    @property
    def label(self):
        if self.node is None:
            return "METS Import"
        return self.node.attrib.get("LABEL", self.id)[:250]

    def publish_element(
        self,
        arkindex_client: ArkindexClient,
        worker_run_id: UUID,
        corpus_id: str | None = None,
    ) -> str:
        payload = {
            "type": self.type,
            "name": self.label,
            "parent": self.parent_id and str(self.parent_id) or None,
            "worker_run_id": str(worker_run_id),
        }

        # Populate the database by adding element to the parent as if using the Arkindex API
        if db.is_available():
            element_id = str(uuid.uuid4())

            # Always create new element as on Arkindex
            db.create_elements(
                payload.pop("parent"),
                [
                    {
                        "id": element_id,
                        **payload,
                    }
                ],
            )

            return element_id

        # Use API client
        try:
            return arkindex_client.request(
                "CreateElement", body={"corpus": corpus_id, **payload}
            )["id"]
        except ErrorResponse as e:
            logger.error(f"Failed to create placeholder element: {e.content}")
            raise UploadProcessingError

    def publish(
        self,
        cache: Cache,
        arkindex_client: ArkindexClient,
        worker_run_id: UUID,
        corpus_id: str | None = None,
        publish_metadata: bool = False,
    ):
        """
        Publish elements not linked to an image: every element mentioned in METS
        that is not described by an ALTO file
        """
        # Check cache
        cache_key = f"mets/{self.id}"
        self.arkindex_id = cache.get(cache_key)
        if self.arkindex_id is not None:
            return self.arkindex_id

        # Publish element without any link to an image
        logger.debug(f"Creating {self.type} {self.label}…")

        self.arkindex_id = self.publish_element(
            arkindex_client, worker_run_id, corpus_id
        )

        # Publish METS ID as metadata for later reference
        if publish_metadata:
            create_metadata(
                arkindex_client, self.arkindex_id, self.metadata_list, worker_run_id
            )

        # Store arkindex reference in cache
        cache.set(cache_key, self.arkindex_id)


class RootMetsElement:
    def __init__(
        self,
        path: Path,
        iiif_base_url: str,
        iiif_prefix: str | None = None,
        dpi_x: int | None = None,
        dpi_y: int | None = None,
    ):
        self.files_mapping = {}
        """Mapping from file_ids (as defined in the METS) to tuple of
        - path to ALTO xml file,
        - Loaded Arkindex summary.
        """
        self.files_order = []
        """
        List of ordered local ALTO files path (as defined in the METS)
        """
        self.metadata_list = {}
        """
        Mapping from node ID (as defined in the METS) to list of Arkindex metadata
        """

        with path.open() as file:
            # This ensures that comments in the XML files do not cause the
            # "no Alto namespace found" exception.
            parser = ET.XMLParser(remove_comments=True)
            tree = objectify.parse(file, parser=parser)
            self.root = tree.getroot()

        self.namespaces = {
            **METS_NS,
            # Empty namespace prefixes are not supported in XPath
            **{name or "mets": ns for name, ns in self.root.nsmap.items()},
        }

        self.iiif_base_url = iiif_base_url
        self.iiif_prefix = iiif_prefix
        self.dpi_x = dpi_x
        self.dpi_y = dpi_y

        self.parse_files(path)
        self.parse_metadata()

    def parse_files(self, toc_file: Path):
        """
        Parse files listed in the METS file section,
        and extract its immediate child FLocat path
        and build a relevant high-level class to use the content of
        - remote images
        - local Alto file
        """
        # Iterate over <file> in any <filesec>
        for file in self.root.xpath(
            "./mets:fileSec/mets:fileGrp/mets:file", namespaces=self.namespaces
        ):
            location = file.find("mets:FLocat", namespaces=self.namespaces)
            if location is None:
                logger.error(
                    f"Could not find location of file ({file.get('ID')}) in METS."
                )
                raise UploadProcessingError

            href = location.get("{" + self.namespaces["xlink"] + "}href")

            # Only support local files for now
            if href.startswith("file://"):
                href = href[7:]
            file_path = (toc_file.parent / href).resolve()

            mime_type = file.attrib.get("MIMETYPE")

            # Build IIIF image using local path to an image (even when not present)
            if (
                mime_type and mime_type.startswith("image/")
            ) or file_path.suffix.lower() in IMAGE_SUFFIXES:
                relpath = str(file_path.relative_to(toc_file.parent.resolve()))
                self.files_mapping[file.attrib["ID"]] = MetsImage(
                    relpath,
                    self.iiif_base_url,
                    self.iiif_prefix,
                )

            # Local Alto file
            elif (
                mime_type and mime_type == "text/xml"
            ) or file_path.suffix.lower() in ALTO_SUFFIXES:
                self.files_mapping[file.attrib["ID"]] = MetsAlto(
                    file_path, self.dpi_x, self.dpi_y
                )
                self.files_order.append(file_path)

            else:
                logger.warning(f"Unsupported file {file_path}")

    def parse_metadata(self):
        """
        Parse metadata and store them with the corresponding node ID
        """

        def build_metadata(node: ET._Element) -> dict:
            # Name without namespace
            name = ET.QName(node).localname

            # If has `xsi:type` attribute, use it instead
            name = (
                subname
                if (subname := node.attrib.get(f"{{{self.namespaces['xsi']}}}type"))
                else name.capitalize()
            )

            # Value
            value = node.text.strip()

            return {
                "type": get_metadata_type(value),
                "name": name.strip(),
                "value": value,
            }

        # Iterate over <dmdSec> with <mdWrap> child with a `MDTYPE="DC"` attribute
        for dmdSec in self.root.xpath(
            './/mets:mdWrap[@MDTYPE="DC"]/parent::mets:dmdSec',
            namespaces=self.namespaces,
        ):
            node_id = dmdSec.attrib.get("ID")
            if not node_id:
                continue

            self.metadata_list = AltoMetadata(
                target="DMDID",
                metadata_list={
                    node_id: list(
                        filter(
                            itemgetter("value"),
                            map(
                                build_metadata,
                                dmdSec.xpath(".//dc:*", namespaces=self.namespaces),
                            ),
                        )
                    )
                },
            )

    def list_required_types(self):
        # each <div> with a type will generate a new arkindex element
        return set(
            self.root.xpath(
                "./mets:structMap//mets:div/@TYPE", namespaces=self.namespaces
            )
        )

    def publish_alto(
        self,
        arkindex_client: ArkindexClient,
        parent_id: UUID,
        worker_run_id: UUID,
        corpus_id: str | None = None,
        publish_metadata: bool = True,
        ignore_types: list[str] = [],
    ):
        for alto_file in self.files_order:
            upload_alto_file(
                path=alto_file,
                client=arkindex_client,
                iiif_base_url=self.iiif_base_url,
                corpus={"id": corpus_id} if corpus_id else {},
                parent_id=parent_id,
                types_dict=None,
                create_types=True,
                ignore_types=ignore_types,
                dpi_x=self.dpi_x,
                dpi_y=self.dpi_y,
                gallica=False,
                folders_ark_id_dict=None,
                alto_namespace=None,
                worker_run_id=worker_run_id,
                skip_metadata=not publish_metadata,
            )

    @save_cache
    def publish(
        self,
        cache: Cache,
        arkindex_client: ArkindexClient,
        parent_id: UUID,
        worker_run_id: UUID,
        corpus_id: str | None = None,
        publish_metadata: bool = True,
        ignore_types: list[str] = [],
    ):
        """Build the hierarchy on Arkindex, browsing the tree in a breadth-first fashion

        :param arkindex_client: Arkindex API client.
        :param parent_id: Root element id on Arkindex.
        :param corpus_id: ID of the corpus where the element will be created
        """
        # Mock top element as it's already present in Arkindex and
        # has no real presence in the METS file
        top = MetsElement(None)
        top.arkindex_id = parent_id

        # Find all structure maps and process their children
        for div in self.root.xpath(
            "./mets:structMap/mets:div", namespaces=self.namespaces
        ):
            # Convert XML node to MetsElement, linked to our top element
            element = MetsElement(div, parent=top)
            logger.debug(f"Build {element.type} {element.id}: {element.label}")

            self.publish_element(
                cache,
                arkindex_client,
                element,
                worker_run_id,
                corpus_id,
                publish_metadata,
                ignore_types,
            )

    def publish_element(
        self,
        cache: Cache,
        arkindex_client: ArkindexClient,
        element: MetsElement,
        worker_run_id: UUID,
        corpus_id: str | None = None,
        publish_metadata: bool = True,
        ignore_types: list[str] = [],
    ):
        """
        Recursive method that process a METS structural node
        and publishes relevant parts on Arkindex (image or elements)
        """
        if element.type in ignore_types:
            return

        # Create a placeholder element
        element.metadata_list.extend(self.metadata_list.get_metadata_list(element.node))
        element.publish(
            cache, arkindex_client, worker_run_id, corpus_id, publish_metadata
        )

        # Simple discovery algo where we only remember the first alto & image found
        data, images = [], []

        def add_image(mets_image: MetsImage) -> None:
            """
            Only add a MetsImage to the image list if it is not already there
            """
            existing_image = next(
                (image for image in images if image.url == mets_image.url), None
            )
            if not existing_image:
                images.append(mets_image)

        for area in element.node.findall(
            "./mets:fptr//mets:area", namespaces=self.namespaces
        ):
            file = self.files_mapping.get(area.attrib["FILEID"])
            if file is None:
                continue
            if isinstance(file, MetsAlto):
                alto = file
                alto_begin = area.attrib.get("BEGIN")
                data.append((alto, alto_begin))
                # Add linked image
                if file.root.file_identifier:
                    add_image(
                        MetsImage(
                            image_relative_path=file.root.file_identifier,
                            iiif_base_url=self.iiif_base_url,
                            iiif_prefix=self.iiif_prefix,
                        )
                    )
            elif isinstance(file, MetsImage):
                add_image(file)

        image = None
        if images:
            # There should be only one image
            if len(images) != 1:
                logger.error("Found several images")
                raise UploadProcessingError
            image = images.pop()

        for alto, alto_begin in data:
            # Parse then publish on Arkindex
            alto.parse(alto_begin)

            # Publish IIIF image
            if image:
                image.publish(cache, arkindex_client)

            # Store arkindex id on element
            alto.publish(
                arkindex_client,
                worker_run_id,
                element.arkindex_id,
                corpus_id,
                image,
                publish_metadata,
                ignore_types,
            )

        # Recursion
        for child in element.node.findall("./mets:div", namespaces=self.namespaces):
            child_element = MetsElement(child, parent=element)
            self.publish_element(
                cache,
                arkindex_client,
                child_element,
                worker_run_id,
                corpus_id,
                publish_metadata,
                ignore_types,
            )
