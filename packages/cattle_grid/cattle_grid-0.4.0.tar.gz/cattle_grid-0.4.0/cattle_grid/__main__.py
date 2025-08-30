import click
import asyncio
import logging
from pathlib import Path

from cattle_grid.config import load_settings
from .statistics import statistics
from .auth.__main__ import add_auth_commands
from .auth.block_cli import add_block_command
from .auth.key_cli import add_keys_command
from .actors import add_actors_to_cli_as_group
from .extensions.cli import add_extension_commands_as_group
from .account.cli import add_account_commands

from .cli import (
    filenames_for_component,
    async_api_schema_for_component,
    fastapi_for_component,
    filenames_for_openapi_components,
)

logger = logging.getLogger(__name__)


@click.group()
@click.option("--config_file", default="cattle_grid.toml")
@click.pass_context
def main(ctx, config_file):
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config_file

    try:
        ctx.obj["config"] = load_settings(config_file)
    except Exception as e:
        logger.Exception(e)


@main.command()
@click.pass_context
def stat(ctx):
    """Displays statistical information about cattle_grid"""
    asyncio.run(statistics(ctx.obj["config"]))


@main.command()
@click.option("--db_uri")
@click.option("--name")
@click.pass_context
def create_db_migration(ctx, db_uri, name):
    """Creates a database migration; run after editing models"""
    from .database import migrate

    config = ctx.obj["config"]

    if db_uri:
        config.db_uri = db_uri

    asyncio.run(migrate(config, name))


@main.command()
@click.option("--db_uri")
@click.pass_context
def upgrade_db(ctx, db_uri):
    from .database import upgrade

    config = ctx.obj["config"]

    if db_uri:
        config.db_uri = db_uri

    asyncio.run(upgrade(config))


@main.command()
@click.option("--filename", default="asyncapi.json")
@click.option(
    "--for_docs",
    is_flag=True,
    default=False,
    help="Generate schema for use in documentation",
)
@click.option(
    "--component",
    default="exchange",
    help="Restrict to a component. Currently allowed ap",
)
def async_api(filename: str, for_docs: bool, component: str):
    if for_docs:
        Path("./docs/assets/schemas").mkdir(parents=True, exist_ok=True)
        to_process = filenames_for_component
    else:
        to_process = {component: filename}

    for component, filename in to_process.items():
        schema = async_api_schema_for_component(component)

        with open(filename, "w") as fp:
            fp.write(schema)


@main.command()
@click.option("--filename", default="openapi.json")
@click.option(
    "--for_docs",
    is_flag=True,
    default=False,
    help="Generate schema for use in documentation",
)
@click.option(
    "--component",
    default=None,
    help="Restrict to a component. Currently allowed auth or ap",
)
def openapi(filename: str, for_docs: bool, component):
    import json

    if for_docs:
        Path("./docs/assets/schemas").mkdir(parents=True, exist_ok=True)
        to_process = filenames_for_openapi_components
    else:
        to_process = {component: filename}

    for component, filename in to_process.items():
        app = fastapi_for_component(component)

        with open(filename, "w") as fp:
            json.dump(app.openapi(), fp)


add_auth_commands(main)
add_block_command(main)
add_keys_command(main)
add_extension_commands_as_group(main)
add_account_commands(main)
add_actors_to_cli_as_group(main)

if __name__ == "__main__":
    main()
