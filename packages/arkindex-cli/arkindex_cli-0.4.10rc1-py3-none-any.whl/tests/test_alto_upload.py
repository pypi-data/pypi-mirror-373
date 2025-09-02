import json
import shutil
from pathlib import Path

import pytest
from responses import matchers

from arkindex_cli.commands.upload import db
from arkindex_cli.commands.upload.alto import (
    format_url,
    parse_image_idx,
    upload_alto_file,
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

TEST_FILE_PATH = Path("tests/samples/alto_page.xml")
GALLICA_TEST_FILE_PATH = Path("tests/samples/18840615_1-0001.xml")
IIIF_BASE_URL = "http://some-server.com/iiif/a%2Fpath%2F"
GALLICA_IIIF_BASE_URL = "https://gallica.bnf.fr/iiif/"
PARENT_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
IMAGE_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
PAGE_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"


def test_format_url():
    assert (
        format_url(
            GALLICA_TEST_FILE_PATH,
            GALLICA_IIIF_BASE_URL,
            {"18840615": "ark:/12148/bpt6k7155522"},
        )
        == "https://gallica.bnf.fr/iiif/ark:/12148/bpt6k7155522/f1"
    )


@pytest.mark.parametrize(
    "filename, idx",
    (
        ("0001.xml", "1"),
        ("X0001.xml", "1"),
        ("0011.xml", "11"),
        ("X0011.xml", "11"),
    ),
)
def test_parse_image_idx(filename, idx):
    assert parse_image_idx(filename) == idx


@pytest.mark.parametrize(
    "path, iiif_url, page_name, image_url, gallica, folders_ark_id_dict, alto_namespace",
    [
        (
            TEST_FILE_PATH,
            IIIF_BASE_URL,
            "P1",
            IIIF_BASE_URL + "tests%2Fsamples%2Fpage_image.jpg",
            False,
            None,
            None,
        ),
        (
            GALLICA_TEST_FILE_PATH,
            GALLICA_IIIF_BASE_URL,
            "P1",
            "https://gallica.bnf.fr/iiif/ark:/12148/bpt6k7155522/f1",
            True,
            {"18840615": "ark:/12148/bpt6k7155522"},
            "http://schema.ccs-gmbh.com/docworks/version20/alto-1-4.xsd",
        ),
    ],
)
@pytest.mark.parametrize("cache_exists", [True, False])
def test_import_one_page_alto(
    responses,
    api_client,
    mock_corpus,
    tmp_path,
    path,
    iiif_url,
    page_name,
    image_url,
    gallica,
    folders_ark_id_dict,
    alto_namespace,
    cache_exists,
):
    worker_run_id = "worker_run_id"

    responses.add(
        responses.POST,
        "http://testserver/api/v1/image/iiif/url/",
        match=[matchers.json_params_matcher({"url": image_url})],
        json={"id": IMAGE_ID},
        status=201,
    )

    if not cache_exists:
        for item in ["rightmargin", "printspace", "textblock", "textline"]:
            responses.add(
                responses.POST,
                "http://testserver/api/v1/elements/type/",
                status=201,
                match=[
                    matchers.json_params_matcher(
                        {
                            "slug": item,
                            "display_name": item,
                            "corpus": mock_corpus["id"],
                        }
                    )
                ],
            )

        responses.add(
            responses.GET,
            f"http://testserver/api/v1/corpus/{mock_corpus['id']}/",
            json=mock_corpus,
            status=200,
        )

    # Create page
    page_body = {
        "corpus": mock_corpus["id"],
        "parent": PARENT_ID,
        "type": "page",
        "name": page_name,
        "image": IMAGE_ID,
        "polygon": [[0, 0], [0, 1200], [800, 1200], [800, 0], [0, 0]],
        "worker_run_id": worker_run_id,
    }
    # If the cache exists, we do not create a new element but link the existing one to the new parent
    if cache_exists:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{PAGE_ID}/parent/{page_body['parent']}/",
            json={},
            status=201,
        )
    else:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/elements/create/",
            match=[matchers.json_params_matcher(page_body)],
            json={"id": PAGE_ID},
            status=201,
        )
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{PAGE_ID}/transcription/",
            match=[
                matchers.json_params_matcher(
                    {
                        "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                        "confidence": 1.0,
                        "worker_run_id": worker_run_id,
                    }
                )
            ],
            json={},
            status=201,
        )

    # Create right margin
    # If the cache exists, we do not create a new element but link the existing one to the new parent
    if cache_exists:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/rm_1_id/parent/{PAGE_ID}/",
            json={},
            status=201,
        )
    else:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{PAGE_ID}/children/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "elements": [
                            {
                                "type": "rightmargin",
                                "name": "RM_1",
                                "polygon": [
                                    [0, 0],
                                    [0, 1100],
                                    [30, 1100],
                                    [30, 0],
                                    [0, 0],
                                ],
                            }
                        ],
                        "worker_run_id": worker_run_id,
                    }
                )
            ],
            json=[{"id": "rm_1_id"}],
            status=201,
        )

    # Create transcriptions
    for element_id, element_type, transcriptions, api_results in [
        # Page with printspace
        (
            PAGE_ID,
            "printspace",
            [
                {
                    "polygon": [[0, 0], [0, 1010], [650, 1010], [650, 0], [0, 0]],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                }
            ],
            [{"element_id": "ps_1_id"}],
        ),
        # Printspace with text blocks
        (
            "ps_1_id",
            "textblock",
            [
                {
                    "polygon": [[0, 0], [0, 400], [650, 400], [650, 0], [0, 0]],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en A-",
                    "confidence": 1.0,
                },
                {
                    "polygon": [[0, 410], [0, 760], [650, 760], [650, 410], [0, 410]],
                    "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tb_1_id"}, {"element_id": "tb_2_id"}],
        ),
        # Text block 1 with text lines
        (
            "tb_1_id",
            "textline",
            [
                {
                    "polygon": [
                        [200, 250],
                        [200, 290],
                        [550, 290],
                        [550, 250],
                        [200, 250],
                    ],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermo-",
                    "confidence": 1.0,
                },
                {
                    "polygon": [
                        [210, 300],
                        [210, 335],
                        [560, 335],
                        [560, 300],
                        [210, 300],
                    ],
                    "text": "gène qui vient de rentrer à la Villa après un assez long voyage en A-",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tl_1_id"}, {"element_id": "tl_2_id"}],
        ),
        # Text block 2 with text lines
        (
            "tb_2_id",
            "textline",
            [
                {
                    "polygon": [
                        [200, 550],
                        [200, 590],
                        [550, 590],
                        [550, 550],
                        [200, 550],
                    ],
                    "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée.",
                    "confidence": 1.0,
                },
                {
                    "polygon": [
                        [190, 600],
                        [190, 650],
                        [540, 650],
                        [540, 600],
                        [190, 600],
                    ],
                    "text": "Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tl_3_id"}, {"element_id": "tl_4_id"}],
        ),
    ]:
        # If the cache exists, we do not create a new element but link the existing one to the new parent
        if cache_exists:
            for child in api_results:
                responses.add(
                    responses.POST,
                    f"http://testserver/api/v1/element/{child['element_id']}/parent/{element_id}/",
                    json={},
                    status=201,
                )
        else:
            responses.add(
                responses.POST,
                f"http://testserver/api/v1/element/{element_id}/transcriptions/bulk/",
                match=[
                    matchers.json_params_matcher(
                        {
                            "element_type": element_type,
                            "transcriptions": transcriptions,
                            "return_elements": True,
                            "worker_run_id": worker_run_id,
                        }
                    )
                ],
                json=api_results,
                status=201,
            )

    # Create metadata
    for element_id, metadata_list in [
        # Page
        (PAGE_ID, [{"type": "reference", "name": "Alto ID", "value": "P1"}]),
        # Right margin
        ("rm_1_id", [{"type": "reference", "name": "Alto ID", "value": "RM_1"}]),
        # Printspace
        ("ps_1_id", [{"type": "reference", "name": "Alto ID", "value": "PS_1"}]),
        # Text block 1
        (
            "tb_1_id",
            [
                {"name": "Alto ID", "value": "TB_1", "type": "reference"},
                {"name": "Fontfamily", "value": "Times New Roman", "type": "text"},
                {"name": "Fontsize", "value": "20", "type": "numeric"},
                {"name": "Align", "value": "Block", "type": "text"},
                {"name": "Description", "value": "Début", "type": "text"},
                {"name": "Type", "value": "Structural", "type": "text"},
            ],
        ),
        # Text block 2
        (
            "tb_2_id",
            [
                {"name": "Alto ID", "value": "TB_2", "type": "reference"},
                {"name": "Fontfamily", "value": "Times New Roman", "type": "text"},
                {"name": "Fontsize", "value": "20", "type": "numeric"},
                {"name": "Align", "value": "Block", "type": "text"},
                {"name": "Description", "value": "Fin", "type": "text"},
                {"name": "Type", "value": "Structural", "type": "text"},
            ],
        ),
        # Text line 1
        ("tl_1_id", [{"type": "reference", "name": "Alto ID", "value": "TL_1"}]),
        # Text line 2
        ("tl_2_id", [{"type": "reference", "name": "Alto ID", "value": "TL_2"}]),
        # Text line 3
        ("tl_3_id", [{"type": "reference", "name": "Alto ID", "value": "TL_3"}]),
        # Text line 4
        ("tl_4_id", [{"type": "reference", "name": "Alto ID", "value": "TL_4"}]),
    ]:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{element_id}/metadata/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "metadata_list": metadata_list,
                        "worker_run_id": worker_run_id,
                    }
                )
            ],
            json=[],
            status=201,
        )

    if cache_exists:
        # List children
        for element_id in [
            PARENT_ID,
            PAGE_ID,
            "ps_1_id",
            "tb_1_id",
            "tb_2_id",
        ]:
            responses.add(
                responses.GET,
                f"http://testserver/api/v1/elements/{element_id}/children/",
                json={"next": None, "count": 0, "results": []},
                status=200,
            )

    dest = tmp_path / path.name
    shutil.copy(path, dest)
    if cache_exists:
        dest.with_suffix(".json").write_text(
            json.dumps(
                {
                    "P1": PAGE_ID,
                    "PS_1": "ps_1_id",
                    "RM_1": "rm_1_id",
                    "TB_1": "tb_1_id",
                    "TB_2": "tb_2_id",
                    "TL_1": "tl_1_id",
                    "TL_2": "tl_2_id",
                    "TL_3": "tl_3_id",
                    "TL_4": "tl_4_id",
                }
            )
        )

    upload_alto_file(
        path=dest,
        client=api_client,
        iiif_base_url=iiif_url,
        corpus=mock_corpus,
        types_dict=None,
        create_types=True,
        worker_run_id=worker_run_id,
        gallica=gallica,
        folders_ark_id_dict=folders_ark_id_dict,
        alto_namespace=alto_namespace,
        parent_id=PARENT_ID,
    )


