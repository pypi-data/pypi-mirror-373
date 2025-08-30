import os
import asyncio
import aio_pika
import json


async def publish_reporting(routing_key, data):
    mq_host = os.environ.get("CATTLE_GRID_MQ", "rabbitmq")

    connection = await aio_pika.connect_robust(
        f"amqp://guest:guest@{mq_host}/",
    )

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "reporting", aio_pika.ExchangeType.TOPIC
        )

        await exchange.publish(
            aio_pika.Message(body=json.dumps(data).encode()),
            routing_key=routing_key,
        )


def before_step(context, step):
    data = {"name": step.name, "type": step.step_type}
    asyncio.get_event_loop().run_until_complete(publish_reporting("step", data))
