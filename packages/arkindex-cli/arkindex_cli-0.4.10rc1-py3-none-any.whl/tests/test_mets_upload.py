import shutil
from pathlib import Path

import pytest
from responses import matchers

from arkindex_cli.commands.upload import db
from arkindex_cli.commands.upload.alto.parser import AltoMetadata
from arkindex_cli.commands.upload.mets.parser import (
    METS_NS,
    MetsAlto,
    MetsElement,
    RootMetsElement,
)
from arkindex_export import (
    Element,
    ElementPath,
    Image,
    ImageServer,
    Metadata,
    Transcription,
    create_database,
    database,
)

TEST_FILE_PATH = Path("tests/samples/mets/mets_toc.xml")


@pytest.fixture
def mets_file_mapping():
    return {
        "ocr.1": MetsAlto(TEST_FILE_PATH.parent / "alto_gallica_X0000001.xml"),
        "ocr.2": MetsAlto(TEST_FILE_PATH.parent / "alto_gallica_X0000002.xml"),
    }


@pytest.fixture
def parsed_mets(tmp_path):
    # Copy folder to avoid cache storage
    dest = tmp_path / "data"
    dest.mkdir()
    for file in TEST_FILE_PATH.parent.glob("*.xml"):
        shutil.copy(file, dest / file.name)

    return RootMetsElement(dest / TEST_FILE_PATH.name, "https://iiifserver/", "bucket/")


def test_mets_parsing(mets_file_mapping):
    root = RootMetsElement(TEST_FILE_PATH, "https://iiifserver/", "bucket/")

    assert root.files_mapping == mets_file_mapping
    assert root.files_order == [
        Path(TEST_FILE_PATH.parent / "alto_gallica_X0000001.xml").resolve(),
        Path(TEST_FILE_PATH.parent / "alto_gallica_X0000002.xml").resolve(),
    ]
    assert root.metadata_list == AltoMetadata(
        target="DMDID",
        metadata_list={
            "DMD.2": [
                {"type": "text", "name": "Title", "value": "1926-01-02 (Numéro 3746)"},
                {
                    "type": "text",
                    "name": "spar_dc:sequentialDesignation1",
                    "value": "Numéro 3746",
                },
                {"type": "text", "name": "Type", "value": "periodical"},
                {"type": "date", "name": "Date", "value": "1926-01-02"},
                {"type": "text", "name": "Publisher", "value": "[s.n.]"},
                {
                    "type": "text",
                    "name": "spar_dc:ark",
                    "value": "ark:/12148/cb34429265b",
                },
            ]
        },
    )

    assert root.root is not None


def test_parse_object_types(parsed_mets):
    assert parsed_mets.list_required_types() == {
        "PAGE",
        "NEWSPAPER",
        "ISSUE",
        "TITLESECTION",
        "HEADLINE",
        "CONTENT",
        "BODY",
        "ARTICLE",
        "PARAGRAPH",
    }


def test_publish_element(responses, parsed_mets, api_client, cache):
    # Find newspaper node
    node = parsed_mets.root.find(".//mets:div[@ID='DIV.12']", namespaces=METS_NS)
    assert node is not None

    # Add create element mock response
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        match=[
            matchers.json_params_matcher(
                {
                    "type": "NEWSPAPER",
                    "name": "DIV.12",
                    "corpus": "corpus_id",
                    "parent": None,
                    "worker_run_id": "worker_run_id",
                }
            )
        ],
        json={"id": "newspaper_id"},
        status=201,
    )

    # Add create metadata mock response
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/newspaper_id/metadata/bulk/",
        match=[
            matchers.json_params_matcher(
                {
                    "metadata_list": [
                        {"type": "reference", "name": "METS ID", "value": "DIV.12"}
                    ],
                    "worker_run_id": "worker_run_id",
                }
            )
        ],
        json=[],
        status=201,
    )

    child = MetsElement(node)
    child.publish(
        cache,
        arkindex_client=api_client,
        corpus_id="corpus_id",
        worker_run_id="worker_run_id",
        publish_metadata=True,
    )

    assert child.arkindex_id == "newspaper_id"
    assert len(responses.calls) == 2


def test_publish_child(responses, parsed_mets, api_client, mets_file_mapping, cache):
    # Find a child element with lines
    headline_node = parsed_mets.root.find(
        ".//mets:div[@ID='DIV.15']", namespaces=METS_NS
    )

    assert headline_node is not None

    # Mock responses
    # Add create element mock response
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        match=[
            matchers.json_params_matcher(
                {
                    "type": "HEADLINE",
                    "name": "DIV.15",
                    "corpus": "corpus_id",
                    "parent": None,
                    "worker_run_id": "worker_run_id",
                }
            )
        ],
        json={"id": "headline_id"},
        status=201,
    )

    # Add create metadata mock response
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/headline_id/metadata/bulk/",
        match=[
            matchers.json_params_matcher(
                {
                    "metadata_list": [
                        {"type": "reference", "name": "METS ID", "value": "DIV.15"},
                        {"name": "ORDER", "type": "numeric", "value": "1"},
                    ],
                    "worker_run_id": "worker_run_id",
                }
            )
        ],
        json=[],
        status=201,
    )

    # Publication
    child = MetsElement(headline_node)

    child.publish(
        cache,
        arkindex_client=api_client,
        corpus_id="corpus_id",
        worker_run_id="worker_run_id",
        publish_metadata=True,
    )
    assert len(responses.calls) == 2


