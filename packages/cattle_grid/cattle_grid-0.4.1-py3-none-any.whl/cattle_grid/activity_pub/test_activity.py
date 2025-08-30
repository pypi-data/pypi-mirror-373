from .activity import actor_deletes_themselves


def test_actor_deletes_themselves():
    assert not actor_deletes_themselves({})


def test_actor_deletes_themselves_embedded_object():
    activity = {
        "type": "Delete",
        "actor": "http://actor.test/",
        "object": {
            "id": "http://actor.test/",
        },
    }

    assert actor_deletes_themselves(activity)
