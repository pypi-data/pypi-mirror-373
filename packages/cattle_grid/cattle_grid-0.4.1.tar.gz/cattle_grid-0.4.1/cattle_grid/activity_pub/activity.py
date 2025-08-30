from typing import Dict, Any

from bovine.activitystreams.utils import id_for_object


def actor_deletes_themselves(activity: Dict[str, Any]) -> bool:
    """
    Checks if activity is self delete of actor

    ```pycon
    >>> actor_deletes_themselves({"type": "Delete",
    ...     "actor": "http://actor.test/",
    ...     "object": "http://actor.test/"})
    True

    >>> actor_deletes_themselves({"type": "Delete",
    ...     "actor": "http://actor.test/",
    ...     "object": "http://other.test/"})
    False

    ```
    """

    activity_type = activity.get("type")
    if activity_type != "Delete":
        return False

    actor_id = activity.get("actor")
    object_id = id_for_object(activity.get("object"))

    if actor_id is None or object_id is None:
        return False

    return actor_id == object_id
