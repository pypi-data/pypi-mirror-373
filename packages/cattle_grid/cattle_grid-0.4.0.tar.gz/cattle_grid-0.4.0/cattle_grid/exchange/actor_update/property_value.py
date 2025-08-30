import logging
from sqlalchemy.orm.attributes import flag_modified

from bovine.activitystreams.utils.property_value import from_key_value

from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.model.exchange import UpdatePropertyValueAction

logger = logging.getLogger(__name__)


def find_key_in_attachments(attachments: list, key: str) -> int | None:
    for idx, attachment in enumerate(attachments):
        if not isinstance(attachment, dict):
            continue
        if attachment.get("type") != "PropertyValue":
            continue
        if attachment.get("name") == key:
            return idx

    return None


def handle_update_property_value(
    actor: Actor, action: UpdatePropertyValueAction
) -> None:
    current_attachments = actor.profile.get("attachment", [])

    current_index = find_key_in_attachments(current_attachments, action.key)

    if current_index is None:
        current_attachments.append(from_key_value(action.key, action.value))
    else:
        current_attachments[current_index] = from_key_value(action.key, action.value)

    actor.profile["attachment"] = current_attachments
    flag_modified(actor, "profile")


def handle_delete_property_value(actor: Actor, action: UpdatePropertyValueAction):
    current_attachments = actor.profile.get("attachment", [])

    current_index = find_key_in_attachments(current_attachments, action.key)

    if current_index is not None:
        del current_attachments[current_index]

    actor.profile["attachment"] = current_attachments
    flag_modified(actor, "profile")
