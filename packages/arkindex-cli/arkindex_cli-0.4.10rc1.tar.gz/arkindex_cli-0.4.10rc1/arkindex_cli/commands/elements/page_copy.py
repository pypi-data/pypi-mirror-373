import logging
from pathlib import Path
from uuid import UUID

from arkindex.exceptions import ErrorResponse

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.elements.utils import retrieve_elements

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s/%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class PageCopier:
    """
    Copy a page, without any of its children, to a folder element.
    This does not link an existing page element to a new parent, but creates
    a new page element from the same image.
    Technically not a copy.
    """

    def __init__(
        self,
        profile_slug: str | None = None,
        gitlab_secure_file: Path | None = None,
        **kwargs,
    ):
        self.parent_element = kwargs.get("folder")
        self.page_ids = kwargs.get("pages")
        self.uuids_file = kwargs.get("uuid_list")
        self.use_selection = kwargs.get("selection")

        profiles = Profiles(gitlab_secure_file)
        self.api_client = profiles.get_api_client_or_exit(profile_slug)

    def get_parent_folder(self):
        try:
            element_info = self.api_client.request(
                "RetrieveElement", id=self.parent_element
            )
        except ErrorResponse as e:
            if e.status_code == 404:
                raise Exception(
                    f"Parent element {self.parent_element} does not exist. Check the UUID."
                ) from None
            else:
                raise
        # check that the element is a folder-type element
        element_corpus = element_info["corpus"]["id"]
        corpus_folders = [
            element_type["slug"]
            for element_type in self.api_client.request(
                "RetrieveCorpus", id=element_corpus
            )["types"]
            if element_type["folder"] is True
        ]
        assert (
            element_info["type"] in corpus_folders
        ), f"Element {element_info['name']} of type {element_info['type']} is not a folder."
        logger.info(
            f"Copying page elements to {element_info['type']} {element_info['name']}."
        )
        return element_info

    def copy_pages(self, target, pages):
        successful = 0
        corpus = target["corpus"]["id"]
        parent = target["id"]
        for one_page in pages:
            body = {
                "type": one_page["type"],
                "name": one_page["name"],
                "image": one_page["zone"]["image"]["id"],
                "corpus": corpus,
                "parent": parent,
            }
            try:
                self.api_client.request("CreateElement", body=body, slim_output=True)
                successful += 1
            except ErrorResponse as e:
                logger.error(
                    f"Failed to copy page {one_page['id']} to {target['type']} {target['name']}: {e.status_code} - {e.content}."
                )
        return successful

    def run(self):
        target = self.get_parent_folder()
        pages_list = retrieve_elements(
            self.api_client,
            elements=self.page_ids,
            uuid_list=self.uuids_file,
            selection=self.use_selection,
            element_type="page",
        )
        copied_pages = self.copy_pages(target, pages_list)
        logger.info(
            f"Copied {copied_pages} (out of {len(pages_list)}) page(s) to {target['type']} {target['name']}."
        )


def add_page_copy_parser(subcommands):
    page_copy_parser = subcommands.add_parser(
        "page-copy",
        description="Copy page elements (without children or transcriptions, only the page is copied) to another folder element.",
        help="Make a blank copy of one or more page element(s), from a single UUUID, a list or the selection on Arkindex, to another folder, inside or outside their original corpus.",
    )
    page_copy_parser.add_argument(
        "--folder",
        help="UUID of an existing folder element to copy the pages to.",
        type=UUID,
        required=True,
    )
    pages = page_copy_parser.add_mutually_exclusive_group(required=True)
    pages.add_argument(
        "--pages", help="One or more page UUID(s).", nargs="+", type=UUID
    )
    pages.add_argument(
        "--selection",
        help="Retrieve page elements from the user's selection on Arkindex.",
        action="store_true",
    )
    pages.add_argument(
        "--uuid-list",
        help="Path to a file containing a list of page UUIDs, one per line.",
        type=Path,
    )
    page_copy_parser.set_defaults(func=run)


def run(
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
    **kwargs,
):
    PageCopier(profile_slug, gitlab_secure_file, **kwargs).run()
