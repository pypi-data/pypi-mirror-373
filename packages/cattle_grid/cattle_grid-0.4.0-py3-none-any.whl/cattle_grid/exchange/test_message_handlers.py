from unittest.mock import AsyncMock, MagicMock


from .message_handlers import send_message


async def test_send_message():
    msg = MagicMock(actor="http://actor.test", data={})

    await send_message(msg, broker=AsyncMock())


async def test_send_message_context_serialization():
    activity = dict(
        id="http://local.test/id1",
        type="Create",
        actor="http://local.test",
        to=["http://remote.test"],
    )
    activity["@context"] = "https://www.w3.org/ns/activitystreams"
    msg = MagicMock(actor="http://actor.test", data=activity)

    broker = AsyncMock()

    await send_message(msg, broker=broker)

    broker.publish.assert_awaited()

    args = broker.publish.call_args[0][0]

    resulting_activity = args.data
    assert "@context" in resulting_activity
