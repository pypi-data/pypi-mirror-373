import pytest


from .recipients import extension as recipients_extension
from .webfinger_lookup import extension as webfinger_lookup_extension
from .cache import extension as cache_extension
from .simple_storage import extension as simple_storage_extension


@pytest.mark.parametrize(
    "extension",
    [
        recipients_extension,
        webfinger_lookup_extension,
        cache_extension,
        simple_storage_extension,
    ],
)
def test_factory(extension):
    extension.configure({})
