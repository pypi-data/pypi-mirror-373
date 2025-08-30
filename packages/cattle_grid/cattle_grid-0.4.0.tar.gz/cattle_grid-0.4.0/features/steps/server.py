import jsonschema
import json


from behave import then, when, given

from urllib.parse import urljoin

from bovine.models import JrdData


@given("A Fediverse server")
def fediverse_server(context):
    context.server = "http://abel"


@when('Querying "{path}"')
async def query_path(context, path):
    response = await context.session.get(urljoin(context.server, path))

    response.raise_for_status()
    context.response_body = await response.json()


@then('The jrd links contain one of type "{link_type}"')
def parse_jrd_links(context, link_type):
    data = JrdData.model_validate(context.response_body)

    value = None
    for link in data.links:
        if link.type == link_type:
            value = link.href

    assert value, f"Link not found in JRD {context.response_body}"

    context.link_to_resolve = value


@then("This page can be resolved")
async def can_resolve_page(context):
    response = await context.session.get(context.link_to_resolve)

    response.raise_for_status()
    context.result = await response.json()


@then('The result obeys the schema given by "{schema_url}"')
async def validate_against_schema(context, schema_url):
    response = await context.session.get(
        schema_url, headers={"accept": "application/json"}
    )
    schema = json.loads(await response.text())

    jsonschema.validate(context.result, schema)
