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


class RejectClassifications:
    """
    If the classification is of manual origin, it will be deleted.
    If the classification comes from a worker, it will be marked as rejected.
    """

    def __init__(
        self,
        profile_slug: str | None = None,
        gitlab_secure_file: Path | None = None,
        **kwargs,
    ):
        self.element_ids = kwargs.get("element")
        self.uuids_file = kwargs.get("uuid_list")
        self.use_selection = kwargs.get("selection")
        self.classes_to_reject = kwargs.get("classes")
        self.reject_all_classes = kwargs.get("all")

        profiles = Profiles(gitlab_secure_file)
        self.api_client = profiles.get_api_client_or_exit(profile_slug)

    def reject_classifications(self, element, element_classifications):
        if self.classes_to_reject:
            to_reject = [
                classification
                for classification in element_classifications
                if classification["ml_class"]["name"] in self.classes_to_reject
            ]
        else:
            to_reject = element_classifications
        if len(to_reject) == 0:
            logger.warning(
                f"Element {element['id']} has no classifications, or none with the specified name(s)."
            )
        for one_classification in to_reject:
            body = {
                "ml_class": {"name": one_classification["ml_class"]["name"]},
                "state": "rejected",
            }
            try:
                self.api_client.request(
                    "RejectClassification", id=one_classification["id"], body=body
                )
                logger.info(
                    f"Classification {one_classification['ml_class']['name']} {'rejected' if one_classification['worker_version'] else 'deleted'} from element {element['id']}!"
                )
            except ErrorResponse as e:
                logger.error(
                    f"Failed to reject classification {one_classification['ml_class']['name']} on element {element['id']}: {e.status_code} - {e.content}."
                )

    def retrieve_classifications(self, element):
        element_classifications = self.api_client.request(
            "RetrieveElement", id=element["id"]
        )["classifications"]
        return element_classifications

    def run(self):
        logger.info(
            "Manual classifications will be deleted; classifications created by a worker will be marked as 'rejected' but not deleted."
        )
        target_elements = retrieve_elements(
            self.api_client,
            elements=self.element_ids,
            uuid_list=self.uuids_file,
            selection=self.use_selection,
        )
        for one_element in target_elements:
            element_classifications = self.retrieve_classifications(one_element)
            self.reject_classifications(one_element, element_classifications)


def add_classification_rejection_parser(subcommands):
    class_rejection_parser = subcommands.add_parser(
        "reject-classifications",
        description="Reject/remove one or more classifications from elements.",
        help="",
    )
    target_elements = class_rejection_parser.add_mutually_exclusive_group(required=True)
    target_elements.add_argument(
        "--element",
        help="One or more element UUID(s) to reject/remove classification(s) from.",
        nargs="+",
        type=UUID,
    )
    target_elements.add_argument(
        "--uuid-list", help="Path to a list of element UUIDs, one per line."
    )
    target_elements.add_argument(
        "--selection",
        help="Reject/remove classification(s) from the elements in the selection on Arkindex.",
        action="store_true",
    )
    target_classes = class_rejection_parser.add_mutually_exclusive_group(required=True)
    target_classes.add_argument(
        "--all",
        help="Reject/remove all classifications from the target element(s).",
        action="store_true",
    )
    target_classes.add_argument(
        "--classes",
        help="One or more class name(s).",
        nargs="+",
    )
    class_rejection_parser.set_defaults(func=run)


def run(
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
    **kwargs,
):
    RejectClassifications(profile_slug, gitlab_secure_file, **kwargs).run()
