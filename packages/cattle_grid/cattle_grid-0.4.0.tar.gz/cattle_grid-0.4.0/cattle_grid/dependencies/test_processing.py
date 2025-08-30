from unittest.mock import MagicMock
from faststream.rabbit import RabbitBroker, TestRabbitBroker

from cattle_grid.model.common import WithActor

from cattle_grid.testing.fixtures import *  # noqa

from .processing import MessageActor, ActorProfile, FactoriesForActor


async def test_message_actor(actor_for_test):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(actor: MessageActor):
        subscriber(actor.actor_id)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=actor_for_test.actor_id), "test")

    subscriber.assert_called_once_with(actor_for_test.actor_id)


async def test_actor_profile(actor_for_test):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(actor: ActorProfile):
        subscriber(actor)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=actor_for_test.actor_id), "test")

    subscriber.assert_called_once()

    (profile,) = subscriber.call_args[0]

    assert isinstance(profile, dict)
    assert profile["id"] == actor_for_test.actor_id


async def test_factories(actor_for_test):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(factories: FactoriesForActor):
        subscriber(factories)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=actor_for_test.actor_id), "test")

    subscriber.assert_called_once()

    (factories,) = subscriber.call_args[0]

    assert len(factories) == 2
