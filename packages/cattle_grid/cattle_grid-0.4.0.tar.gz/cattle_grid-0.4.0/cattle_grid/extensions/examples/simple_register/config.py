from pydantic import BaseModel, Field


class RegistrationType(BaseModel):
    """Configuration for one registration path"""

    name: str = Field(
        examples=["dev"],
        description="name of the registration. Will be part of the path, i.e. `/register/{name}`",
    )

    permissions: list[str] = Field(
        examples=["admin"],
        description="List of permissions given to the registering account.",
    )

    extra_parameters: list[str] = Field(
        default=[],
        description="Extra parameters that should be in the request, will be stored in the actors meta information",
        examples=["fediverse"],
    )


class RegisterConfiguration(BaseModel):
    """Configuration for the register endpoint"""

    registration_types: list[RegistrationType] = Field(
        examples=[
            RegistrationType(name="dev", permissions=["dev"]),
        ],
        description="List of registration types",
    )
