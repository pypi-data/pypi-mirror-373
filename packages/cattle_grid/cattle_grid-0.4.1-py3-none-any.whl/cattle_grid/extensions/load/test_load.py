from cattle_grid.extensions import Extension
from . import load_extension, build_transformer


def test_load_extension():
    result = load_extension({"module": "cattle_grid.extensions.examples.recipients"})

    assert isinstance(result, Extension)


def test_load_extension_set_options():
    result = load_extension(
        {"module": "cattle_grid.extensions.examples.recipients", "lookup_order": 10}
    )

    assert isinstance(result, Extension)
    assert result.lookup_order == 10


async def test_build_transformer():
    extensions = [
        load_extension({"module": "cattle_grid.extensions.examples.recipients"})
    ]

    transformer = build_transformer(extensions)

    result = await transformer({"raw": {}})

    assert "recipients" in result