def test_mm10(responses, api_client, mock_corpus, cache):
    worker_run_id = "worker_run_id"

    element_types = ["rightmargin", "printspace", "textblock", "textline"]
    for item in element_types:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/elements/type/",
            status=201,
            match=[
                matchers.json_params_matcher(
                    {"slug": item, "display_name": item, "corpus": mock_corpus["id"]}
                )
            ],
        )

    responses.add(
        responses.POST,
        "http://testserver/api/v1/image/iiif/url/",
        match=[
            matchers.json_params_matcher(
                {"url": IIIF_BASE_URL + "tests%2Fsamples%2Fpage_image.jpg"}
            )
        ],
        json={"id": IMAGE_ID},
        status=201,
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{mock_corpus['id']}/",
        json=mock_corpus,
        status=200,
    )

    # Create page
    page_body = {
        "corpus": mock_corpus["id"],
        "parent": PARENT_ID,
        "type": "page",
        "name": "P1",
        "image": IMAGE_ID,
        "polygon": [[0, 0], [0, 1417], [944, 1417], [944, 0], [0, 0]],
        "worker_run_id": worker_run_id,
    }
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        match=[matchers.json_params_matcher(page_body)],
        json={"id": PAGE_ID},
        status=201,
    )
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{PAGE_ID}/transcription/",
        match=[
            matchers.json_params_matcher(
                {
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                    "worker_run_id": worker_run_id,
                }
            )
        ],
        json={},
        status=201,
    )

    # Create right margin
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{PAGE_ID}/children/bulk/",
        match=[
            matchers.json_params_matcher(
                {
                    "elements": [
                        {
                            "type": "rightmargin",
                            "name": "RM_1",
                            "polygon": [[0, 0], [0, 1299], [35, 1299], [35, 0], [0, 0]],
                        }
                    ],
                    "worker_run_id": worker_run_id,
                }
            )
        ],
        json=[{"id": "rm_1_id"}],
        status=201,
    )

    # Create transcriptions
    for element_id, element_type, transcriptions, api_results in [
        # Page with printspace
        (
            PAGE_ID,
            "printspace",
            [
                {
                    "polygon": [[0, 0], [0, 1193], [768, 1193], [768, 0], [0, 0]],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                }
            ],
            [{"element_id": "ps_1_id"}],
        ),
        # Printspace with text blocks
        (
            "ps_1_id",
            "textblock",
            [
                {
                    "polygon": [[0, 0], [0, 472], [768, 472], [768, 0], [0, 0]],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en A-",
                    "confidence": 1.0,
                },
                {
                    "polygon": [[0, 484], [0, 898], [768, 898], [768, 484], [0, 484]],
                    "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tb_1_id"}, {"element_id": "tb_2_id"}],
        ),
        # Text block 1 with text lines
        (
            "tb_1_id",
            "textline",
            [
                {
                    "polygon": [
                        [236, 295],
                        [236, 343],
                        [650, 343],
                        [650, 295],
                        [236, 295],
                    ],
                    "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermo-",
                    "confidence": 1.0,
                },
                {
                    "polygon": [
                        [248, 354],
                        [248, 396],
                        [661, 396],
                        [661, 354],
                        [248, 354],
                    ],
                    "text": "gène qui vient de rentrer à la Villa après un assez long voyage en A-",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tl_1_id"}, {"element_id": "tl_2_id"}],
        ),
        # Text block 2 with text lines
        (
            "tb_2_id",
            "textline",
            [
                {
                    "polygon": [
                        [236, 650],
                        [236, 697],
                        [650, 697],
                        [650, 650],
                        [236, 650],
                    ],
                    "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée.",
                    "confidence": 1.0,
                },
                {
                    "polygon": [
                        [224, 709],
                        [224, 768],
                        [638, 768],
                        [638, 709],
                        [224, 709],
                    ],
                    "text": "Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
                    "confidence": 1.0,
                },
            ],
            [{"element_id": "tl_3_id"}, {"element_id": "tl_4_id"}],
        ),
    ]:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{element_id}/transcriptions/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "element_type": element_type,
                        "transcriptions": transcriptions,
                        "return_elements": True,
                        "worker_run_id": worker_run_id,
                    }
                )
            ],
            json=api_results,
            status=201,
        )

    # Create metadata
    for element_id, metadata_list in [
        # Page
        (PAGE_ID, [{"type": "reference", "name": "Alto ID", "value": "P1"}]),
        # Right margin
        ("rm_1_id", [{"type": "reference", "name": "Alto ID", "value": "RM_1"}]),
        # Printspace
        ("ps_1_id", [{"type": "reference", "name": "Alto ID", "value": "PS_1"}]),
        # Text block 1
        (
            "tb_1_id",
            [
                {"name": "Alto ID", "value": "TB_1", "type": "reference"},
                {"name": "Fontfamily", "value": "Times New Roman", "type": "text"},
                {"name": "Fontsize", "value": "20", "type": "numeric"},
                {"name": "Align", "value": "Block", "type": "text"},
            ],
        ),
        # Text block 2
        (
            "tb_2_id",
            [
                {"name": "Alto ID", "value": "TB_2", "type": "reference"},
                {"name": "Fontfamily", "value": "Times New Roman", "type": "text"},
                {"name": "Fontsize", "value": "20", "type": "numeric"},
                {"name": "Align", "value": "Block", "type": "text"},
            ],
        ),
        # Text line 1
        ("tl_1_id", [{"type": "reference", "name": "Alto ID", "value": "TL_1"}]),
        # Text line 2
        ("tl_2_id", [{"type": "reference", "name": "Alto ID", "value": "TL_2"}]),
        # Text line 3
        ("tl_3_id", [{"type": "reference", "name": "Alto ID", "value": "TL_3"}]),
        # Text line 4
        ("tl_4_id", [{"type": "reference", "name": "Alto ID", "value": "TL_4"}]),
    ]:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{element_id}/metadata/bulk/",
            match=[
                matchers.json_params_matcher(
                    {
                        "metadata_list": metadata_list,
                        "worker_run_id": worker_run_id,
                    }
                )
            ],
            json=[],
            status=201,
        )

    upload_alto_file(
        path=Path("tests/samples/alto_mm10.xml"),
        client=api_client,
        iiif_base_url=IIIF_BASE_URL,
        corpus=mock_corpus,
        types_dict=None,
        create_types=True,
        worker_run_id=worker_run_id,
        dpi_x=300,
        dpi_y=300,
        parent_id=PARENT_ID,
    )


