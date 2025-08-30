import click

from .cli import add_extension_commands


@click.group()
@click.pass_context
def main(ctx):
    """Tooling for managing extensions"""

    ctx.ensure_object(dict)


add_extension_commands(main)

if __name__ == "__main__":
    main()
