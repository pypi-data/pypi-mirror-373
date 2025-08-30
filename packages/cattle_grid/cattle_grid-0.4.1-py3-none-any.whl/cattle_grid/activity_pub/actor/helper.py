from urllib.parse import urljoin


def shared_inbox_from_actor_id(actor_id: str) -> str:
    """Returns the shared inbox of the actor identified by actor_id

    ```pycon
    >>> shared_inbox_from_actor_id("http://host.test/actor/someId")
    'http://host.test/shared_inbox'

    ```
    """

    return urljoin(actor_id, "/shared_inbox")


def endpoints_object_from_actor_id(actor_id: str) -> dict:
    """Returns the endpoints object of the actor identified by actor_id

    ```pycon
    >>> endpoints_object_from_actor_id("http://host.test/actor/someId")
    {'sharedInbox': 'http://host.test/shared_inbox'}

    ```
    """
    return {"sharedInbox": shared_inbox_from_actor_id(actor_id)}