@pytest.mark.parametrize("nb_import", [1, 2])
def test_import_on_db(nb_import, responses, api_client, tmp_path):
    worker_version = {
        "id": "worker_version_id",
        "worker": {
            "slug": "fake-worker",
            "name": "Fake worker",
            "type": "fake",
            "repository_url": None,
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

    responses.add(
        responses.POST,
        "http://testserver/api/v1/image/iiif/url/",
        match=[
            matchers.json_params_matcher(
                {"url": IIIF_BASE_URL + "tests%2Fsamples%2Fpage_image.jpg"}
            )
        ],
        json={
            "id": IMAGE_ID,
            "url": IIIF_BASE_URL + "tests%2Fsamples%2Fpage_image.jpg",
            "width": 800,
            "height": 1200,
            "server": {
                "id": 5,
                "url": IIIF_BASE_URL,
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
    Element.update({Element.id: PARENT_ID}).where(
        Element.id
        == db.get_or_create_element(
            name="ALTO upload from CLI", type="folder", worker_run=worker_run
        ).id
    ).execute()

    dest = tmp_path / TEST_FILE_PATH.name
    shutil.copy(TEST_FILE_PATH, dest)

    for _ in range(nb_import):
        upload_alto_file(
            path=dest,
            client=api_client,
            iiif_base_url=IIIF_BASE_URL,
            parent_id=PARENT_ID,
            types_dict=None,
            create_types=True,
            worker_run_id=worker_run["id"],
        )

    assert list(ImageServer.select().dicts()) == [
        {
            "id": 5,
            "url": IIIF_BASE_URL,
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
            "url": IIIF_BASE_URL + "tests%2Fsamples%2Fpage_image.jpg",
            "width": 800,
            "height": 1200,
        }
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
            "name": "ALTO upload from CLI",
            "type": "folder",
            "image": None,
            "polygon": None,
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "P1",
            "type": "page",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[0, 0], [0, 1200], [800, 1200], [800, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "RM_1",
            "type": "rightmargin",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[0, 0], [0, 1100], [30, 1100], [30, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "PS_1",
            "type": "printspace",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[0, 0], [0, 1010], [650, 1010], [650, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TB_1",
            "type": "textblock",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[0, 0], [0, 400], [650, 400], [650, 0], [0, 0]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TB_2",
            "type": "textblock",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[0, 410], [0, 760], [650, 760], [650, 410], [0, 410]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TL_1",
            "type": "textline",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[200, 250], [200, 290], [550, 290], [550, 250], [200, 250]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TL_2",
            "type": "textline",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[210, 300], [210, 335], [560, 335], [560, 300], [210, 300]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TL_3",
            "type": "textline",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[200, 550], [200, 590], [550, 590], [550, 550], [200, 550]]",
            "confidence": None,
            "rotation_angle": 0,
            "mirrored": 0,
            "worker_run": worker_run["id"],
        },
        {
            "name": "TL_4",
            "type": "textline",
            "image": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "polygon": "[[190, 600], [190, 650], [540, 650], [540, 600], [190, 600]]",
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
        {"ordering": 0, "parent_name": "ALTO upload from CLI", "child_name": "P1"},
        {"ordering": 0, "parent_name": "P1", "child_name": "RM_1"},
        {"ordering": 1, "parent_name": "P1", "child_name": "PS_1"},
        {"ordering": 0, "parent_name": "PS_1", "child_name": "TB_1"},
        {"ordering": 1, "parent_name": "PS_1", "child_name": "TB_2"},
        {"ordering": 0, "parent_name": "TB_1", "child_name": "TL_1"},
        {"ordering": 1, "parent_name": "TB_1", "child_name": "TL_2"},
        {"ordering": 0, "parent_name": "TB_2", "child_name": "TL_3"},
        {"ordering": 1, "parent_name": "TB_2", "child_name": "TL_4"},
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
        {
            "orientation": "horizontal-lr",
            "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "P1",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en Asie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "PS_1",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermogène qui vient de rentrer à la Villa après un assez long voyage en A-",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "orientation": "horizontal-lr",
            "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée. Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Mon cher Marc, Je suis descendu ce matin chez mon médecin Hermo-",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TL_1",
        },
        {
            "orientation": "horizontal-lr",
            "text": "gène qui vient de rentrer à la Villa après un assez long voyage en A-",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TL_2",
        },
        {
            "orientation": "horizontal-lr",
            "text": "sie. L'examen devait se faire à jeun : nous avions pris rendez-vous pour les premières heures de la matinée.",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TL_3",
        },
        {
            "orientation": "horizontal-lr",
            "text": "Je me suis couché sur un lit après m'être dépouillé de mon manteau et de ma tunique.",
            "confidence": 1.0,
            "worker_run": worker_run["id"],
            "element_name": "TL_4",
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
            "name": "Alto ID",
            "value": "P1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "P1",
        },
        {
            "name": "Alto ID",
            "value": "RM_1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "RM_1",
        },
        {
            "name": "Alto ID",
            "value": "PS_1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "PS_1",
        },
        {
            "name": "Alto ID",
            "value": "TB_1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Fontfamily",
            "value": "Times New Roman",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Fontsize",
            "value": "20",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Align",
            "value": "Block",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Description",
            "value": "Début",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Type",
            "value": "Structural",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_1",
        },
        {
            "name": "Alto ID",
            "value": "TB_2",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Fontfamily",
            "value": "Times New Roman",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Fontsize",
            "value": "20",
            "type": "numeric",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Align",
            "value": "Block",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Description",
            "value": "Fin",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Type",
            "value": "Structural",
            "type": "text",
            "worker_run": worker_run["id"],
            "element_name": "TB_2",
        },
        {
            "name": "Alto ID",
            "value": "TL_1",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TL_1",
        },
        {
            "name": "Alto ID",
            "value": "TL_2",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TL_2",
        },
        {
            "name": "Alto ID",
            "value": "TL_3",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TL_3",
        },
        {
            "name": "Alto ID",
            "value": "TL_4",
            "type": "reference",
            "worker_run": worker_run["id"],
            "element_name": "TL_4",
        },
    ]

    database.close()
    assert not db.is_available()
