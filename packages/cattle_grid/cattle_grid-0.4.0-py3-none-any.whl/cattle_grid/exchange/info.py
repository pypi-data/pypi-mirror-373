from cattle_grid.dependencies.globals import global_container

from cattle_grid.model.extension import (
    MethodInformationModel,
    AddMethodInformationMessage,
)


exchange_method_information = [
    MethodInformationModel(
        module="cattle_grid.exchange",
        routing_key="send_message",
        description="Takes an activity and sends it to its recipients",
    ),
    MethodInformationModel(
        module="cattle_grid.exchange",
        routing_key="update_actor",
        description="Updates an actor",
    ),
    MethodInformationModel(
        module="cattle_grid.exchange",
        routing_key="delete_actor",
        description="Deletes an actor",
    ),
]
"""Information about the methods defined on the ActivityExchange
by default"""


async def add_method_information(message: AddMethodInformationMessage):
    """Adds information about methods defined by an extension"""
    current_information = global_container.method_information or []

    global_container.method_information = (
        current_information + message.method_information
    )
