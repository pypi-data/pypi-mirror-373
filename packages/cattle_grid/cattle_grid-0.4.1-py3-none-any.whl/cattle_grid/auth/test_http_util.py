import pytest

from .http_util import should_serve, ContentType


@pytest.mark.parametrize(
    "header,expected",
    [
        ("", []),
        ("text/html", [ContentType.html]),
        ("application/activity+json", [ContentType.activity_pub]),
    ],
)
def test_should_serve(header, expected):
    assert should_serve(header) == expected


def test_none_as_header():
    assert should_serve(None) == [ContentType.other]
