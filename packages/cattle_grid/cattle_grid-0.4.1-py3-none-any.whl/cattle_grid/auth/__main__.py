import click
import os
from cattle_grid.config.auth import new_auth_config, save_auth_config


from .block_cli import add_block_command


@click.group()
def auth_cli(): ...


def add_auth_commands(auth_cli):
    @auth_cli.command()
    @click.argument("actor_id", required=True)
    @click.option(
        "--config_file",
        help="Filename to save the configuration to",
        default="cattle_grid_auth.toml",
    )
    @click.option(
        "--username",
        help="Specify a username for the fetch actor. Otherwise it is automatically generated",
    )
    @click.option(
        "--force",
        help="Used to override the old configuration file",
        is_flag=True,
        default=False,
    )
    def new_config(actor_id, config_file, username, force):
        """Creates a new authorization configuration,
        including generating a public and private key.

        Argument is the actor_id for the fetch actor,
        e.g. http://cattle_grid/fetch_actor
        """

        if os.path.exists(config_file) and not force:
            print("Configuration file already exists! Use --force to overwrite.")
            exit(1)

        config = new_auth_config(actor_id, username=username)

        save_auth_config(config_file, config)


add_auth_commands(auth_cli)
add_block_command(auth_cli)

if __name__ == "__main__":
    auth_cli()
