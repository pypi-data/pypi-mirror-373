from pathlib import Path
from uuid import UUID

import pytest

from arkindex_cli.commands.utils import configuration_parser
from teklia_toolbox.config import ConfigurationError


@pytest.mark.parametrize(
    "config_file,error_message",
    [
        (
            "no_name.yml",
            '{"workers": {"name": "This option is required"}, "models": {"name": "This option is required"}}',
        ),
        ("no_slug.yml", '{"workers": {"slug": "This option is required"}}'),
        ("no_type.yml", '{"workers": {"type": "This option is required"}}'),
        ("no_path.yml", '{"models": {"path": "This option is required"}}'),
    ],
)
def test_required_fields(samples_dir, config_file, error_message):
    with pytest.raises(ConfigurationError, match=error_message):
        config_dir = samples_dir / "configuration/bad_configurations"
        parser = configuration_parser(config_dir)
        parser.parse(Path(config_dir) / config_file)


def test_parse_yaml_classic_config(samples_dir):
    """
    Parse the config of a configuration file
    """
    config_dir = samples_dir / "configuration/classic"
    parser = configuration_parser(config_dir)
    parsed_data = parser.parse(Path(config_dir) / ".arkindex.yml")

    assert parsed_data["workers"] == [
        {
            "name": "U-FCN Line Historical",
            "type": "dla",
            "slug": "ufcn_line_historical",
            "description": Path("path/to/file.md"),
            "model_usage": "required",
            "gpu_usage": "supported",
            "configuration": {
                "model": "line_historical.pth",
                "input_size": 768,
            },
            "user_configuration": {
                "classes": {"title": "Classes", "type": "list"},
                "min_cc": {"default": 50, "title": "Min_cc", "type": "int"},
            },
            "secrets": [],
            "docker": {
                "command": None,
                "shm_size": None,
            },
        },
        {
            "name": "U-FCN Line Madcat",
            "type": "dla",
            "slug": "ufcn_line_madcat",
            "description": None,
            "model_usage": "disabled",
            "gpu_usage": "disabled",
            "configuration": {
                "model": "line_madcat.pth",
                "input_size": 768,
            },
            "user_configuration": {},
            "secrets": [],
            "docker": {
                "command": None,
                "shm_size": None,
            },
        },
    ]

    assert parsed_data["models"] == [
        {
            "name": "U-FCN | Line Historical",
            "path": Path("path/to/model/dir"),
            "description": Path("path/to/file.md"),
            "tag": "official",
            "parent": UUID("cafecafe-cafe-cafe-cafe-cafecafecafe"),
            "configuration": {"input_size": 768},
        }
    ]


def test_parse_yaml_multiple_worker_configs(samples_dir):
    """
    Parse a config that links to another config file
    """
    # Read the config of the worker directly
    config_dir = samples_dir / "configuration/multiple_configs"
    parser = configuration_parser(config_dir)
    parsed_data = parser.parse(Path(config_dir) / "single.yml")
    assert parsed_data["workers"] == [
        {
            "name": "spaCy French",
            "slug": "spacy-fr",
            "type": "ner",
            "description": Path("path/to/file.md"),
            "model_usage": "disabled",
            "gpu_usage": "supported",
            "configuration": {"model": "fr_model", "lang": "fr"},
            "user_configuration": {},
            "secrets": [],
            "docker": {
                "command": None,
                "shm_size": None,
            },
        }
    ]
    assert parsed_data["models"] == [
        {
            "name": "spaCy | French",
            "path": Path("path/to/model/dir"),
            "description": Path("path/to/file.md"),
            "tag": "official",
            "parent": UUID("cafecafe-cafe-cafe-cafe-cafecafecafe"),
            "configuration": {"lang": "fr"},
        }
    ]

    # Read the config that links to the single worker's config
    parsed_data = parser.parse(Path(config_dir) / ".arkindex.yml")
    # We should have the same result
    assert parsed_data["workers"] == [
        {
            "name": "spaCy French",
            "slug": "spacy-fr",
            "type": "ner",
            "description": Path("path/to/file.md"),
            "model_usage": "disabled",
            "gpu_usage": "supported",
            "configuration": {"model": "fr_model", "lang": "fr"},
            "user_configuration": {},
            "secrets": [],
            "docker": {
                "command": None,
                "shm_size": None,
            },
        }
    ]
    assert parsed_data["models"] == [
        {
            "name": "spaCy | French",
            "path": Path("path/to/model/dir"),
            "description": Path("path/to/file.md"),
            "tag": "official",
            "parent": UUID("cafecafe-cafe-cafe-cafe-cafecafecafe"),
            "configuration": {"lang": "fr"},
        }
    ]
