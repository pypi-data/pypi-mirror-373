import glob
import logging
import os
import re
from enum import Enum
from functools import partial
from pathlib import Path
from uuid import UUID

from teklia_toolbox.config import ConfigParser

SHM_SIZE_PATTERN = re.compile(r"^[0-9]+[bkmgBKMG]?$")

logger = logging.getLogger(__name__)


def shm_size_validator(value):
    str_value = str(value)
    assert re.match(
        SHM_SIZE_PATTERN, str_value
    ), f"{str_value} is not a valid value for shm_size"
    if str_value.isdigit():
        assert int(str_value) > 0, "shm_size value must be greater than 0"
    else:
        assert int(str_value[:-1]) > 0, "shm_size value must be greater than 0"
    return value


class FeatureUsage(Enum):
    Disabled = "disabled"
    Supported = "supported"
    Required = "required"


def worker_configuration_parser():
    """
    Configure YAML parser for the Worker ML configuration
    """
    worker_parser = ConfigParser()
    worker_parser.add_option("name", type=str)
    worker_parser.add_option("slug", type=str)
    worker_parser.add_option("type", type=str)
    worker_parser.add_option("description", type=Path, default=None)
    worker_parser.add_option("gpu_usage", type=str, default=FeatureUsage.Disabled.value)
    worker_parser.add_option(
        "model_usage", type=str, default=FeatureUsage.Disabled.value
    )
    worker_parser.add_option("configuration", type=dict, default={})
    worker_parser.add_option("user_configuration", type=dict, default={})
    worker_parser.add_option("secrets", type=list, default=[])

    docker_parser = worker_parser.add_subparser("docker", default={})
    docker_parser.add_option("command", type=str, default=None)
    docker_parser.add_option("shm_size", type=shm_size_validator, default=None)

    return worker_parser


def model_configuration_parser():
    """
    Configure YAML parser for the Model ML configuration
    """
    model_parser = ConfigParser()
    model_parser.add_option("name", type=str)
    model_parser.add_option("path", type=Path)
    model_parser.add_option("description", type=Path, default=None)
    model_parser.add_option("tag", type=str, default=None)
    model_parser.add_option("parent", type=UUID, default=None)
    model_parser.add_option("configuration", type=dict, default={})

    return model_parser


def configuration_parser(base_dir):
    """
    Configure YAML parser for the .arkindex.yml configuration
    """

    parser = ConfigParser()
    parser.add_option("version", type=int)

    def subparser_validator(entries, subparser):
        entries_list = []
        for entry in entries:
            # Workers config are inside other YAML files
            if not isinstance(entry, dict):
                entries_sublist = [
                    subparser.parse(Path(entry_path))
                    for entry_path in glob.glob(
                        os.path.join(base_dir, entry), recursive=True
                    )
                ]
                entries_list.extend(entries_sublist)
            # Worker config is stocked in global configuration dict directly
            else:
                entries_list.append(subparser.parse_data(entry))

        return entries_list

    # Worker parser
    parser.add_option(
        "workers",
        type=partial(subparser_validator, subparser=worker_configuration_parser()),
        default=[],
    )

    # Model parser
    parser.add_option(
        "models",
        type=partial(subparser_validator, subparser=model_configuration_parser()),
        default=[],
    )

    return parser


def parse_config(path):
    """Parse .arkindex.yml and retrieve each workers data"""
    configuration_file = Path(path) / ".arkindex.yml"
    try:
        parser = configuration_parser(path)
        workers = parser.parse(configuration_file)
    except Exception as exc:
        msg = getattr(exc, "content", repr(exc))
        logger.error(f"Failed parsing the .arkindex.yml configuration file: {msg}.")
        raise

    return workers
