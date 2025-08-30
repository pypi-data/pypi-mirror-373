import uuid

from .config import SimpleStorageConfiguration


def test_make_id():
    config = SimpleStorageConfiguration(prefix="/simple/storage/")

    new_id, new_uuid = config.make_id("http://alice.example/some/path")

    expected_start = "http://alice.example/simple/storage/"

    assert new_id.startswith(expected_start)

    generated_uuid = uuid.UUID(new_id.removeprefix(expected_start))

    assert isinstance(generated_uuid, uuid.UUID)
    assert generated_uuid == new_uuid
