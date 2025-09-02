import logging
import re

import pytest
import responses
from arkindex.exceptions import ErrorResponse
from responses import matchers

from arkindex_cli.commands.elements.ml_splits import Set, Splits


def test_set_check():
    with pytest.raises(Exception, match=re.escape("'non_float' is not a valid number")):
        Set(name="train", ratio="non_float")


@pytest.mark.parametrize(
    "arguments,message",
    [
        (
            {
                "project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5",
                "folder": "925c59af-2c63-4978-9957-fcafad279966",
            },
            "Only one of --project or --folder may be set.",
        ),
        (
            {"project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5", "recursive": True},
            "The --recursive option can only be used with the --folder one.",
        ),
        (
            {"project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5", "sets": []},
            "The --set option should have at least one value.",
        ),
        (
            {
                "project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5",
                "sets": [
                    Set(name="train", ratio=0.9),
                    Set(name="validation", ratio=0.3),
                    Set(name="test", ratio=0.2),
                ],
            },
            "The sum of the set ratios must be equal to 1.",
        ),
        (
            {
                "project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5",
                "sets": [Set(name="train", ratio=0)],
            },
            "The ratio of the train set must be strictly between 0 and 1 (not included).",
        ),
        (
            {
                "project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5",
                "sets": [Set(name="train", ratio=1)],
            },
            "The ratio of the train set must be strictly between 0 and 1 (not included).",
        ),
        (
            {
                "project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5",
                "sets": [Set(name="train", ratio=-5)],
            },
            "The ratio of the train set must be strictly between 0 and 1 (not included).",
        ),
    ],
)
def test_check_arguments(arguments, message, mocker, api_client):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    ml_splits = Splits(**arguments)
    with pytest.raises(AssertionError, match=re.escape(message)):
        ml_splits.check_arguments()


def test_check_arguments_folder_does_not_exist(api_client, mocker):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)

    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/925c59af-2c63-4978-9957-fcafad279966/",
        status=404,
    )
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)

    with pytest.raises(
        ValueError,
        match="Parent element 925c59af-2c63-4978-9957-fcafad279966 does not exist. Check the UUID.",
    ):
        ml_splits = Splits(folder="925c59af-2c63-4978-9957-fcafad279966")
        ml_splits.check_arguments()


def test_check_arguments_project_does_not_exist(api_client, mocker):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)

    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/",
        status=404,
    )
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)

    ml_splits = Splits(project="8b389e21-bfbe-446b-9c23-1f1c4314bbe5")
    with pytest.raises(
        ValueError,
        match="Project 8b389e21-bfbe-446b-9c23-1f1c4314bbe5 does not exist. Check the UUID.",
    ):
        ml_splits.check_arguments()


def test_check_arguments_type_errors(api_client, mocker):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)

    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/",
        status=200,
        json={
            "name": "My Project",
            "types": [
                {"slug": "folder", "folder": True},
                {
                    "slug": "page",
                },
                {
                    "slug": "text_line",
                },
            ],
        },
    )
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)

    ml_splits = Splits(
        project="8b389e21-bfbe-446b-9c23-1f1c4314bbe5", element_type="text_zone"
    )
    with pytest.raises(
        AssertionError,
        match=re.escape("Element type text_zone not found in project My Project."),
    ):
        ml_splits.check_arguments()


@pytest.mark.parametrize(
    "sets, expected_result",
    [
        (
            [
                Set(name="train", ratio=0.8),
                Set(name="dev", ratio=0.1),
                Set(name="test", ratio=0.1),
            ],
            [("train", 13), ("dev", 1), ("test", 1)],
        ),
        (
            [
                Set(name="train", ratio=0.8),
                Set(name="dev", ratio=0),
                Set(name="test", ratio=0.2),
            ],
            [("train", 12), ("dev", 0), ("test", 3)],
        ),
    ],
)
def test_make_splits(
    mocker,
    api_client,
    sets,
    expected_result,
):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    ml_splits = Splits()

    ml_splits.sets = sets

    # 15 elements
    test_elements = [
        "goose",
        "maverick",
        "iceman",
        "slider",
        "carole",
        "charlie",
        "phoenix",
        "bob",
        "hangman",
        "rooster",
        "coyote",
        "fanboy",
        "payback",
        "cyclone",
        "warlock",
    ]

    splits = ml_splits.make_splits(test_elements)
    assert [
        (split_name, len(elements)) for split_name, elements in splits.items()
    ] == expected_result


