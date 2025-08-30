import pytest
from .property_value import find_key_in_attachments


@pytest.mark.parametrize(
    "attachments, expected",
    [
        ([], None),
        (["string"], None),
        ([{"name": "string"}], None),
        ([{"name": "key"}], None),
        ([{"type": "PropertyValue", "name": "key"}], 0),
        ([{"type": "PropertyValue", "name": "other"}], None),
    ],
)
def test_find_key_in_attachments(attachments, expected):
    assert find_key_in_attachments(attachments, "key") == expected
