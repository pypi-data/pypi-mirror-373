def skip_method_information(routing_key):
    """Method information is not created for subscribtions to incoming.* or outgoing.*

    as only cattle_grid should publish to these
    routing keys

    ```pycon
    >>> skip_method_information("incoming.test")
    True

    >>> skip_method_information("outgoing.test")
    True

    >>> skip_method_information("test")
    False

    ```
    """

    if routing_key.startswith("incoming.") or routing_key.startswith("outgoing."):
        return True

    return False
