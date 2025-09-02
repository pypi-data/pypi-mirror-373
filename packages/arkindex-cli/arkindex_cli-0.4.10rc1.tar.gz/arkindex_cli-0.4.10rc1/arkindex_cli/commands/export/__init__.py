from pathlib import Path

from arkindex_cli.commands.export.alto import add_alto_parser
from arkindex_cli.commands.export.csv import add_csv_parser
from arkindex_cli.commands.export.docx import add_docx_parser
from arkindex_cli.commands.export.entities import add_entities_parser
from arkindex_cli.commands.export.pagexml import add_pagexml_parser
from arkindex_cli.commands.export.pdf import add_pdf_parser


def add_export_parser(subcommands) -> None:
    export_parser = subcommands.add_parser(
        "export",
        description="Export elements from an exported SQLite database to other formats.",
        help="Export elements from an exported SQLite database to other formats.",
    )
    export_parser.add_argument(
        "database_path",
        type=Path,
        help="Path to the SQLite database exported from an Arkindex instance.",
    )

    subparsers = export_parser.add_subparsers()
    add_pdf_parser(subparsers)
    add_alto_parser(subparsers)
    add_csv_parser(subparsers)
    add_entities_parser(subparsers)
    add_docx_parser(subparsers)
    add_pagexml_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        export_parser.error("A subcommand is required.")

    export_parser.set_defaults(func=subcommand_required)
