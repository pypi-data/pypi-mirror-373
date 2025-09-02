import pytest

from arkindex_cli.commands.export.alto import run
from arkindex_export import database


@pytest.mark.parametrize("mets", [True, False])
def test_export_alto_mets(
    tmp_path,
    fixtures_dir,
    samples_dir,
    mets,
):
    output = tmp_path / "alto"
    output.mkdir()

    folder_id = "177a971a-4889-44c1-b5d6-c5a09fb4452e"
    run(
        database_path=fixtures_dir / "alto.sqlite",
        output_path=output,
        folder_type="folder",
        page_type="page",
        line_type="text_line",
        mets=mets,
    )

    expected_file_names = [
        "0310d5e8-94f5-4efb-b4d7-fc6417a1b059.xml",
        "981d1e76-79c4-43e1-a982-1617338da9f7.xml",
    ]
    if mets:
        expected_file_names.append("mets_entrypoint.xml")

    assert sorted(output.rglob("*")) == [output / folder_id] + [
        output / folder_id / file_name for file_name in expected_file_names
    ]

    for file_name in expected_file_names:
        expected_file = samples_dir / "alto_export" / file_name
        actual_file = output / folder_id / file_name
        assert (
            # Stored files are formatted to be more readable,
            # but the generated files are only one line long
            "".join(
                [
                    line.strip()
                    for line in expected_file.read_text()
                    .format(path=str(output))
                    .split("\n")
                ]
            )
            == actual_file.read_text()
        )

    database.close()
