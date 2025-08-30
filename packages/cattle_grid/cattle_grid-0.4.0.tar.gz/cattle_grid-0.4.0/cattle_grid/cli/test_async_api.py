import pytest

from fastapi import FastAPI

from cattle_grid.testing.fixtures import *  # noqa

from . import (
    async_api_components,
    async_api_schema_for_component,
    fastapi_for_component,
    fastapi_components,
)


@pytest.mark.parametrize("component", async_api_components)
def test_async_api_schema(component, sql_engine_for_tests):
    schema = async_api_schema_for_component(component)
    assert isinstance(schema, str)


@pytest.mark.parametrize("component", fastapi_components)
def test_fastapi_for_component(component, sql_engine_for_tests):
    schema = fastapi_for_component(component)
    assert isinstance(schema, FastAPI)
