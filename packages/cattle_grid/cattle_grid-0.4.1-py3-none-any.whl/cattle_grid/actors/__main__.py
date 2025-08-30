import click

from cattle_grid.config.settings import get_settings
from . import add_to_cli


@click.group()
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    ctx.obj["config"] = get_settings()


add_to_cli(main)
