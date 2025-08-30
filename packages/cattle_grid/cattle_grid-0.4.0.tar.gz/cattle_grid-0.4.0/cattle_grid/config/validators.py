from dynaconf import Validator

base_validators = [
    Validator("amqp_uri", default="amqp://localhost"),
    Validator("db_uri", default="sqlite:///cattle_grid.db"),
    Validator("enable_reporting", cast=bool, default=False),
    Validator("processor_in_app", cast=bool, default=False),
    Validator("permissions", default={}),
]
"""Validates the basic configuration"""

auth_validators = [
    Validator("auth.require_signature_for_activity_pub", default=True),
]
"""Validates the authentication configuration"""

activity_pub_validators = [
    Validator("activity_pub.internal_exchange", default="cattle_grid_internal"),
    Validator("activity_pub.exchange", default="cattle_grid"),
    Validator("activity_pub.account_exchange", default="amq.topic"),
]
"""Validators for ActivityPub"""

gateway_admin_validations = [
    Validator("gateway.admin.enable", cast=bool, default=False),
    Validator("gateway.admin.enable_reset", cast=bool, default=False),
]
"""Validators for the gateway"""

account_validations = [
    Validator(
        "account.forbidden_names",
        default=lambda a, b: list(["bovine", "cattle_grid", "admin", "guest"]),
        cast=list,
    ),
    Validator("account.allowed_name_regex", cast=str, default="^[a-zA-Z0-9_]{1,16}$"),
]
"""Validators for the account"""

plugins_validations = [
    Validator("plugins", default=lambda a, b: list([]), cast=list),
]
"""Validators for the plugins"""


frontend_validations = [
    Validator(
        "frontend.base_urls",
        default=lambda a, b: list([]),
        cast=lambda x: [str(y) for y in x],
        condition=lambda items: all(
            x.startswith("http://") or x.startswith("https://") for x in items
        ),
    )
]
"""Validators for the frontend"""


extensions_validations = [
    Validator("extensions", default=lambda a, b: list([]), cast=list),
]
"""Validators for the plugins"""

testing_validators = [
    Validator("testing.enable", cast=bool, default=False),
    Validator("testing.accounts", default=lambda a, b: list([]), cast=list),
]
"""Validators for testing"""

all_validators = (
    base_validators
    + activity_pub_validators
    + auth_validators
    + gateway_admin_validations
    + plugins_validations
    + frontend_validations
    + extensions_validations
    + account_validations
    + testing_validators
)
