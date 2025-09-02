from arkindex_cli.commands.upload.alto import add_alto_parser
from arkindex_cli.commands.upload.data_file import add_data_file_parser
from arkindex_cli.commands.upload.iiif import add_iiif_parser
from arkindex_cli.commands.upload.mets import add_mets_parser
from arkindex_cli.commands.upload.minio_client import add_minio_client_parser
from arkindex_cli.commands.upload.model_version import add_model_version_parser
from arkindex_cli.commands.upload.page_xml_import import add_pagexml_import_parser


def add_upload_parser(subcommands) -> None:
    upload_parser = subcommands.add_parser(
        "upload",
        description="Upload data to Arkindex",
        help="Upload data to Arkindex",
    )
    subparsers = upload_parser.add_subparsers()
    add_iiif_parser(subparsers)
    add_minio_client_parser(subparsers)
    add_pagexml_import_parser(subparsers)
    add_alto_parser(subparsers)
    add_mets_parser(subparsers)
    add_data_file_parser(subparsers)
    add_model_version_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        upload_parser.error("A subcommand is required.")

    upload_parser.set_defaults(func=subcommand_required)
