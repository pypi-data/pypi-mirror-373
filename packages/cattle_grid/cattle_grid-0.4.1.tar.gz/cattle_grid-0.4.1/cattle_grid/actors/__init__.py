import asyncio
import click
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.database import run_with_database
from cattle_grid.database.activity_pub_actor import Actor, ActorStatus
from cattle_grid.database.account import ActorForAccount

from cattle_grid.manage import ActorManager


async def list_actors(session: AsyncSession, deleted: bool = False):
    result = await session.scalars(select(Actor))

    if deleted:
        result = [x for x in result if x.status == ActorStatus.deleted]

    count = 0
    for x in result:
        print(x.actor_id)
        count = count + 1

    if count == 0:
        print("No actors")


async def show_actor(session: AsyncSession, actor_id: str):
    manager = ActorManager(session=session, actor_id=actor_id)
    groups = ", ".join(await manager.groups())

    print(f"Actor ID: {actor_id}")
    if groups == "":
        print("Not a member of a group")
    else:
        print(f"Groups: {groups}")
    print()


async def modify_actor(session: AsyncSession, actor_id: str, add_groups: list[str]):
    manager = ActorManager(session=session, actor_id=actor_id)

    for group_name in add_groups:
        await manager.add_to_group(group_name)


async def prune_actors(session: AsyncSession):
    await session.execute(delete(Actor).where(Actor.status == ActorStatus.deleted))
    await session.execute(delete(ActorForAccount).where(ActorForAccount.deleted))


def add_actors_to_cli_as_group(main):
    @main.group()
    def actor():
        """Used to manage actors"""

    add_to_cli(actor)


def add_to_cli(main):
    @main.command("list")  # type: ignore
    @click.option(
        "--deleted", is_flag=True, default=False, help="Only list deleted actors"
    )
    @click.pass_context
    def list_actors_command(ctx, deleted):
        asyncio.run(
            run_with_database(
                ctx.obj["config"], lambda session: list_actors(session, deleted)
            )
        )

    @main.command("prune")  # type: ignore
    @click.pass_context
    def prune_actors_command(ctx):
        asyncio.run(
            run_with_database(ctx.obj["config"], lambda session: prune_actors(session))
        )

    @main.command("show")  # type: ignore
    @click.argument("actor_id")
    @click.pass_context
    def show_actor_command(ctx, actor_id):
        asyncio.run(
            run_with_database(
                ctx.obj["config"], lambda session: show_actor(session, actor_id)
            )
        )

    @main.command("modify")  # type: ignore
    @click.argument("actor_id")
    @click.option("--add_group", multiple=True, default=[])
    @click.pass_context
    def modify_actor_command(ctx, actor_id, add_group):
        """Adds a group to the actor"""
        asyncio.run(
            run_with_database(
                ctx.obj["config"],
                lambda session: modify_actor(session, actor_id, add_group),
            )
        )
