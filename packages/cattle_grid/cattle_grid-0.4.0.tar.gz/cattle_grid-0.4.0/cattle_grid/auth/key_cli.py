import asyncio
import click
from sqlalchemy import delete

from cattle_grid.database import database_session

from cattle_grid.database.auth import RemoteIdentity


async def prune_keys(config):
    try:
        async with database_session(config.db_uri) as session:
            await session.execute(delete(RemoteIdentity))
    except Exception:
        print("Failed to purge remote identifiers")


def add_keys_command(main):
    @main.group()
    @click.pass_context
    def keys(ctx):
        """Allows the management of public keys"""
        if "config" not in ctx.obj:
            print("Could not load config and it is necessary for keys management")
            exit(1)

    @keys.command()  # type:ignore
    @click.option(
        "--all_flag", help="Remove all known public keys", default=False, is_flag=True
    )
    @click.pass_context
    def clear(ctx, all_flag):
        try:
            if all_flag:
                asyncio.run(prune_keys(ctx.obj["config"]))
            else:
                click.echo(
                    "Currently only remove all keys is supported. If you want to do this run with the --all_flag"
                )
        except Exception as e:
            print(e)
