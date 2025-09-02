from arkindex_cli.commands.export.entities import retrieve_transcription_entities
from arkindex_export import open_database


def test_export_entities_no_filters(export_db_path):
    open_database(export_db_path)
    assert list(
        retrieve_transcription_entities("http://instance.teklia.com/", None, [])
    ) == [
        {
            "transcription_id": "traid1",
            "element_id": "b53a8dbd-3135-4540-87f0-e08a9a396e11",
            "element_url": "http://instance.teklia.com/element/b53a8dbd-3135-4540-87f0-e08a9a396e11",
            "transcription_entity_id": "9a0ec675-7d1a-4019-ab73-367d8471dea8",
            "entity_value": "satra",
            "entity_type": "entitytype1",
            "confidence": None,
            "offset": 3,
            "length": 5,
        },
        {
            "transcription_id": "traid2",
            "element_id": "ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "element_url": "http://instance.teklia.com/element/ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "transcription_entity_id": "a24d3d72-59d1-4b25-9186-7d5842cf4b8b",
            "entity_value": "isnext",
            "entity_type": "entitytype1",
            "confidence": None,
            "offset": 2,
            "length": 6,
        },
        {
            "transcription_id": "traid4",
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "0d97030b-7567-4335-8aa2-30b23387583d",
            "entity_value": "page",
            "entity_type": "entitytype2",
            "confidence": 1.0,
            "offset": 0,
            "length": 4,
        },
        {
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "1b30712c-5b8f-4d68-99b6-7eba5eed9667",
            "entity_type": "entitytype1",
            "entity_value": "page",
            "confidence": 0.12,
            "length": 4,
            "offset": 20,
            "transcription_id": "traid4",
        },
        {
            "transcription_id": "traid4",
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "c8dfd65a-c384-473e-a17e-6dc3655ce273",
            "entity_value": "transcription",
            "entity_type": "entitytype1",
            "confidence": 0.3,
            "offset": 4,
            "length": 13,
        },
        {
            "transcription_id": "traid5",
            "element_id": "7605faf7-b316-423e-b2c1-b6d845dba4bd",
            "element_url": "http://instance.teklia.com/element/7605faf7-b316-423e-b2c1-b6d845dba4bd",
            "transcription_entity_id": "3ef5c4a8-cd76-4527-80e3-73cf75920e3e",
            "entity_value": "e suis d",
            "entity_type": "entitytype3",
            "confidence": None,
            "offset": 15,
            "length": 8,
        },
        {
            "transcription_id": "traid6",
            "element_id": "ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "element_url": "http://instance.teklia.com/element/ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "transcription_entity_id": "e78bbae2-1c68-4357-8627-25e2462f0716",
            "entity_value": " to me",
            "entity_type": "entitytype2",
            "confidence": 0.96,
            "offset": 4,
            "length": 6,
        },
    ]


def test_export_entities_type_filter(export_db_path):
    open_database(export_db_path)
    assert list(
        retrieve_transcription_entities("http://instance.teklia.com/", "page", [])
    ) == [
        {
            "transcription_id": "traid4",
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "0d97030b-7567-4335-8aa2-30b23387583d",
            "entity_value": "page",
            "entity_type": "entitytype2",
            "confidence": 1.0,
            "offset": 0,
            "length": 4,
        },
        {
            "transcription_id": "traid4",
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "1b30712c-5b8f-4d68-99b6-7eba5eed9667",
            "entity_type": "entitytype1",
            "entity_value": "page",
            "confidence": 0.12,
            "length": 4,
            "offset": 20,
        },
        {
            "transcription_id": "traid4",
            "element_id": "a87884d1-5233-4207-9b02-66bbe494da84",
            "element_url": "http://instance.teklia.com/element/a87884d1-5233-4207-9b02-66bbe494da84",
            "transcription_entity_id": "c8dfd65a-c384-473e-a17e-6dc3655ce273",
            "entity_value": "transcription",
            "entity_type": "entitytype1",
            "confidence": 0.3,
            "offset": 4,
            "length": 13,
        },
    ]


def test_export_entities_worker_version_filter(export_db_path):
    open_database(export_db_path)
    assert list(
        retrieve_transcription_entities(
            "http://instance.teklia.com/", None, ["worker_id2"]
        )
    ) == [
        {
            "transcription_id": "traid2",
            "element_id": "ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "element_url": "http://instance.teklia.com/element/ccc04dfe-39af-4118-bb56-3aaf0350ba8b",
            "transcription_entity_id": "a24d3d72-59d1-4b25-9186-7d5842cf4b8b",
            "entity_value": "isnext",
            "entity_type": "entitytype1",
            "confidence": None,
            "offset": 2,
            "length": 6,
        },
        {
            "transcription_id": "traid5",
            "element_id": "7605faf7-b316-423e-b2c1-b6d845dba4bd",
            "element_url": "http://instance.teklia.com/element/7605faf7-b316-423e-b2c1-b6d845dba4bd",
            "transcription_entity_id": "3ef5c4a8-cd76-4527-80e3-73cf75920e3e",
            "entity_value": "e suis d",
            "entity_type": "entitytype3",
            "confidence": None,
            "offset": 15,
            "length": 8,
        },
    ]


def test_export_entities_all_filters(export_db_path):
    open_database(export_db_path)
    assert (
        retrieve_transcription_entities(
            "http://instance.teklia.com/", "page", ["worker_id2"]
        )
        == []
    )
