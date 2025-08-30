input_fields = {"one"}
output_fields = {"two"}


async def transformer(data: dict) -> dict:
    return {"two": 2}
