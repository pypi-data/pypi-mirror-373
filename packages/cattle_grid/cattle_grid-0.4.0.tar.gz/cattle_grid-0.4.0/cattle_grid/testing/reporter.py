"""
Made as a tool to create reports from test runs
done using behave. Basically, a scenario is run, and a markdown file is created.

Currently recorded are the step, the scenario, messages
received on the `incoming.#` and `outgoing.#` routing keys
of the cattle_grid exchange.

Finally, fetch results from gateway are reported.
"""

import logging
import os
import asyncio
import json
from contextlib import asynccontextmanager

from faststream import Context
from faststream.rabbit import RabbitExchange, ExchangeType, RabbitRouter, RabbitQueue

from cattle_grid.dependencies.globals import global_container

logger = logging.getLogger(__name__)

exchange = RabbitExchange("reporting", type=ExchangeType.TOPIC)
lock = asyncio.Lock()
current_file: str | None = None
step_title: str | None = None


def create_reporting_router() -> RabbitRouter:
    router = RabbitRouter()

    @asynccontextmanager
    async def current_file_handler(mode="a"):
        if current_file is None:
            raise ValueError("No current file")
        async with lock:
            with open(current_file, mode) as fp:
                yield fp

    @router.subscriber(RabbitQueue("step_queue", routing_key="step"), exchange)
    async def reporting_step(msg):
        """Reports the current step"""
        if not current_file:
            return

        global step_title

        message_type = msg.get("type")

        step_title = "## " + message_type + ": " + msg.get("name") + "\n\n"

        if message_type in ["when", "then"]:
            async with current_file_handler() as fp:
                fp.writelines([step_title])
                step_title = None

    @router.subscriber(RabbitQueue("scenario_queue", routing_key="scenario"), exchange)
    async def reporting_scenario(msg):
        """Reports the scenario.

        Note every scenario is written to its own file in the `reports` directory."""
        scenario = msg.get("name")
        scenario_filename = "_".join(msg.get("file").split("/")[1:]).removesuffix(
            ".feature"
        )

        async with lock:
            global current_file
            scenario_alpha = "".join([x for x in scenario if x.isalpha()])

            directory = f"reports/{scenario_filename}"
            os.makedirs(directory, exist_ok=True)

            current_file = f"{directory}/{scenario_alpha}.md"

        async with current_file_handler(mode="w") as fp:
            logger.info(msg.get("description"))
            fp.writelines([f"#{scenario}\n\n"] + msg.get("description") + ["\n\n"])

    @router.subscriber(
        RabbitQueue("scenario_end_queue", routing_key="scenario_end"), exchange
    )
    async def reporting_scenario_end():
        """Reports the scenario.

        Note every scenario is written to its own file in the `reports` directory."""

        async with lock:
            global current_file

            current_file = None

    @router.subscriber(
        RabbitQueue("processing_reporting_in", routing_key="receive.#"),
        global_container.account_exchange,
    )
    @router.subscriber(
        RabbitQueue("processing_reporting_out", routing_key="send.#"),
        global_container.account_exchange,
    )
    async def reporting_incoming_outgoing(
        msg: dict,
        routing_key=Context("message.raw_message.routing_key"),
    ):
        """Records incoming and outgoing messages"""
        if not current_file:
            return
        if routing_key.endswith("info"):
            return

        global step_title

        async with current_file_handler() as fp:
            if step_title:
                fp.writelines([step_title])
                step_title = None

            fp.writelines(
                [
                    f"""

```json title="{routing_key}"
""",
                    json.dumps(msg, indent=2),
                    "\n```\n\n",
                ]
            )

        return {}

    return router