def test_publish_newspaper(
    responses, parsed_mets, api_client, mets_file_mapping, cache
):
    # Mock responses
    # Image creation
    for image_id, url in [
        # Image page 1
        ("ocr-1", "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff1"),
        # Image page 2
        ("ocr-2", "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff2"),
    ]:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/image/iiif/url/",
            match=[matchers.json_params_matcher({"url": url}, strict_match=True)],
            json={"id": f"ark-{image_id}"},
            status=201,
        )

    for element_id, element in [
        # Physical structure: page 1
        (
            "PAG_1",
            {
                "type": "page",
                "name": "PAG_1",
                "corpus": "corpus_id",
                "parent": "ark-DIV_2",
                "worker_run_id": "worker_run_id",
            },
        ),
        # Physical structure: page 2
        (
            "PAG_2",
            {
                "type": "page",
                "name": "PAG_2",
                "corpus": "corpus_id",
                "parent": "ark-DIV_3",
                "worker_run_id": "worker_run_id",
            },
        ),
        # Logical structure
        (
            "DIV_1",
            {
                "type": "NEWSPAPER",
                "name": "DIV.1",
                "corpus": "corpus_id",
                "parent": "parent_id",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_2",
            {
                "type": "PAGE",
                "name": "DIV.2",
                "corpus": "corpus_id",
                "parent": "ark-DIV_1",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_3",
            {
                "type": "PAGE",
                "name": "DIV.3",
                "corpus": "corpus_id",
                "parent": "ark-DIV_1",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_12",
            {
                "type": "NEWSPAPER",
                "name": "DIV.12",
                "corpus": "corpus_id",
                "parent": "parent_id",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_13",
            {
                "type": "ISSUE",
                "name": "DIV.13",
                "corpus": "corpus_id",
                "parent": "ark-DIV_12",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_14",
            {
                "type": "TITLESECTION",
                "name": "DIV.14",
                "corpus": "corpus_id",
                "parent": "ark-DIV_13",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_15",
            {
                "type": "HEADLINE",
                "name": "DIV.15",
                "corpus": "corpus_id",
                "parent": "ark-DIV_14",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_21",
            {
                "type": "CONTENT",
                "name": "DIV.21",
                "corpus": "corpus_id",
                "parent": "ark-DIV_13",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_144",
            {
                "type": "ARTICLE",
                "name": "A LA RECHERCHE D'UN DIEU",
                "corpus": "corpus_id",
                "parent": "ark-DIV_21",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_148",
            {
                "type": "BODY",
                "name": "DIV.148",
                "corpus": "corpus_id",
                "parent": "ark-DIV_144",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_149",
            {
                "type": "PARAGRAPH",
                "name": "DIV.149",
                "corpus": "corpus_id",
                "parent": "ark-DIV_148",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_153",
            {
                "type": "PARAGRAPH",
                "name": "DIV.153",
                "corpus": "corpus_id",
                "parent": "ark-DIV_148",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_154",
            {
                "type": "PARAGRAPH",
                "name": "DIV.154",
                "corpus": "corpus_id",
                "parent": "ark-DIV_148",
                "worker_run_id": "worker_run_id",
            },
        ),
        (
            "DIV_155",
            {
                "type": "PARAGRAPH",
                "name": "DIV.155",
                "corpus": "corpus_id",
                "parent": "ark-DIV_148",
                "worker_run_id": "worker_run_id",
            },
        ),
    ]:
        # Add create element mock response
        responses.add(
            responses.POST,
            "http://testserver/api/v1/elements/create/",
            match=[
                matchers.json_params_matcher(
                    element,
                    strict_match=False,
                )
            ],
            json={"id": f"ark-{element_id}"},
            status=201,
        )

    for element_id, transcription in [
        # Physical structure: page 1
        (
            "PAG_1",
            {
                "text": "L'ŒUVRE\n\nLe Caire,\n\nLa mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
                "confidence": 0.94,
                "worker_run_id": "worker_run_id",
            },
        ),
        # Physical structure: page 2
        (
            "PAG_2",
            {
                "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]\n\nLes saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
                "confidence": 0.98,
                "worker_run_id": "worker_run_id",
            },
        ),
    ]:
        # Add create transcription mock response
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/ark-{element_id}/transcription/",
            match=[matchers.json_params_matcher(transcription)],
            json={},
            status=201,
        )

    for element_id, element_type, transcriptions, api_results in [
        # Physical structure: page 1
        (
            "PAG_1",
            "printspace",
            [
                {
                    "polygon": [
                        [110, 392],
                        [110, 8081],
                        [5450, 8081],
                        [5450, 392],
                        [110, 392],
                    ],
                    "text": "L'ŒUVRE\n\nLe Caire,\n\nLa mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
                    "confidence": 0.94,
                }
            ],
            [{"element_id": "ark-PAG_1_PrintSpace"}],
        ),
        (
            "PAG_1_PrintSpace",
            "textblock",
            [
                {
                    "polygon": [
                        [176, 492],
                        [176, 1161],
                        [3308, 1161],
                        [3308, 492],
                        [176, 492],
                    ],
                    "text": "L'ŒUVRE",
                    "confidence": 1.0,
                },
                {
                    "polygon": [
                        [5021, 5854],
                        [5021, 5895],
                        [5241, 5895],
                        [5241, 5854],
                        [5021, 5854],
                    ],
                    "text": "Le Caire,",
                    "confidence": 0.99,
                },
                {
                    "polygon": [
                        [4345, 7666],
                        [4345, 8081],
                        [5383, 8081],
                        [5383, 7666],
                        [4345, 7666],
                    ],
                    "text": "La mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
                    "confidence": 0.93,
                },
            ],
            [
                {"element_id": "ark-PAG_1_TB000001"},
                {"element_id": "ark-PAG_1_TB000100"},
                {"element_id": "ark-PAG_1_TB000104"},
            ],
        ),
        (
            "PAG_1_TB000001",
            "textline",
            [
                {
                    "polygon": [
                        [176, 492],
                        [176, 1161],
                        [3308, 1161],
                        [3308, 492],
                        [176, 492],
                    ],
                    "text": "L'ŒUVRE",
                    "confidence": 1.0,
                }
            ],
            [{"element_id": "ark-PAG_1_TL000001"}],
        ),
        (
            "PAG_1_TB000100",
            "textline",
            [
                {
                    "polygon": [
                        [5021, 5854],
                        [5021, 5895],
                        [5241, 5895],
                        [5241, 5854],
                        [5021, 5854],
                    ],
                    "text": "Le Caire,",
                    "confidence": 0.99,
                }
            ],
            [{"element_id": "ark-PAG_1_TL000467"}],
        ),
        (
            "PAG_1_TB000104",
            "textline",
            [
                {
                    "polygon": [
                        [4402, 7666],
                        [4402, 7714],
                        [5361, 7714],
                        [5361, 7666],
                        [4402, 7666],
                    ],
                    "text": "La mosquée du sultan Hassan date du",
                    "confidence": 0.97,
                },
                {
                    "polygon": [
                        [4350, 7718],
                        [4350, 7769],
                        [5366, 7769],
                        [5366, 7718],
                        [4350, 7718],
                    ],
                    "text": "XIV\" siècle ; son extérieur est d'un châ-'",
                    "confidence": 0.9,
                },
            ],
            [
                {"element_id": "ark-PAG_1_TL000501"},
                {"element_id": "ark-PAG_1_TL000502"},
            ],
        ),
        # Physical structure: page 2
        (
            "PAG_2",
            "printspace",
            [
                {
                    "polygon": [
                        [436, 465],
                        [436, 8137],
                        [5781, 8137],
                        [5781, 465],
                        [436, 465],
                    ],
                    "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]\n\nLes saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
                    "confidence": 0.98,
                }
            ],
            [{"element_id": "ark-PAG_2_PrintSpace"}],
        ),
        (
            "PAG_2_PrintSpace",
            "textblock",
            [
                {
                    "polygon": [
                        [436, 507],
                        [436, 2485],
                        [1527, 2485],
                        [1527, 507],
                        [436, 507],
                    ],
                    "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]",
                    "confidence": 0.98,
                },
                {
                    "polygon": [
                        [438, 2474],
                        [438, 3166],
                        [1527, 3166],
                        [1527, 2474],
                        [438, 2474],
                    ],
                    "text": "Les saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
                    "confidence": 0.99,
                },
            ],
            [
                {"element_id": "ark-PAG_2_TB000001"},
                {"element_id": "ark-PAG_2_TB000002"},
            ],
        ),
        (
            "PAG_2_TB000001",
            "textline",
            [
                {
                    "polygon": [
                        [438, 507],
                        [438, 562],
                        [1527, 562],
                        [1527, 507],
                        [438, 507],
                    ],
                    "text": "sait que la congrégation des derviches 1",
                    "confidence": 0.98,
                },
                {
                    "polygon": [
                        [438, 560],
                        [438, 614],
                        [1527, 614],
                        [1527, 560],
                        [438, 560],
                    ],
                    "text": "exécute des danses sacrées pour faire ]",
                    "confidence": 0.99,
                },
            ],
            [
                {"element_id": "ark-PAG_2_TL000001"},
                {"element_id": "ark-PAG_2_TL000002"},
            ],
        ),
        (
            "PAG_2_TB000002",
            "textline",
            [
                {
                    "polygon": [
                        [493, 2474],
                        [493, 2527],
                        [1527, 2527],
                        [1527, 2474],
                        [493, 2474],
                    ],
                    "text": "Les saintes femmes, ayant la vague j",
                    "confidence": 0.98,
                },
                {
                    "polygon": [
                        [438, 2528],
                        [438, 2582],
                        [1462, 2582],
                        [1462, 2528],
                        [438, 2528],
                    ],
                    "text": "idée qu'elles èommettraient un péché en",
                    "confidence": 0.99,
                },
            ],
            [
                {"element_id": "ark-PAG_2_TL000038"},
                {"element_id": "ark-PAG_2_TL000039"},
            ],
        ),
    ]:
        # Add create element transcription mock response
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/ark-{element_id}/transcriptions/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "element_type": element_type,
                        "transcriptions": transcriptions,
                        "return_elements": True,
                        "worker_run_id": "worker_run_id",
                    },
                )
            ],
            json=api_results,
            status=201,
        )

    for element_id, metadata_list in [
        # Physical structure: page 1
        (
            "PAG_1",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1"}],
        ),
        (
            "PAG_1_PrintSpace",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1_PrintSpace"}],
        ),
        (
            "PAG_1_TB000001",
            [
                {"type": "reference", "name": "Alto ID", "value": "PAG_1_TB000001"},
                {"type": "text", "name": "Lang", "value": "fr"},
            ],
        ),
        (
            "PAG_1_TL000001",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1_TL000001"}],
        ),
        (
            "PAG_1_TB000100",
            [
                {"type": "reference", "name": "Alto ID", "value": "PAG_1_TB000100"},
                {"type": "text", "name": "Lang", "value": "fr"},
            ],
        ),
        (
            "PAG_1_TL000467",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1_TL000467"}],
        ),
        (
            "PAG_1_TB000104",
            [
                {"type": "reference", "name": "Alto ID", "value": "PAG_1_TB000104"},
                {"type": "text", "name": "Lang", "value": "fr"},
            ],
        ),
        (
            "PAG_1_TL000501",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1_TL000501"}],
        ),
        (
            "PAG_1_TL000502",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_1_TL000502"}],
        ),
        # Physical structure: page 2
        (
            "PAG_2",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2"}],
        ),
        (
            "PAG_2_PrintSpace",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2_PrintSpace"}],
        ),
        (
            "PAG_2_TB000001",
            [
                {"type": "reference", "name": "Alto ID", "value": "PAG_2_TB000001"},
                {"type": "text", "name": "Lang", "value": "fr"},
            ],
        ),
        (
            "PAG_2_TL000001",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2_TL000001"}],
        ),
        (
            "PAG_2_TL000002",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2_TL000002"}],
        ),
        (
            "PAG_2_TB000002",
            [
                {"type": "reference", "name": "Alto ID", "value": "PAG_2_TB000002"},
                {"type": "text", "name": "Lang", "value": "fr"},
            ],
        ),
        (
            "PAG_2_TL000038",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2_TL000038"}],
        ),
        (
            "PAG_2_TL000039",
            [{"type": "reference", "name": "Alto ID", "value": "PAG_2_TL000039"}],
        ),
        # Logical structure
        (
            "DIV_1",
            [{"type": "reference", "name": "METS ID", "value": "DIV.1"}],
        ),
        (
            "DIV_2",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.2"},
                {"type": "numeric", "name": "ORDER", "value": "1"},
            ],
        ),
        (
            "DIV_3",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.3"},
                {"type": "numeric", "name": "ORDER", "value": "2"},
            ],
        ),
        (
            "DIV_12",
            [{"type": "reference", "name": "METS ID", "value": "DIV.12"}],
        ),
        (
            "DIV_13",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.13"},
                {"type": "text", "name": "Title", "value": "1926-01-02 (Numéro 3746)"},
                {
                    "type": "text",
                    "name": "spar_dc:sequentialDesignation1",
                    "value": "Numéro 3746",
                },
                {"type": "text", "name": "Type", "value": "periodical"},
                {"type": "date", "name": "Date", "value": "1926-01-02"},
                {"type": "text", "name": "Publisher", "value": "[s.n.]"},
                {
                    "type": "text",
                    "name": "spar_dc:ark",
                    "value": "ark:/12148/cb34429265b",
                },
            ],
        ),
        (
            "DIV_14",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.14"},
                {"name": "ORDER", "type": "numeric", "value": "1"},
            ],
        ),
        (
            "DIV_15",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.15"},
                {"type": "numeric", "name": "ORDER", "value": "1"},
            ],
        ),
        (
            "DIV_21",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.21"},
                {"name": "ORDER", "type": "numeric", "value": "2"},
            ],
        ),
        (
            "DIV_144",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.144"},
                {"name": "ORDER", "type": "numeric", "value": "3"},
            ],
        ),
        (
            "DIV_148",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.148"},
                {"name": "ORDER", "type": "numeric", "value": "2"},
            ],
        ),
        (
            "DIV_149",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.149"},
                {"name": "ORDER", "type": "numeric", "value": "1"},
            ],
        ),
        (
            "DIV_153",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.153"},
                {"name": "ORDER", "type": "numeric", "value": "2"},
            ],
        ),
        (
            "DIV_154",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.154"},
                {"name": "ORDER", "type": "numeric", "value": "3"},
            ],
        ),
        (
            "DIV_155",
            [
                {"type": "reference", "name": "METS ID", "value": "DIV.155"},
                {"name": "ORDER", "type": "numeric", "value": "4"},
            ],
        ),
    ]:
        # Add create metadata mock response
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/ark-{element_id}/metadata/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "metadata_list": metadata_list,
                        "worker_run_id": "worker_run_id",
                    }
                )
            ],
            json=[],
            status=201,
        )

    # Links between elements
    for child, parent in [
        # Logical structure
        ("ark-PAG_1_TB000001", "ark-DIV_15"),
        ("ark-PAG_1_TB000100", "ark-DIV_149"),
        ("ark-PAG_1_TB000104", "ark-DIV_153"),
        ("ark-PAG_2_TB000001", "ark-DIV_154"),
        ("ark-PAG_2_TB000002", "ark-DIV_155"),
    ]:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{child}/parent/{parent}/",
            json={"child": child, "parent": parent},
            status=201,
        )

    # Corpus for types
    responses.add(
        responses.GET,
        "http://testserver/api/v1/corpus/corpus_id/",
        json={"id": "corpus_id", "types": []},
        status=200,
    )

    # Missing Types creation
    for type_slug in ("page", "printspace", "textblock", "textline"):
        responses.add(
            responses.POST,
            "http://testserver/api/v1/elements/type/",
            match=[
                matchers.json_params_matcher(
                    {
                        "corpus": "corpus_id",
                        "slug": type_slug,
                        "display_name": type_slug,
                    }
                )
            ],
            json={
                "id": f"ID_{type_slug}",
                "slug": type_slug,
                "display_name": type_slug,
            },
            status=201,
        )

    # Publication
    parsed_mets.publish(
        cache=cache,
        arkindex_client=api_client,
        corpus_id="corpus_id",
        parent_id="parent_id",
        worker_run_id="worker_run_id",
    )

    assert len(responses.calls) == 70


