import click
import tomli_w
from .util import blocklist_form_url_or_file


def save_block_list(block_list, filename="cattle_grid_block_list.toml"):
    with open(filename, "wb") as fp:
        tomli_w.dump({"domain_block": list(block_list)}, fp)


def add_block_command(main):
    @main.group()
    @click.pass_context
    def block(ctx):
        """Allows management of the level 0 blocklist of cattle_grid.
        These are the instances that you consider so bad you want them
        blocked on the lowest level possible."""
        if "config" not in ctx.obj:
            print("Could not load config and it is necessary for blocklist management")
            exit(1)

    @block.command()  # type:ignore
    @click.pass_context
    def empty(ctx):
        """Sets the blocklist to the empty set"""
        ctx.obj["config"].domain_blocks = set()

        save_block_list(set(), filename=ctx.obj["config_file_block_list"])

        exit(0)

    @block.command("list")  # type:ignore
    @click.pass_context
    def list_blocks(ctx):
        """Prints the current blockllist in alphabetical order"""
        blocks = ctx.obj["config"].domain_blocks
        blocks = sorted(blocks)

        for x in blocks:
            print(x)

    @block.command()  # type:ignore
    @click.argument("domain")
    @click.pass_context
    def add(ctx, domain):
        """Adds domain to the current list of domain blocks"""
        ctx.obj["config"].auth.domain_blocks = ctx.obj["config"].auth.domain_blocks | {
            domain
        }
        save_block_list(set(), filename=ctx.obj["config_file_block_list"])

    @block.command()  # type:ignore
    @click.argument("domain")
    @click.pass_context
    def remove(ctx, domain):
        """Removes domain from the current list of domain blocks"""
        ctx.obj["config"].auth.domain_blocks = ctx.obj["config"].auth.domain_blocks - {
            domain
        }
        save_block_list(set(), filename=ctx.obj["config_file_block_list"])

    @block.command()  # type:ignore
    @click.option(
        "--source",
        help="URL or file to import blocklist from",
        default="https://seirdy.one/pb/FediNuke.txt",
    )
    @click.pass_context
    def compare(ctx, source):
        """Compares the current block list with the one provided by source"""
        blocks = blocklist_form_url_or_file(source)
        current = ctx.obj["config"].auth.domain_blocks

        print(f"New blocks in source ({source}):")
        for x in blocks - current:
            print(x)
        print()
        print("Blocks not in source:")
        for x in current - blocks:
            print(x)
        print()

    @block.command("import")  # type:ignore
    @click.option(
        "--source",
        help="URL or file to import blocklist from",
        default="https://seirdy.one/pb/FediNuke.txt",
    )
    @click.option(
        "--overwrite",
        help="Use to overwrite the existing blocklist instead of just adding to it",
        is_flag=True,
        default=False,
    )
    @click.pass_context
    def import_from_source(ctx, source, overwrite):
        """Imports the blocklist from source. By default the blocklist is merged with current one. By specifying the allow flag, one can overwrite the current blocklist."""
        blocks = blocklist_form_url_or_file(source)

        if overwrite:
            ctx.obj["config"].auth.domain_blocks = blocks
        else:
            ctx.obj["config"].auth.domain_blocks = (
                blocks | ctx.obj["config"].auth.domain_blocks
            )
        save_block_list(set(), filename=ctx.obj["config_file_block_list"])

    return block
