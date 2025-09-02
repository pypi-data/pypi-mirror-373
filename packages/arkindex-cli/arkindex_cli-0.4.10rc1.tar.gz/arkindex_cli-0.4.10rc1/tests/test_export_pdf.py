import pytest
from reportlab.pdfgen import canvas

from arkindex_cli.commands.export.pdf import (
    get_children_elements,
    image_draw,
    list_folders,
)
from arkindex_export import Element, open_database


@pytest.mark.parametrize(
    "page_element,expected",
    [
        (
            Element(
                id="pageid1",
                name="pagename1",
                type="page",
                polygon="[[0, 0], [0, 110], [110, 110], [110, 0], [0, 0]]",
                worker_version="workerversion1",
            ),
            (110, 110),
        ),
        (
            Element(
                id="pageid1",
                name="pagename1",
                type="page",
                polygon="[[0, 0], [0, 219], [230, 219], [230, 0], [0, 0]]",
                worker_version="workerversion1",
            ),
            (230, 219),
        ),
    ],
)
def test_image_draw(tmp_path, samples_dir, page_element, expected):
    """
    Tests correct starting coordinates, width and height is return from polygon
    coordinates
    """
    image_path = samples_dir / "image.jpg"
    c = canvas.Canvas(tmp_path / "testpdf")
    assert image_draw(page_element, image_path, c, tmp_path) == expected


@pytest.mark.parametrize(
    "folder_type,folder_ids,expected",
    [
        (
            "folder",
            None,
            [
                "b6f57a29-7260-410a-8d21-6633bae6842c",
                "9d503c00-adf1-4f03-9818-51fe18f4f5ad",
            ],
        ),
        (
            "folder",
            [],
            [
                "b6f57a29-7260-410a-8d21-6633bae6842c",
                "9d503c00-adf1-4f03-9818-51fe18f4f5ad",
            ],
        ),
        ("volume", None, ["f7b1801e-d4bf-42c6-be68-5a3a45fe2aa8"]),
        (
            "folder",
            ["b6f57a29-7260-410a-8d21-6633bae6842c"],
            ["b6f57a29-7260-410a-8d21-6633bae6842c"],
        ),
        (
            "folder",
            [
                "b6f57a29-7260-410a-8d21-6633bae6842c",
                "f7b1801e-d4bf-42c6-be68-5a3a45fe2aa8",
            ],
            ["b6f57a29-7260-410a-8d21-6633bae6842c"],
        ),
    ],
)
def test_list_folders(export_db_path, folder_type, folder_ids, expected):
    open_database(export_db_path)
    assert [
        item.id for item in list_folders(folder_type=folder_type, folder_ids=folder_ids)
    ] == expected


@pytest.mark.parametrize(
    "folder_id,page_type,order_by_name,expected",
    [
        ("f7b1801e-d4bf-42c6-be68-5a3a45fe2aa8", "page", False, []),
        (
            "b6f57a29-7260-410a-8d21-6633bae6842c",
            "page",
            False,
            [
                "a87884d1-5233-4207-9b02-66bbe494da84",
                "9a3b3818-5b3d-40d5-9e4f-b0d444884455",
                "1c133d38-0a39-4bc2-add9-c63d6f4836b2",
                "1edb51e5-217d-4d67-8768-39e7f0aca143",
            ],
        ),
        (
            "b6f57a29-7260-410a-8d21-6633bae6842c",
            "page",
            True,
            [
                "1c133d38-0a39-4bc2-add9-c63d6f4836b2",
                "1edb51e5-217d-4d67-8768-39e7f0aca143",
                "a87884d1-5233-4207-9b02-66bbe494da84",
                "9a3b3818-5b3d-40d5-9e4f-b0d444884455",
            ],
        ),
        (
            "b6f57a29-7260-410a-8d21-6633bae6842c",
            "folder",
            False,
            ["9d503c00-adf1-4f03-9818-51fe18f4f5ad"],
        ),
    ],
)
def test_list_pages(export_db_path, folder_id, page_type, order_by_name, expected):
    open_database(export_db_path)
    assert [
        item.id
        for item in get_children_elements(
            folder_id, page_type, order_by_name=order_by_name
        )
    ] == expected


@pytest.mark.parametrize(
    "parent_id,type,worker_version,expected",
    [
        ("1c133d38-0a39-4bc2-add9-c63d6f4836b2", "text_line", None, []),
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "text_line",
            None,
            [
                "quand nous en serons au temps des cerises",
                "les gais rossignols et merles moqueurs seront tous en fête",
            ],
        ),
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "table_line",
            None,
            ["the world is changed because you are made of ivory and gold"],
        ),
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "text_line",
            "worker_id2",
            ["les gais rossignols et merles moqueurs seront tous en fête"],
        ),
    ],
)
def test_children_transcriptions(
    export_db_path, parent_id, type, worker_version, expected
):
    open_database(export_db_path)
    assert [
        tr.text
        for line in get_children_elements(
            parent_id,
            type,
            with_transcriptions=True,
            transcription_worker_version=worker_version,
        )
        for tr in line.transcription_set
    ] == expected


@pytest.mark.parametrize(
    "folder_id,page_type,order_by_name,worker_version,expected",
    [
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "text_line",
            False,
            None,
            [
                "quand nous en serons au temps des cerises",
                "les gais rossignols et merles moqueurs seront tous en fête",
            ],
        ),
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "table_line",
            False,
            None,
            ["the world is changed because you are made of ivory and gold"],
        ),
        (
            "c24a7c1c-eafe-4795-9d76-508019c9c49b",
            "text_line",
            False,
            "worker_id2",
            ["les gais rossignols et merles moqueurs seront tous en fête"],
        ),
    ],
)
def test_list_pages_with_transcription(
    export_db_path, folder_id, page_type, order_by_name, worker_version, expected
):
    open_database(export_db_path)
    assert [
        item.text
        for elem in get_children_elements(
            folder_id,
            page_type,
            order_by_name=order_by_name,
            with_transcriptions=True,
            transcription_worker_version=worker_version,
        )
        for item in elem.transcription_set
    ] == expected
