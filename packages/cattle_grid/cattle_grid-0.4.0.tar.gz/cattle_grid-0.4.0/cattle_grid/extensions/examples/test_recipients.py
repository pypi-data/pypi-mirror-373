from .recipients import transformer


async def test_transformer():
    data = {"raw": {"type": "Activity", "to": ["as:Public"]}}

    result = await transformer(data)

    assert list(result.keys()) == ["recipients"]

    recipients = result["recipients"]

    assert recipients["recipients"] == ["as:Public"]
    assert recipients["public"] is True
