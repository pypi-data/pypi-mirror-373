import argparse
import json
import tempfile
from pathlib import Path

import pytest

from arkindex_cli.commands.export import add_export_parser
from arkindex_cli.commands.export.csv import (
    build_csv_header,
    classes_columns,
    element_classes,
    element_dict,
    element_entities,
    element_metadata,
    element_row,
    entity_type_columns,
    get_elements,
    metadata_columns,
    run,
)
from arkindex_cli.commands.export.utils import MANUAL_SOURCE
from arkindex_export import Element, Image, open_database
from peewee import JOIN
from playhouse.test_utils import assert_query_count

DB_PATH = Path("/path/to/db.sqlite")
FAKE_DATE = "2023-07-25T15:27:31.893647+00:00"


@pytest.fixture
def mock_db_path(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)


@pytest.mark.parametrize(
    "arguments,message",
    [
        (
            ["export", "/path/to/db.sqlite", "csv", "--parent", "bob"],
            "--parent: invalid UUID value: 'bob'",
        ),
        (
            [
                "export",
                "/path/to/db.sqlite",
                "csv",
                "--classification-worker-version",
                "bob",
            ],
            "--classification-worker-version: invalid uuid_or_manual value: 'bob'",
        ),
        (
            ["export", "/path/to/db.sqlite", "csv", "--entities-worker-version", "bob"],
            "--entities-worker-version: invalid uuid_or_manual value: 'bob'",
        ),
    ],
)
def test_command_arguments_errors(capsys, mock_db_path, arguments, message):
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(metavar="subcommand")
    add_export_parser(subcommands)
    with pytest.raises(SystemExit):
        parser.parse_args(arguments)
    out, err = capsys.readouterr()
    assert message in str(err)


@pytest.mark.parametrize(
    "arguments,exception,message",
    [
        (
            {"recursive": True},
            AssertionError,
            "The recursive option can only be used if a parent_element is given. If no parent_element is specified, element listing is recursive by default.",
        ),
        (
            {"with_parent_metadata": True},
            AssertionError,
            "The --with-parent-metadata option can only be used if --with-metadata is set.",
        ),
        (
            {"entities_worker_version": "b2d11bdd-2a6c-4a55-83ee-1bd2fa92989e"},
            AssertionError,
            "The --entities-worker-version option can only be used if --with-entities is set.",
        ),
    ],
)
def test_run_arguments_errors(mock_db_path, arguments, exception, message):
    with pytest.raises(exception) as e:
        run(DB_PATH, output_path=Path("/tmp/elements.csv"), **arguments)
    assert message in str(e.value)


def test_get_elements(export_db_path):
    open_database(export_db_path)
    with assert_query_count(1):
        elements = list(get_elements())
    assert elements == list(Element.select())


def test_get_elements_type_filter(export_db_path):
    open_database(export_db_path)
    with assert_query_count(1):
        elements = list(get_elements(element_type="text_line"))
    assert elements == list(Element.select().where(Element.type == "text_line"))


