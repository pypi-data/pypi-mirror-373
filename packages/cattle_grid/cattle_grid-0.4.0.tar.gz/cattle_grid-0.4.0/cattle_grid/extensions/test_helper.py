from .examples.simple_storage import extension

from .helper import async_schema_for_extension, openapi_schema_for_extension


def test_async_schema():
    async_schema_for_extension(extension)


def test_openapi_schema():
    result = openapi_schema_for_extension(extension)

    assert isinstance(result, dict)
