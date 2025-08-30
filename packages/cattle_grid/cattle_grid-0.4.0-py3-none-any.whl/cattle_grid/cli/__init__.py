from fastapi import FastAPI

async_api_components: list[str] = ["exchange", "ap", "account"]
fastapi_components: list[str] = ["auth", "ap", "account", "rabbit", "app"]

filenames_for_component: dict[str, str] = {
    name: f"docs/assets/schemas/asyncapi_{name}.json" for name in async_api_components
}

filenames_for_openapi_components: dict[str, str] = {
    name: f"docs/assets/schemas/openapi_{name}.json"
    for name in fastapi_components
    if name != "app"
} | {"app": "docs/assets/schemas/openapi.json"}


def async_api_schema_for_component(component: str) -> str:
    if component == "ap":
        from cattle_grid.activity_pub import get_async_api_schema
    elif component == "account":
        from cattle_grid.account.router.schema import get_async_api_schema
    else:
        from cattle_grid.exchange import get_async_api_schema

    schema = get_async_api_schema().to_json()

    return schema


def fastapi_for_component(component: str) -> FastAPI:
    match component:
        case "auth":
            from cattle_grid.auth import create_app

            app = create_app()
        case "ap":
            from cattle_grid.activity_pub import get_fastapi_app

            app = get_fastapi_app()
        case "account":
            from cattle_grid.account.server.app import app
        case "rabbit":
            from cattle_grid.account.rabbit import app_for_schema

            app = app_for_schema()
        case _:
            from cattle_grid import create_app

            app = create_app()

    return app
