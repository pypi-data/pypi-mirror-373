from arkindex_cli.commands.worker.import_worker import add_import_parser
from arkindex_cli.commands.worker.publish import add_publish_parser


def add_worker_parser(subcommands) -> None:
    export_parser = subcommands.add_parser(
        "worker",
        description="Manage workers and their versions.",
        help="Manage workers and their versions.",
    )
    subparsers = export_parser.add_subparsers()
    add_import_parser(subparsers)
    add_publish_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        export_parser.error("A subcommand is required.")

    export_parser.set_defaults(func=subcommand_required)
