from .exchange import UpdateActorMessage, UpdateAction


def test_update_actor_message():
    msg = {
        "actor": "http://local.test/actor",
        "actions": [
            {
                "action": "add_identifier",
                "identifier": "acct:test@example.com",
                "primary": True,
            }
        ],
    }
    data = UpdateActorMessage.model_validate(msg)

    assert isinstance(data.actions[0], UpdateAction)
