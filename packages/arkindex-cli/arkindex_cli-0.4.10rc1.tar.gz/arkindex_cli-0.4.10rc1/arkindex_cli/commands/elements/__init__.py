from arkindex_cli.commands.elements.link import add_linking_parser
from arkindex_cli.commands.elements.ml_splits import add_splits_parser
from arkindex_cli.commands.elements.page_copy import add_page_copy_parser
from arkindex_cli.commands.elements.reject_classifications import (
    add_classification_rejection_parser,
)
from arkindex_cli.commands.elements.unlink import add_unlinking_parser


def add_elements_parser(subcommands) -> None:
    elements_parser = subcommands.add_parser(
        "elements",
        description="Manage elements",
        help="",
    )
    subparsers = elements_parser.add_subparsers()
    add_linking_parser(subparsers)
    add_unlinking_parser(subparsers)
    add_page_copy_parser(subparsers)
    add_classification_rejection_parser(subparsers)
    add_splits_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        elements_parser.error("A subcommand is required.")

    elements_parser.set_defaults(func=subcommand_required)
