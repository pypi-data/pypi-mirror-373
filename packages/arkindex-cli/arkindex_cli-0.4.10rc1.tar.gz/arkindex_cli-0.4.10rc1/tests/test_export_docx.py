import argparse
from pathlib import Path

import pytest

from arkindex_cli.commands.export import add_export_parser
from arkindex_cli.commands.export.docx import get_transcription
from arkindex_cli.commands.export.utils import MANUAL_SOURCE
from arkindex_export import Element, open_database

DB_PATH = Path("/path/to/db.sqlite")


@pytest.fixture
def mock_db_path(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)


@pytest.mark.parametrize(
    "arguments,message",
    [
        (
            [
                "export",
                "/path/to/db.sqlite",
                "docx",
                "--folder-ids",
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "--folder-type",
                "volume",
            ],
            "argument --folder-type: not allowed with argument --folder-ids",
        ),
        (
            [
                "export",
                "/path/to/db.sqlite",
                "docx",
                "--worker-run-id",
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                MANUAL_SOURCE,
                "--worker-version-id",
                "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            ],
            "argument --worker-version-id: not allowed with argument --worker-run-id",
        ),
        (
            [
                "export",
                "/path/to/db.sqlite",
                "docx",
                "--worker-run-id",
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "run run run",
            ],
            "--worker-run-id: invalid uuid_or_manual value: 'run run run'",
        ),
        (
            [
                "export",
                "/path/to/db.sqlite",
                "docx",
                "--worker-version-id",
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "unit 00",
            ],
            "--worker-version-id: invalid uuid_or_manual value: 'unit 00'",
        ),
        (
            [
                "export",
                "/path/to/db.sqlite",
                "docx",
                "--folder-ids",
                "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "unit 00",
            ],
            "--folder-ids: invalid UUID value: 'unit 00'",
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
    "worker_version_ids,worker_run_ids,expected_transcription",
    [
        (
            [MANUAL_SOURCE],
            [],
            "例えばいつか違う世界で 生まれ変わっても\\n僕らはそれぞれ 同じように出会い\\n同じように貴方を愛すでしょう",
        ),
        (
            [],
            [MANUAL_SOURCE],
            "例えばいつか違う世界で 生まれ変わっても\\n僕らはそれぞれ 同じように出会い\\n同じように貴方を愛すでしょう",
        ),
        (
            ["worker_id1"],
            [],
            "一歩づつでいいさ この手を離さずに\\n共に歩んだ日々が 生きつづけてるから\\nボロボロになるまで 引きさかれていても\\nあの時のあの場所 消えないこの絆",
        ),
        (
            [],
            ["run_2"],
            "SI俺達はあの頃 辿り着いたこの街 全てが手に入る 気がした\\nSI故郷を捨て去り でかい夢を追いかけ 笑って生きてきた",
        ),
        (
            [MANUAL_SOURCE, "worker_id2"],
            [],
            "例えばいつか違う世界で 生まれ変わっても\\n僕らはそれぞれ 同じように出会い\\n同じように貴方を愛すでしょう",
        ),
        (
            [],
            ["run_2", MANUAL_SOURCE],
            "SI俺達はあの頃 辿り着いたこの街 全てが手に入る 気がした\\nSI故郷を捨て去り でかい夢を追いかけ 笑って生きてきた",
        ),
        (
            ["worker_id3", MANUAL_SOURCE],
            [],
            "例えばいつか違う世界で 生まれ変わっても\\n僕らはそれぞれ 同じように出会い\\n同じように貴方を愛すでしょう",
        ),
        (["worker_id3"], [], None),
    ],
)
def test_get_transcriptions(
    worker_version_ids, worker_run_ids, expected_transcription, export_db_path
):
    open_database(export_db_path)
    transcription = get_transcription(
        worker_version_ids,
        worker_run_ids,
        Element(id="ad9639eb-91c7-450d-b5f2-3b755cef5662", type="page"),
    )
    assert transcription == expected_transcription


@pytest.mark.parametrize(
    "worker_version_ids,worker_run_ids",
    [([], []), ([MANUAL_SOURCE], []), (["worker_id1"], [])],
)
def test_multiple_transcriptions_error(
    worker_version_ids, worker_run_ids, export_db_path
):
    open_database(export_db_path)
    with pytest.raises(Exception, match="Multiple transcriptions returned"):
        get_transcription(
            worker_version_ids,
            worker_run_ids,
            Element(id="c0016dda-dfd9-486e-a19e-1e2785446e94", type="page"),
        )