@pytest.mark.parametrize(
    "options,element_names",
    [
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"},
            ["testname2", "testname5", "testname6", "testname8"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            [
                "testname10",
                "testname11",
                "testname12",
                "testname2",
                "testname3",
                "testname5",
                "testname6",
                "testname7",
                "testname8",
                "testname9",
            ],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            ["testname2"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            [
                "testname10",
                "testname11",
                "testname12",
                "testname3",
                "testname9",
            ],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            [],
        ),
    ],
)
def test_get_elements_parent_recursive_type_options(
    export_db_path, options, element_names
):
    open_database(export_db_path)
    with assert_query_count(1):
        retrieved_element_names = list(
            item.name for item in get_elements(**options).order_by(Element.name)
        )
    assert retrieved_element_names == element_names


@pytest.mark.parametrize(
    "element_options,classification_worker_id,columns",
    [
        (
            {},
            None,
            [
                "bretzel",
                "croissant",
                "kougelhopf",
                "pain aux raisins",
                "pain aux raisins",
            ],
        ),
        ({}, MANUAL_SOURCE, ["croissant", "kougelhopf", "pain aux raisins"]),
        ({}, "worker_id1", ["bretzel", "kougelhopf", "pain aux raisins"]),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"},
            None,
            ["bretzel", "kougelhopf", "pain aux raisins", "pain aux raisins"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"},
            MANUAL_SOURCE,
            ["pain aux raisins"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"},
            "worker_id1",
            ["bretzel", "kougelhopf", "pain aux raisins"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            None,
            [
                "bretzel",
                "croissant",
                "kougelhopf",
                "pain aux raisins",
                "pain aux raisins",
            ],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            MANUAL_SOURCE,
            ["croissant", "kougelhopf", "pain aux raisins"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            "worker_id1",
            ["bretzel", "kougelhopf", "pain aux raisins"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            None,
            ["bretzel"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            MANUAL_SOURCE,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            "worker_id1",
            ["bretzel"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            None,
            ["croissant", "kougelhopf"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            MANUAL_SOURCE,
            ["croissant", "kougelhopf"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            "worker_id1",
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            None,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            MANUAL_SOURCE,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            "worker_id1",
            [],
        ),
    ],
)
def test_classes_columns(
    export_db_path, element_options, classification_worker_id, columns
):
    open_database(export_db_path)
    elements = get_elements(**element_options)
    with assert_query_count(1):
        cl_columns = classes_columns(
            elements=elements, classification_worker_version=classification_worker_id
        )
    assert cl_columns == columns


@pytest.mark.parametrize(
    "element_id,classification_worker_version,results",
    [
        ("7791f6a1-fdbb-4ed1-b03d-10d56fc87641", None, ["kougelhopf", "croissant"]),
        (
            "7791f6a1-fdbb-4ed1-b03d-10d56fc87641",
            MANUAL_SOURCE,
            ["kougelhopf", "croissant"],
        ),
        ("7791f6a1-fdbb-4ed1-b03d-10d56fc87641", "worker_id1", []),
        ("7791f6a1-fdbb-4ed1-b03d-10d56fc87641", "worker_id2", []),
        ("b6f57a29-7260-410a-8d21-6633bae6842c", None, ["croissant"]),
        ("b6f57a29-7260-410a-8d21-6633bae6842c", MANUAL_SOURCE, []),
        ("b6f57a29-7260-410a-8d21-6633bae6842c", "worker_id1", []),
        ("b6f57a29-7260-410a-8d21-6633bae6842c", "worker_id2", ["croissant"]),
    ],
)
def test_element_classes(
    export_db_path, element_id, classification_worker_version, results
):
    open_database(export_db_path)
    with assert_query_count(1):
        el_classes = list(
            item.class_name
            for item in element_classes(
                element_id=element_id,
                classification_worker_version=classification_worker_version,
            )
        )
    assert el_classes == results


@pytest.mark.parametrize(
    "element_options,load_parents,columns",
    [
        ({}, False, ["commander", "pilot", "unit"]),
        ({}, True, ["commander", "pilot", "pilot", "pilot", "unit", "unit"]),
        ({"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"}, False, ["commander"]),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"},
            True,
            ["commander", "pilot"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            False,
            ["commander", "pilot", "unit"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            True,
            ["commander", "pilot", "pilot", "pilot", "unit", "unit"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            False,
            ["commander"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            True,
            ["commander", "pilot"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            False,
            ["pilot", "unit"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            True,
            ["commander", "pilot", "pilot", "pilot", "unit", "unit"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            False,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            True,
            [],
        ),
    ],
)
def test_metadata_columns(export_db_path, element_options, load_parents, columns):
    open_database(export_db_path)
    elements = get_elements(**element_options)
    with assert_query_count(1):
        md_columns = metadata_columns(elements=elements, load_parents=load_parents)
    assert md_columns == columns


@pytest.mark.parametrize(
    "element_id,load_parents,results",
    [
        (
            "a87884d1-5233-4207-9b02-66bbe494da84",
            False,
            [("pilot", "ikari shinji"), ("unit", "01")],
        ),
        (
            "a87884d1-5233-4207-9b02-66bbe494da84",
            True,
            [
                ("commander", "ikari gendou"),
                ("pilot", "ikari shinji"),
                ("pilot", "soryu asuka langley"),
                ("unit", "01"),
            ],
        ),
    ],
)
def test_element_metadata(export_db_path, element_id, load_parents, results):
    open_database(export_db_path)
    with assert_query_count(1):
        el_metadata = list(
            (item.name, item.value)
            for item in element_metadata(
                element_id=element_id, load_parents=load_parents
            )
        )
    assert el_metadata == results


@pytest.mark.parametrize(
    "element_options,entity_worker_version,columns",
    [
        (
            {},
            None,
            [
                "entitytype1",
                "entitytype1",
                "entitytype2",
                "entitytype3",
            ],
        ),
        ({}, MANUAL_SOURCE, ["entitytype1", "entitytype2"]),
        ({}, "worker_id1", ["entitytype1", "entitytype2"]),
        ({"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"}, None, []),
        ({"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"}, MANUAL_SOURCE, []),
        ({"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c"}, "worker_id1", []),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            None,
            [
                "entitytype1",
                "entitytype1",
                "entitytype2",
                "entitytype3",
            ],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            MANUAL_SOURCE,
            ["entitytype1", "entitytype2"],
        ),
        (
            {"parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c", "recursive": True},
            "worker_id1",
            ["entitytype1", "entitytype2"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            None,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            MANUAL_SOURCE,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "folder",
            },
            "worker_id1",
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            None,
            ["entitytype1", "entitytype2", "entitytype3"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            MANUAL_SOURCE,
            ["entitytype1", "entitytype2"],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "recursive": True,
                "element_type": "text_line",
            },
            "worker_id1",
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            None,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            MANUAL_SOURCE,
            [],
        ),
        (
            {
                "parent_id": "b6f57a29-7260-410a-8d21-6633bae6842c",
                "element_type": "text_line",
            },
            "worker_id1",
            [],
        ),
    ],
)
def test_entity_type_columns(
    export_db_path, element_options, entity_worker_version, columns
):
    """
    ELEMENT ENTITIES STRUCTURE

    a87884d1-5233-4207-9b02-66bbe494da84 [page]
    |•-- traid4 [transcription]
    |    •-- transcription [entitytype1]
    |    •-- page [entitytype2] {worker_id1}
    |    •-- page [entitytype1] {worker_id1}
    |__ b53a8dbd-3135-4540-87f0-e08a9a396e11 [text_line]
    |   |•-- traid1 [transcription]
    |   |    •-- transcription [entitytype1]
    |   |__ 1cd4c304-46e1-497a-a92e-d4d25ab1cd91 [text_line]
    |       |•-- traid3 [transcription]
    |__ ccc04dfe-39af-4118-bb56-3aaf0350ba8b [text_line]
        |•-- traid2 [transcription]
        |    •-- page [entitytype1] {worker_id2}
        |•-- traid6 [transcription]
        |    •-- page [entitytype2]
        |__ 7605faf7-b316-423e-b2c1-b6d845dba4bd [text_line]
            |•-- traid5 [transcription]
                 •-- entityname4 [entitytype3] {worker_id2}
    """
    open_database(export_db_path)
    elements = get_elements(**element_options)
    with assert_query_count(1):
        entity_columns = entity_type_columns(
            elements=elements, entities_worker_version=entity_worker_version
        )
    assert entity_columns == columns


@pytest.mark.parametrize(
    "element_id,entities_worker_version,results",
    [
        (
            "a87884d1-5233-4207-9b02-66bbe494da84",
            None,
            [
                ("entitytype1", "transcription"),
                ("entitytype1", "page"),
                ("entitytype2", "page"),
            ],
        ),
        (
            "a87884d1-5233-4207-9b02-66bbe494da84",
            MANUAL_SOURCE,
            [("entitytype1", "transcription")],
        ),
        (
            "a87884d1-5233-4207-9b02-66bbe494da84",
            "worker_id1",
            [("entitytype1", "page"), ("entitytype2", "page")],
        ),
        ("a87884d1-5233-4207-9b02-66bbe494da84", "worker_id2", []),
    ],
)
def test_element_entities(export_db_path, element_id, entities_worker_version, results):
    """
    ELEMENT ENTITIES STRUCTURE

    a87884d1-5233-4207-9b02-66bbe494da84 [page]
    |•-- traid4 [transcription]
    |    •-- transcription [entitytype1]
    |    •-- page [entitytype2] {worker_id1}
    |    •-- page [entitytype1] {worker_id1}
    |__ b53a8dbd-3135-4540-87f0-e08a9a396e11 [text_line]
    |   |•-- traid1 [transcription]
    |   |    •-- transcription [entitytype1]
    |   |__ 1cd4c304-46e1-497a-a92e-d4d25ab1cd91 [text_line]
    |       |•-- traid3 [transcription]
    |__ ccc04dfe-39af-4118-bb56-3aaf0350ba8b [text_line]
        |•-- traid2 [transcription]
        |    •-- page [entitytype1] {worker_id2}
        |•-- traid6 [transcription]
        |    •-- page [entitytype2]
        |__ 7605faf7-b316-423e-b2c1-b6d845dba4bd [text_line]
            |•-- traid5 [transcription]
                 •-- entityname4 [entitytype3] {worker_id2}
    """
    open_database(export_db_path)
    with assert_query_count(1):
        el_entities = list(
            (item.type_name, item.name)
            for item in element_entities(
                element_id=element_id, entities_worker_version=entities_worker_version
            )
        )
    assert el_entities == results


@pytest.mark.parametrize(
    "with_classes,with_metadata,with_entities,additional_info,csv_header",
    [
        (
            False,
            False,
            False,
            [[], [], []],
            [
                "id",
                "name",
                "type",
                "image_id",
                "image_url",
                "rotation_angle",
                "polygon",
                "worker_version_id",
                "created",
            ],
        ),
        (
            True,
            False,
            False,
            [[None, 0.3, 1], [None, 1.0, None], [0.6, None, None]],
            [
                "id",
                "name",
                "type",
                "image_id",
                "image_url",
                "rotation_angle",
                "polygon",
                "worker_version_id",
                "created",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
            ],
        ),
        (
            True,
            True,
            False,
            [
                [None, None, None, 0.3, 1],
                ["ikari shinji", "01", None, 1.0, None],
                ["soryu asuka langley", None, 0.6, None, None],
            ],
            [
                "id",
                "name",
                "type",
                "image_id",
                "image_url",
                "rotation_angle",
                "polygon",
                "worker_version_id",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
            ],
        ),
        (
            True,
            True,
            True,
            [
                [None, None, None, 0.3, 1.0, None, None, None],
                [
                    "ikari shinji",
                    "01",
                    None,
                    1.0,
                    None,
                    "transcription",
                    "page",
                    "page",
                ],
                ["soryu asuka langley", None, 0.6, None, None, None, None, None],
            ],
            [
                "id",
                "name",
                "type",
                "image_id",
                "image_url",
                "rotation_angle",
                "polygon",
                "worker_version_id",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
                "entity_entitytype1",
                "entity_entitytype1",
                "entity_entitytype2",
            ],
        ),
    ],
)
def test_csv_row_and_header(
    export_db_path,
    with_classes,
    with_metadata,
    with_entities,
    additional_info,
    csv_header,
):
    elements = Element.filter(
        Element.id.in_(
            [
                "1edb51e5-217d-4d67-8768-39e7f0aca143",
                "a87884d1-5233-4207-9b02-66bbe494da84",
                "b6f57a29-7260-410a-8d21-6633bae6842c",
            ]
        )
    ).order_by(Element.id)
    elements = elements.select(Element, Image).join(
        Image, JOIN.LEFT_OUTER, on=[Image.id == Element.image_id]
    )

    open_database(export_db_path)

    cl_columns = classes_columns(elements) if with_classes else None
    md_columns = metadata_columns(elements) if with_metadata else None
    et_columns = entity_type_columns(elements) if with_entities else None

    header = build_csv_header(None, md_columns, cl_columns, et_columns)

    for i, element in enumerate(elements):
        elem_dict = element_dict(
            element,
            with_classes,
            with_metadata,
            False,
            with_entities,
            classes_columns=cl_columns,
            metadata_columns=md_columns,
            entity_type_columns=et_columns,
            classification_worker_version=None,
            entities_worker_version=None,
        )

        elem_row = element_row(elem_dict, header, cl_columns, md_columns, et_columns)

        assert len(elem_row) == len(header)
        assert header == csv_header
        assert (
            elem_row
            == [
                element.id,
                element.name,
                element.type,
                element.image_id,
                element.image.url if element.image else None,
                element.rotation_angle,
                element.polygon,
                element.worker_run.worker_version_id if element.worker_run_id else None,
                FAKE_DATE,
            ]
            + additional_info[i]
        )


@pytest.mark.parametrize(
    "with_classes,with_metadata,with_entities,fields,additional_info,csv_header",
    [
        (
            False,
            False,
            False,
            None,
            [[], [], []],
            [
                "id",
                "name",
                "type",
                "image_id",
                "image_url",
                "rotation_angle",
                "polygon",
                "worker_version_id",
                "created",
            ],
        ),
        (
            False,
            False,
            False,
            ["id", "name", "created"],
            [[], [], []],
            ["id", "name", "created"],
        ),
        (
            True,
            False,
            False,
            [
                "id",
                "name",
                "created",
                "classification_croissant",
                "classification_pain aux raisins",
            ],
            [[None, 0.3, 1], [None, 1.0, None], [0.6, None, None]],
            [
                "id",
                "name",
                "created",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
            ],
        ),
        (
            True,
            True,
            False,
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_pain aux raisins",
            ],
            [
                [None, None, 0.3, 1],
                ["ikari shinji", "01", 1.0, None],
                ["soryu asuka langley", None, None, None],
            ],
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
            ],
        ),
        (
            True,
            True,
            True,
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "entity_entitytype2",
            ],
            [
                [None, None, None, 0.3, 1.0, None],
                [
                    "ikari shinji",
                    "01",
                    None,
                    1.0,
                    None,
                    "page",
                ],
                ["soryu asuka langley", None, 0.6, None, None, None],
            ],
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
                "entity_entitytype2",
            ],
        ),
        (
            True,
            True,
            True,
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "entity_ent*",
            ],
            [
                [None, None, None, 0.3, 1.0, None, None, None],
                [
                    "ikari shinji",
                    "01",
                    None,
                    1.0,
                    None,
                    "transcription",
                    "page",
                    "page",
                ],
                ["soryu asuka langley", None, 0.6, None, None, None, None, None],
            ],
            [
                "id",
                "name",
                "created",
                "metadata_pilot",
                "metadata_unit",
                "classification_croissant",
                "classification_pain aux raisins",
                "classification_pain aux raisins",
                "entity_entitytype1",
                "entity_entitytype1",
                "entity_entitytype2",
            ],
        ),
    ],
)
def test_filter_header(
    export_db_path,
    fields,
    with_classes,
    with_metadata,
    with_entities,
    additional_info,
    csv_header,
):
    elements = Element.filter(
        Element.id.in_(
            [
                "1edb51e5-217d-4d67-8768-39e7f0aca143",
                "a87884d1-5233-4207-9b02-66bbe494da84",
                "b6f57a29-7260-410a-8d21-6633bae6842c",
            ]
        )
    ).order_by(Element.id)
    elements = elements.select(Element, Image).join(
        Image, JOIN.LEFT_OUTER, on=[Image.id == Element.image_id]
    )

    open_database(export_db_path)

    cl_columns = classes_columns(elements) if with_classes else None
    md_columns = metadata_columns(elements) if with_metadata else None
    et_columns = entity_type_columns(elements) if with_entities else None

    header = build_csv_header(fields, md_columns, cl_columns, et_columns)
    assert header == csv_header

    for i, element in enumerate(elements):
        elem_dict = element_dict(
            element,
            with_classes,
            with_metadata,
            False,
            with_entities,
            classes_columns=cl_columns,
            metadata_columns=md_columns,
            entity_type_columns=et_columns,
            classification_worker_version=None,
            entities_worker_version=None,
        )

        elem_row = element_row(elem_dict, header, cl_columns, md_columns, et_columns)

        if fields:
            assert (
                elem_row == [element.id, element.name, FAKE_DATE] + additional_info[i]
            )
        else:
            assert (
                elem_row
                == [
                    element.id,
                    element.name,
                    element.type,
                    element.image_id,
                    element.image.url if element.image else None,
                    element.rotation_angle,
                    element.polygon,
                    element.worker_run.worker_version_id
                    if element.worker_run_id
                    else None,
                    FAKE_DATE,
                ]
                + additional_info[i]
            )
        assert len(header) == len(elem_row)


@pytest.mark.parametrize(
    "transcriptions_worker_version, headers, expected_output",
    [
        (
            None,
            # Element "c0016dda-dfd9-486e-a19e-1e2785446e94" has 2 manual transcriptions
            # and transcriptions from 2 versions based on the same worker "worker_id1".
            ("manual", "manual", "worker_id1", "worker_id1", "worker_id2"),
            "sample_1",
        ),
        (
            "worker_id2",
            ("worker_id2",),
            "sample_2",
        ),
        (
            "manual",
            ("manual", "manual"),
            "sample_3",
        ),
        (
            "worker_id_not_existing",
            tuple(),
            "sample_4",
        ),
    ],
)
def test_with_transcriptions(
    export_db_path, samples_dir, transcriptions_worker_version, headers, expected_output
):
    with tempfile.NamedTemporaryFile(suffix=".csv") as f:
        run(
            export_db_path,
            output_path=Path(f.name),
            with_transcriptions=True,
            transcriptions_worker_version=transcriptions_worker_version,
        )
        rows = (line.decode().strip() for line in f.readlines())
    expected_headers = [
        "id",
        "name",
        "type",
        "image_id",
        "image_url",
        "rotation_angle",
        "polygon",
        "worker_version_id",
        "created",
    ]
    for suffix in headers:
        expected_headers += [
            f"transcription_text_{suffix}",
            f"transcription_confidence_{suffix}",
            f"transcription_orientation_{suffix}",
        ]
    assert next(rows).split(",") == expected_headers

    rows = [row.split(",") for row in rows]
    # Only check columns related to transcriptions
    rows = [[row[0], *row[9:]] for row in rows if any(row[9:])]

    with (samples_dir / "transcriptions_output.json").open("r") as samples:
        data = json.loads(samples.read())[expected_output]
    assert rows == data
