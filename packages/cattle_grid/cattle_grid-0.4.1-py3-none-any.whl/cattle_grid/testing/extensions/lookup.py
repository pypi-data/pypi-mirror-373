from typing import Annotated
from fast_depends import Depends

from cattle_grid.model.lookup import Lookup


async def one(a: Lookup) -> Lookup:
    return Lookup(uri=a.uri, result={"id": a.uri, "method": "one"}, actor=a.actor)


async def skipped(a: Lookup) -> Lookup:
    return a


async def changed(a: Lookup) -> Lookup:
    return Lookup(uri="http://changed.test", actor=a.actor)


async def dependency() -> str:
    return "dependency"


async def with_dependency(a: Lookup, b: Annotated[str, Depends(dependency)]) -> Lookup:
    return Lookup(uri=a.uri, result={"from": b}, actor=a.actor)
