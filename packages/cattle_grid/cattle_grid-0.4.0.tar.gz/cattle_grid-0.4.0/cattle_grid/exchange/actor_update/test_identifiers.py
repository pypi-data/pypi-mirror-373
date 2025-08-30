import pytest

from .identifiers import is_identifier_part_of_base_urls, is_identifier_for_a_base_url


@pytest.mark.parametrize(
    "identifier, base_urls, expected",
    [
        ("acct:test@one.test", ["http://one.test"], True),
        ("acct:test@two.test", ["http://one.test"], False),
    ],
)
def test_is_identifier_part_of_base_urls(identifier, base_urls, expected):
    assert is_identifier_part_of_base_urls(identifier, base_urls) == expected


@pytest.mark.parametrize(
    "identifier, base_urls, expected",
    [
        ("acct:test@one.test", ["http://one.test"], True),
        ("acct:test@two.test", ["http://one.test"], False),
        ("http://one.test/actor", ["http://one.test"], True),
        ("http://two.test/actor", ["http://one.test"], False),
        ("https://one.test/actor", ["http://one.test"], True),
        ("https://two.test/actor", ["http://one.test"], False),
    ],
)
def test_is_identifier_for_a_base_url(identifier, base_urls, expected):
    assert is_identifier_for_a_base_url(identifier, base_urls) == expected
