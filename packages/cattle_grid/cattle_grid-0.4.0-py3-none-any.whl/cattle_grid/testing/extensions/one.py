input_fields = {"raw"}
output_fields = {"one"}


async def transformer(data: dict) -> dict:
    return {"one": 1}
