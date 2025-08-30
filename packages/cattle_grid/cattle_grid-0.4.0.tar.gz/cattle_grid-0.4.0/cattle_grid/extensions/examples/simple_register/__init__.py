"""

Sample configuration

```toml
[[extensions]]
module = "cattle_grid.extensions.examples.simple_register"
api_prefix = "/simple_register"

[[extensions.config.registration_types]]
name = "dev"
permissions = ["dev"]
extra_parameters = ["fediverse"]
```

"""

from fastapi import HTTPException

from cattle_grid.account.account import create_account, AccountAlreadyExists
from cattle_grid.dependencies.fastapi import SqlSession
from cattle_grid.extensions import Extension


from .config import RegisterConfiguration

extension = Extension("simple_register", __name__, config_class=RegisterConfiguration)
"""Definition of the extension"""


def determine_registration_type(config: RegisterConfiguration, name):
    for registration_type in config.registration_types:
        if registration_type.name == name:
            return registration_type
    return None


@extension.post("/register/{name}", status_code=201)
async def post_register(
    name,
    body: dict[str, str],
    config: extension.ConfigFastAPI,  # type: ignore
    session: SqlSession,
):
    registration_type = determine_registration_type(config, name)

    if registration_type is None:
        raise HTTPException(404)

    expected_keys = ["name", "password"] + registration_type.extra_parameters

    if any(x not in body for x in expected_keys):
        raise HTTPException(422)
    if any(not isinstance(body[x], str) for x in expected_keys):
        raise HTTPException(422)

    try:
        await create_account(
            session=session,
            name=body["name"],
            password=body["password"],
            permissions=registration_type.permissions,
            meta_information={
                key: body[key] for key in registration_type.extra_parameters
            },
        )
    except AccountAlreadyExists:
        raise HTTPException(409)
