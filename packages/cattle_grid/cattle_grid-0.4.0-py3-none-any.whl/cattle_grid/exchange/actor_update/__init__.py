import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.database.account import ActorForAccount
from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.model.exchange import (
    UpdateAction,
    UpdateActionType,
    UpdateIdentifierAction,
    RenameActorAction,
    UpdatePropertyValueAction,
)

from .property_value import handle_update_property_value, handle_delete_property_value
from .identifiers import (
    handle_create_identifier,
    handle_update_identifier,
    handle_add_identifier,
)

logger = logging.getLogger(__name__)


async def handle_rename_actor(
    session: AsyncSession, actor: Actor, action: RenameActorAction
) -> None:
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == actor.actor_id)
    )
    if not actor_for_account:
        logger.warning("ActorForAccount does not exist for actor %s", actor.actor_id)
        return

    actor_for_account.name = action.name
    await session.commit()


async def handle_actor_action(
    actor: Actor, session: AsyncSession, action: UpdateAction
) -> bool:
    """Handles individual actions from the UpdateActor
    method"""
    match action.action:
        case UpdateActionType.add_identifier:
            action = UpdateIdentifierAction.model_validate(action.model_dump())
            await handle_add_identifier(actor, session, action)
            return True
        case UpdateActionType.create_identifier:
            action = UpdateIdentifierAction.model_validate(action.model_dump())
            await handle_create_identifier(actor, session, action)
            return True
        case UpdateActionType.update_identifier:
            action = UpdateIdentifierAction.model_validate(action.model_dump())
            await handle_update_identifier(actor, session, action)
            return True
        case UpdateActionType.rename:
            rename_action = RenameActorAction.model_validate(action.model_dump())
            await handle_rename_actor(session, actor, rename_action)
            return False
        case UpdateActionType.update_property_value:
            logger.info("ADDING PROPERTY VALUE")
            cast_action = UpdatePropertyValueAction.model_validate(action.model_dump())
            handle_update_property_value(actor, cast_action)
            await session.commit()

            return True
        case UpdateActionType.remove_property_value:
            cast_action = UpdatePropertyValueAction.model_validate(action.model_dump())
            handle_delete_property_value(actor, cast_action)
            await session.commit()

            return True

    return False