@pytest.mark.parametrize("nb_import", [1, 2])
def test_publish_newspaper_on_db(
    nb_import, responses, parsed_mets, api_client, cache, tmp_path
):
    worker_version = {
        "id": "worker_version_id",
        "worker": {
            "slug": "fake-worker",
            "name": "Fake worker",
            "type": "fake",
            "repository_url": "registry.gitlab.co.jp/nerv/",
        },
        "version": 1,
        "revision_url": None,
    }
    worker_run = {
        "id": "worker_run_id",
        "worker_version": worker_version,
        "model_version": None,
        "configuration": None,
    }

    for image_id, url in [
        # Image page 1
        ("ocr-1", "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff1"),
        # Image page 2
        ("ocr-2", "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff2"),
    ]:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/image/iiif/url/",
            match=[matchers.json_params_matcher({"url": url}, strict_match=True)],
            json={
                "id": f"ark-{image_id}",
                "url": url,
                "width": 800,
                "height": 1200,
                "server": {
                    "id": 5,
                    "url": "https://iiifserver/ark",
                    "display_name": "My server",
                    "max_width": 5000,
                    "max_height": 10000,
                },
            },
            status=201,
        )

    db_path = tmp_path / "test.db"
    db_path.parent.mkdir(exist_ok=True, parents=True)
    create_database(db_path, db.EXPORT_VERSION)
    db.get_or_create_worker_version(worker_version)
    db.get_or_create_worker_run(worker_run)
    parent_id = db.get_or_create_element(
        name="METS upload from CLI", type="folder", worker_run=worker_run
    ).id

    for _ in range(nb_import):
        parsed_mets.publish(
            cache=cache,
            arkindex_client=api_client,
            parent_id=parent_id,
            worker_run_id=worker_run["id"],
        )

    assert list(ImageServer.select().dicts()) == [
        {
            "id": 5,
            "url": "https://iiifserver/ark",
            "display_name": "My server",
            "max_width": 5000,
            "max_height": 10000,
        }
    ]
    assert [
        {key: value for key, value in image.items() if key not in ["id"]}
        for image in Image.select().dicts()
    ] == [
        {
            "server": 5,
            "url": "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff1",
            "width": 800,
            "height": 1200,
        },
        {
            "server": 5,
            "url": "https://iiifserver/ark%3A%2F12148%2Fbpt6k46127951%2Ff2",
            "width": 800,
            "height": 1200,
        },
    ]

    assert [
        {
            key: value
            for key, value in element.items()
            if key not in ["id", "created", "updated"]
        }
        for element in Element.select().order_by(Element.created).dicts()
    ] == [
        {
            "name": "METS upload from CLI",
            "type": "folder",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.1",
            "type": "NEWSPAPER",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.2",
            "type": "PAGE",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        # Physical structure: page 1
        {
            "name": "PAG_1",
            "type": "page",
            "image": "ark-ocr-1",
            "polygon": "[[0, 0], [0, 8687], [5808, 8687], [5808, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_PrintSpace",
            "type": "printspace",
            "image": "ark-ocr-1",
            "polygon": "[[110, 392], [110, 8081], [5450, 8081], [5450, 392], [110, 392]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TB000001",
            "type": "textblock",
            "image": "ark-ocr-1",
            "polygon": "[[176, 492], [176, 1161], [3308, 1161], [3308, 492], [176, 492]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TB000100",
            "type": "textblock",
            "image": "ark-ocr-1",
            "polygon": "[[5021, 5854], [5021, 5895], [5241, 5895], [5241, 5854], [5021, 5854]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TB000104",
            "type": "textblock",
            "image": "ark-ocr-1",
            "polygon": "[[4345, 7666], [4345, 8081], [5383, 8081], [5383, 7666], [4345, 7666]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TL000001",
            "type": "textline",
            "image": "ark-ocr-1",
            "polygon": "[[176, 492], [176, 1161], [3308, 1161], [3308, 492], [176, 492]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TL000467",
            "type": "textline",
            "image": "ark-ocr-1",
            "polygon": "[[5021, 5854], [5021, 5895], [5241, 5895], [5241, 5854], [5021, 5854]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TL000501",
            "type": "textline",
            "image": "ark-ocr-1",
            "polygon": "[[4402, 7666], [4402, 7714], [5361, 7714], [5361, 7666], [4402, 7666]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_1_TL000502",
            "type": "textline",
            "image": "ark-ocr-1",
            "polygon": "[[4350, 7718], [4350, 7769], [5366, 7769], [5366, 7718], [4350, 7718]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.3",
            "type": "PAGE",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        # Physical structure: page 2
        {
            "name": "PAG_2",
            "type": "page",
            "image": "ark-ocr-2",
            "polygon": "[[0, 0], [0, 8663], [5899, 8663], [5899, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_PrintSpace",
            "type": "printspace",
            "image": "ark-ocr-2",
            "polygon": "[[436, 465], [436, 8137], [5781, 8137], [5781, 465], [436, 465]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TB000001",
            "type": "textblock",
            "image": "ark-ocr-2",
            "polygon": "[[436, 507], [436, 2485], [1527, 2485], [1527, 507], [436, 507]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TB000002",
            "type": "textblock",
            "image": "ark-ocr-2",
            "polygon": "[[438, 2474], [438, 3166], [1527, 3166], [1527, 2474], [438, 2474]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TL000001",
            "type": "textline",
            "image": "ark-ocr-2",
            "polygon": "[[438, 507], [438, 562], [1527, 562], [1527, 507], [438, 507]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TL000002",
            "type": "textline",
            "image": "ark-ocr-2",
            "polygon": "[[438, 560], [438, 614], [1527, 614], [1527, 560], [438, 560]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TL000038",
            "type": "textline",
            "image": "ark-ocr-2",
            "polygon": "[[493, 2474], [493, 2527], [1527, 2527], [1527, 2474], [493, 2474]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PAG_2_TL000039",
            "type": "textline",
            "image": "ark-ocr-2",
            "polygon": "[[438, 2528], [438, 2582], [1462, 2582], [1462, 2528], [438, 2528]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        # Logical structure
        {
            "name": "DIV.12",
            "type": "NEWSPAPER",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.13",
            "type": "ISSUE",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.14",
            "type": "TITLESECTION",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.15",
            "type": "HEADLINE",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.21",
            "type": "CONTENT",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "A LA RECHERCHE D'UN DIEU",
            "type": "ARTICLE",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.148",
            "type": "BODY",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.149",
            "type": "PARAGRAPH",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.153",
            "type": "PARAGRAPH",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.154",
            "type": "PARAGRAPH",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "DIV.155",
            "type": "PARAGRAPH",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
    ]

    parent = Element.alias("parent")
    child = Element.alias("child")
    assert list(
        ElementPath.select(
            ElementPath.ordering,
            parent.name.alias("parent_name"),
            child.name.alias("child_name"),
        )
        .join(parent, on=ElementPath.parent == parent.id)
        .join(child, on=ElementPath.child == child.id)
        .order_by(parent.created)
        .dicts()
    ) == [
        {"ordering": 0, "parent_name": "METS upload from CLI", "child_name": "DIV.1"},
        {"ordering": 1, "parent_name": "METS upload from CLI", "child_name": "DIV.12"},
        {"ordering": 0, "parent_name": "DIV.1", "child_name": "DIV.2"},
        {"ordering": 1, "parent_name": "DIV.1", "child_name": "DIV.3"},
        # Physical structure: page 1
        {"ordering": 0, "parent_name": "DIV.2", "child_name": "PAG_1"},
        {"ordering": 0, "parent_name": "PAG_1", "child_name": "PAG_1_PrintSpace"},
        {
            "ordering": 0,
            "parent_name": "PAG_1_PrintSpace",
            "child_name": "PAG_1_TB000001",
        },
        {
            "ordering": 1,
            "parent_name": "PAG_1_PrintSpace",
            "child_name": "PAG_1_TB000100",
        },
        {
            "ordering": 2,
            "parent_name": "PAG_1_PrintSpace",
            "child_name": "PAG_1_TB000104",
        },
        {
            "ordering": 0,
            "parent_name": "PAG_1_TB000001",
            "child_name": "PAG_1_TL000001",
        },
        {
            "ordering": 0,
            "parent_name": "PAG_1_TB000100",
            "child_name": "PAG_1_TL000467",
        },
        {
            "ordering": 0,
            "parent_name": "PAG_1_TB000104",
            "child_name": "PAG_1_TL000501",
        },
        {
            "ordering": 1,
            "parent_name": "PAG_1_TB000104",
            "child_name": "PAG_1_TL000502",
        },
        # Physical structure: page 2
        {"ordering": 0, "parent_name": "DIV.3", "child_name": "PAG_2"},
        {"ordering": 0, "parent_name": "PAG_2", "child_name": "PAG_2_PrintSpace"},
        {
            "ordering": 0,
            "parent_name": "PAG_2_PrintSpace",
            "child_name": "PAG_2_TB000001",
        },
        {
            "ordering": 1,
            "parent_name": "PAG_2_PrintSpace",
            "child_name": "PAG_2_TB000002",
        },
        {
            "ordering": 0,
            "parent_name": "PAG_2_TB000001",
            "child_name": "PAG_2_TL000001",
        },
        {
            "ordering": 1,
            "parent_name": "PAG_2_TB000001",
            "child_name": "PAG_2_TL000002",
        },
        {
            "ordering": 0,
            "parent_name": "PAG_2_TB000002",
            "child_name": "PAG_2_TL000038",
        },
        {
            "ordering": 1,
            "parent_name": "PAG_2_TB000002",
            "child_name": "PAG_2_TL000039",
        },
        # Logical structure
        {"ordering": 0, "parent_name": "DIV.12", "child_name": "DIV.13"},
        {"ordering": 0, "parent_name": "DIV.13", "child_name": "DIV.14"},
        {"ordering": 1, "parent_name": "DIV.13", "child_name": "DIV.21"},
        {"ordering": 0, "parent_name": "DIV.14", "child_name": "DIV.15"},
        {"ordering": 0, "parent_name": "DIV.15", "child_name": "PAG_1_TB000001"},
        {
            "ordering": 0,
            "parent_name": "DIV.21",
            "child_name": "A LA RECHERCHE D'UN DIEU",
        },
        {
            "ordering": 0,
            "parent_name": "A LA RECHERCHE D'UN DIEU",
            "child_name": "DIV.148",
        },
        {"ordering": 0, "parent_name": "DIV.148", "child_name": "DIV.149"},
        {"ordering": 1, "parent_name": "DIV.148", "child_name": "DIV.153"},
        {"ordering": 2, "parent_name": "DIV.148", "child_name": "DIV.154"},
        {"ordering": 3, "parent_name": "DIV.148", "child_name": "DIV.155"},
        {"ordering": 0, "parent_name": "DIV.149", "child_name": "PAG_1_TB000100"},
        {"ordering": 0, "parent_name": "DIV.153", "child_name": "PAG_1_TB000104"},
        {"ordering": 0, "parent_name": "DIV.154", "child_name": "PAG_2_TB000001"},
        {"ordering": 0, "parent_name": "DIV.155", "child_name": "PAG_2_TB000002"},
    ]

    assert [
        {
            key: value
            for key, value in transcription.items()
            if key not in ["id", "element"]
        }
        for transcription in (
            Transcription.select(Transcription, Element.name.alias("element_name"))
            .join(Element)
            .order_by(Element.created)
            .dicts()
        )
    ] == [
        # Physical structure: page 1
        {
            "orientation": "horizontal-lr",
            "text": "L'ŒUVRE\n\nLe Caire,\n\nLa mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
            "confidence": 0.94,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1",
        },
        {
            "orientation": "horizontal-lr",
            "text": "L'ŒUVRE\n\nLe Caire,\n\nLa mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
            "confidence": 0.94,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_PrintSpace",
        },
        {
            "orientation": "horizontal-lr",
            "text": "L'ŒUVRE",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000001",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Le Caire,",
            "confidence": 0.99,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000100",
        },
        {
            "orientation": "horizontal-lr",
            "text": "La mosquée du sultan Hassan date du XIV\" siècle ; son extérieur est d'un châ-'",
            "confidence": 0.93,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000104",
        },
        {
            "orientation": "horizontal-lr",
            "text": "L'ŒUVRE",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000001",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Le Caire,",
            "confidence": 0.99,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000467",
        },
        {
            "orientation": "horizontal-lr",
            "text": "La mosquée du sultan Hassan date du",
            "confidence": 0.97,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000501",
        },
        {
            "orientation": "horizontal-lr",
            "text": "XIV\" siècle ; son extérieur est d'un châ-'",
            "confidence": 0.9,
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000502",
        },
        # Physical structure: page 2
        {
            "orientation": "horizontal-lr",
            "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]\n\nLes saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
            "confidence": 0.98,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2",
        },
        {
            "orientation": "horizontal-lr",
            "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]\n\nLes saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
            "confidence": 0.98,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_PrintSpace",
        },
        {
            "orientation": "horizontal-lr",
            "text": "sait que la congrégation des derviches 1 exécute des danses sacrées pour faire ]",
            "confidence": 0.98,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000001",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Les saintes femmes, ayant la vague j idée qu'elles èommettraient un péché en",
            "confidence": 0.99,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000002",
        },
        {
            "orientation": "horizontal-lr",
            "text": "sait que la congrégation des derviches 1",
            "confidence": 0.98,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000001",
        },
        {
            "orientation": "horizontal-lr",
            "text": "exécute des danses sacrées pour faire ]",
            "confidence": 0.99,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000002",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Les saintes femmes, ayant la vague j",
            "confidence": 0.98,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000038",
        },
        {
            "orientation": "horizontal-lr",
            "text": "idée qu'elles èommettraient un péché en",
            "confidence": 0.99,
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000039",
        },
    ]

    assert [
        {key: value for key, value in metadata.items() if key not in ["id", "element"]}
        for metadata in (
            Metadata.select(Metadata, Element.name.alias("element_name"))
            .join(Element)
            .order_by(Element.created)
            .dicts()
        )
    ] == [
        {
            "name": "METS ID",
            "value": "DIV.1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.1",
        },
        {
            "name": "METS ID",
            "value": "DIV.2",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.2",
        },
        {
            "name": "ORDER",
            "value": "1",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.2",
        },
        # Physical structure: page 1
        {
            "name": "Alto ID",
            "value": "PAG_1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_PrintSpace",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_PrintSpace",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TB000001",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000001",
        },
        {
            "name": "Lang",
            "value": "fr",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000001",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TB000100",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000100",
        },
        {
            "name": "Lang",
            "value": "fr",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000100",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TB000104",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000104",
        },
        {
            "name": "Lang",
            "value": "fr",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TB000104",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TL000001",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000001",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TL000467",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000467",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TL000501",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000501",
        },
        {
            "name": "Alto ID",
            "value": "PAG_1_TL000502",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_1_TL000502",
        },
        {
            "name": "METS ID",
            "value": "DIV.3",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.3",
        },
        {
            "name": "ORDER",
            "value": "2",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.3",
        },
        # Physical structure: page 2
        {
            "name": "Alto ID",
            "value": "PAG_2",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_PrintSpace",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_PrintSpace",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TB000001",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000001",
        },
        {
            "name": "Lang",
            "value": "fr",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000001",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TB000002",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000002",
        },
        {
            "name": "Lang",
            "value": "fr",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TB000002",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TL000001",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000001",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TL000002",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000002",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TL000038",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000038",
        },
        {
            "name": "Alto ID",
            "value": "PAG_2_TL000039",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PAG_2_TL000039",
        },
        # Logical structure
        {
            "name": "METS ID",
            "value": "DIV.12",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.12",
        },
        {
            "name": "METS ID",
            "value": "DIV.13",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "Title",
            "value": "1926-01-02 (Numéro 3746)",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "spar_dc:sequentialDesignation1",
            "value": "Numéro 3746",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "Type",
            "value": "periodical",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "Date",
            "value": "1926-01-02",
            "type": "date",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "Publisher",
            "value": "[s.n.]",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "spar_dc:ark",
            "value": "ark:/12148/cb34429265b",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "DIV.13",
        },
        {
            "name": "METS ID",
            "value": "DIV.14",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.14",
        },
        {
            "name": "ORDER",
            "value": "1",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.14",
        },
        {
            "name": "METS ID",
            "value": "DIV.15",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.15",
        },
        {
            "name": "ORDER",
            "value": "1",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.15",
        },
        {
            "name": "METS ID",
            "value": "DIV.21",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.21",
        },
        {
            "name": "ORDER",
            "value": "2",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.21",
        },
        {
            "name": "METS ID",
            "value": "DIV.144",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "A LA RECHERCHE D'UN DIEU",
        },
        {
            "name": "ORDER",
            "value": "3",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "A LA RECHERCHE D'UN DIEU",
        },
        {
            "name": "METS ID",
            "value": "DIV.148",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.148",
        },
        {
            "name": "ORDER",
            "value": "2",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.148",
        },
        {
            "name": "METS ID",
            "value": "DIV.149",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.149",
        },
        {
            "name": "ORDER",
            "value": "1",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.149",
        },
        {
            "name": "METS ID",
            "value": "DIV.153",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.153",
        },
        {
            "name": "ORDER",
            "value": "2",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.153",
        },
        {
            "name": "METS ID",
            "value": "DIV.154",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.154",
        },
        {
            "name": "ORDER",
            "value": "3",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.154",
        },
        {
            "name": "METS ID",
            "value": "DIV.155",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "DIV.155",
        },
        {
            "name": "ORDER",
            "value": "4",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "DIV.155",
        },
    ]

    database.close()
    assert not db.is_available()
