from arkindex_cli.commands.models.publish import add_publish_parser


def add_models_parser(subcommands) -> None:
    publish_parser = subcommands.add_parser(
        "models",
        description="Process ML models",
        help="Process ML models",
    )

    subparsers = publish_parser.add_subparsers()
    add_publish_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        publish_parser.error("A subcommand is required.")

    publish_parser.set_defaults(func=subcommand_required)