def test_run_dataset_create_failure(mocker, api_client):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    items = [
        {"id": "goose"},
        {"id": "maverick"},
        {"id": "iceman"},
        {"id": "slider"},
        {"id": "carole"},
        {"id": "charlie"},
        {"id": "phoenix"},
        {"id": "bob"},
        {"id": "hangman"},
        {"id": "rooster"},
        {"id": "coyote"},
        {"id": "fanboy"},
        {"id": "payback"},
        {"id": "cyclone"},
        {"id": "warlock"},
    ]
    mocker.patch("random.shuffle", return_value=items)

    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/",
        status=200,
        json={
            "name": "My Project",
            "types": [
                {"slug": "folder", "folder": True},
                {
                    "slug": "page",
                },
                {
                    "slug": "text_line",
                },
            ],
        },
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/elements/?type=page",
        status=200,
        json={"count": 15, "next": None, "results": items},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/datasets/",
        status=418,
        match=[
            matchers.json_params_matcher(
                {
                    "name": "Training dataset",
                    "description": "Dataset created with the CLI command",
                    "set_names": ["train", "dev", "test"],
                }
            )
        ],
    )

    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    arguments = {"project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5"}

    ml_splits = Splits(**arguments)
    with pytest.raises(ValueError):
        ml_splits.run()


def test_run(mocker, api_client):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    items = [
        {"id": "goose"},
        {"id": "maverick"},
        {"id": "iceman"},
        {"id": "slider"},
        {"id": "carole"},
        {"id": "charlie"},
        {"id": "phoenix"},
        {"id": "bob"},
        {"id": "hangman"},
        {"id": "rooster"},
        {"id": "coyote"},
        {"id": "fanboy"},
        {"id": "payback"},
        {"id": "cyclone"},
        {"id": "warlock"},
    ]
    # Mock shuffle for testing
    mocker.patch("random.shuffle", return_value=items)

    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/",
        status=200,
        json={
            "name": "My Project",
            "types": [
                {"slug": "folder", "folder": True},
                {
                    "slug": "page",
                },
                {
                    "slug": "text_line",
                },
            ],
        },
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/elements/?type=page",
        status=200,
        json={"count": 15, "next": None, "results": items},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/corpus/8b389e21-bfbe-446b-9c23-1f1c4314bbe5/datasets/",
        status=201,
        match=[
            matchers.json_params_matcher(
                {
                    "name": "Training dataset",
                    "description": "Dataset created with the CLI command",
                    "set_names": ["train", "dev", "test"],
                }
            )
        ],
        json={"id": "datasetid"},
    )
    for item in items[:12]:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/datasets/datasetid/elements/",
            match=[
                matchers.json_params_matcher({"set": "train", "element_id": item["id"]})
            ],
            status=201,
        )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/datasets/datasetid/elements/",
        match=[matchers.json_params_matcher({"set": "dev", "element_id": "payback"})],
        status=201,
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/datasets/datasetid/elements/",
        match=[matchers.json_params_matcher({"set": "test", "element_id": "cyclone"})],
        status=201,
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/datasets/datasetid/elements/",
        match=[matchers.json_params_matcher({"set": "train", "element_id": "warlock"})],
        status=201,
    )

    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    arguments = {"project": "8b389e21-bfbe-446b-9c23-1f1c4314bbe5"}

    ml_splits = Splits(**arguments)
    ml_splits.run()


