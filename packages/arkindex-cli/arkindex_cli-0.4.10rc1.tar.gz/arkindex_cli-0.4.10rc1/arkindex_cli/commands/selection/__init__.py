from arkindex_cli.commands.selection.populate import add_import_parser


def add_selection_parser(subcommands) -> None:
    selection_parser = subcommands.add_parser(
        "selection",
        description="Manage selection",
        help="Manage selection",
    )
    subparsers = selection_parser.add_subparsers()
    add_import_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        selection_parser.error("A subcommand is required.")

    selection_parser.set_defaults(func=subcommand_required)
