from cattle_grid.model.extension import (
    MethodInformationModel,
    AddMethodInformationMessage,
)

from .info import add_method_information


async def test_add_method_information():
    message = AddMethodInformationMessage(
        method_information=[
            MethodInformationModel(
                module="testing",
                routing_key="test_key",
            ),
        ]
    )

    await add_method_information(message)
