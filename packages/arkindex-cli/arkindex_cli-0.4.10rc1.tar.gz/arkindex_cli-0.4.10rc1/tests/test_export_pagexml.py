import logging
from uuid import UUID

import pytest

from arkindex_cli.commands.export.pagexml import run
from arkindex_export import database


def test_export_pagexml_multiple_transcriptions_error(tmp_path, fixtures_dir, caplog):
    caplog.set_level(logging.INFO)

    output = tmp_path / "pagexml"
    output.mkdir()

    with pytest.raises(SystemExit):
        run(
            database_path=fixtures_dir / "pagexml.sqlite",
            output_path=output,
            parent=None,
            page_type="page",
            paragraph_type=None,
            line_type="text_line",
            transcription_source=None,
        )

    assert caplog.record_tuples == [
        (
            "arkindex_cli.commands.export.pagexml",
            logging.INFO,
            f'Created PageXML file at {output / "981d1e76-79c4-43e1-a982-1617338da9f7.xml"}',
        ),
        (
            "arkindex_cli.commands.export.pagexml",
            logging.ERROR,
            "Found 2 transcriptions on text_line 3 (c7ac41b0-2753-41fe-8a3d-aa788507aaf3) from page 2 (0310d5e8-94f5-4efb-b4d7-fc6417a1b059).",
        ),
    ]

    database.close()


@pytest.mark.parametrize("parent", [None, UUID("177a971a-4889-44c1-b5d6-c5a09fb4452e")])
@pytest.mark.parametrize("paragraph_type", [None, "paragraph"])
def test_export_pagexml(
    mocker, tmp_path, fixtures_dir, samples_dir, caplog, parent, paragraph_type
):
    caplog.set_level(logging.INFO)

    mocker.patch(
        "arkindex_cli.commands.export.pagexml.get_now",
        return_value="2024-06-13T11:13:24",
    )

    output = tmp_path / "pagexml"
    output.mkdir()

    run(
        database_path=fixtures_dir / "pagexml.sqlite",
        output_path=output,
        parent=parent,
        page_type="page",
        paragraph_type=paragraph_type,
        line_type="text_line",
        transcription_source=UUID("4aaadb8f-0ea2-455c-9030-2b9a3df05c37"),
    )

    expected_file_names = [
        "981d1e76-79c4-43e1-a982-1617338da9f7.xml",
        "0310d5e8-94f5-4efb-b4d7-fc6417a1b059.xml",
    ]

    assert sorted(output.rglob("*")) == sorted(
        [output / file_name for file_name in expected_file_names]
    )

    for index, file_name in enumerate(expected_file_names):
        expected_file = samples_dir / "pagexml_export" / file_name
        if paragraph_type and index == 1:
            expected_file = (
                expected_file.parent / f"{expected_file.stem}_paragraphs.xml"
            )

        actual_file = output / file_name
        assert expected_file.read_text() == actual_file.read_text()

    assert caplog.record_tuples == [
        (
            "arkindex_cli.commands.export.pagexml",
            logging.INFO,
            f"Created PageXML file at {output / file_name}",
        )
        for file_name in expected_file_names
    ]

    database.close()