def test_run_folder_random_order(mocker, api_client):
    """
    ML splits uses random ordering when the number of elements to pick is known
    """
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    items = [
        {"id": "goose"},
        {"id": "maverick"},
        {"id": "iceman"},
        {"id": "slider"},
        {"id": "carole"},
        {"id": "charlie"},
        {"id": "phoenix"},
        {"id": "bob"},
        {"id": "hangman"},
        {"id": "rooster"},
    ]

    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/folder_id/",
        status=200,
        json={"type": "folder", "corpus": {"id": "corpus_id"}},
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/corpus_id/",
        status=200,
        json={
            "name": "My Project",
            "types": [
                {"slug": "folder", "folder": True},
                {
                    "slug": "page",
                },
                {
                    "slug": "text_line",
                },
            ],
        },
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/folder_id/children/?order=random&page_size=10&recursive=False&type=page",
        status=200,
        json={"count": 1337, "next": None, "results": items},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/corpus/corpus_id/datasets/",
        status=201,
        match=[
            matchers.json_params_matcher(
                {
                    "name": "Training dataset",
                    "description": "Dataset created with the CLI command",
                    "set_names": ["train", "dev"],
                }
            )
        ],
        json={"id": "datasetid"},
    )
    for item in items:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/datasets/datasetid/elements/",
            match=[
                matchers.json_params_matcher({"set": "train", "element_id": item["id"]})
            ],
            status=201,
        )

    ml_splits = Splits(
        folder="folder_id",
        nb_elements=10,
        sets=[Set(name="train", ratio=0.99), Set(name="dev", ratio=0.01)],
    )
    ml_splits.run()


def test_list_random_elements_multiple_pages(mocker, api_client, caplog):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    items = [
        {"id": "goose"},
        {"id": "maverick"},
        {"id": "iceman"},
        {"id": "slider"},
        {"id": "carole"},
        {"id": "charlie"},
        {"id": "phoenix"},
        {"id": "bob"},
        {"id": "hangman"},
        {"id": "rooster"},
    ]

    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/folder_id/children/?order=random&page_size=10&recursive=False&type=page",
        status=200,
        json={"count": 1337, "results": items[:5]},
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/folder_id/children/?order=random&page_size=5&recursive=False&type=page",
        status=200,
        json={"count": 1337, "results": items[2:7]},
    )
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/folder_id/children/?order=random&page_size=3&recursive=False&type=page",
        status=200,
        json={"count": 1337, "results": items[7:]},
    )

    ml_splits = Splits(
        folder="folder_id",
        nb_elements=10,
    )
    elts = ml_splits.list_random_elements()
    assert sorted(elts) == sorted(i["id"] for i in items)
    assert caplog.record_tuples == [
        (
            "arkindex_cli.commands.elements.ml_splits",
            logging.INFO,
            "Retrieving random page elements (currently at 0/10)",
        ),
        (
            "arkindex_cli.commands.elements.ml_splits",
            logging.INFO,
            "Retrieving random page elements (currently at 5/10)",
        ),
        (
            "arkindex_cli.commands.elements.ml_splits",
            logging.INFO,
            "Retrieving random page elements (currently at 7/10)",
        ),
        (
            "arkindex_cli.commands.elements.ml_splits",
            logging.INFO,
            "Retrieved enough page elements (10/10)",
        ),
    ]


def test_list_random_elements_failure(mocker, api_client):
    mocker.url = "http://bonk.com"
    mocker.patch("arkindex_cli.auth.Profiles.get_or_exit", return_value=mocker)
    mocker.patch("arkindex_cli.auth.Profiles.get_api_client", return_value=api_client)
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/folder_id/children/?order=random&page_size=10&recursive=False&type=page",
        status=418,
    )
    ml_splits = Splits(folder="folder_id", nb_elements=10)
    with pytest.raises(ErrorResponse):
        ml_splits.list_random_elements()
