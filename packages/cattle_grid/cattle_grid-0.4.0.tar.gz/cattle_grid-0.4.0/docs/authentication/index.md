# Authentication server

cattle_grid.auth is just the authorization component of cattle_grid.
As described in [request_flow](./request_flow.md) and [configuration](./configuration.md)
one can use it to take care of checking HTTP signatures, as an
authentication step before processing the request.

<div class="grid cards" markdown>

- :material-lock:{ .lg .middle } __Authentication__

    ----

    Instead of checking HTTP Signatures, including resolving
    public keys yourself. You can let cattle_grid.auth handle
    it.

- [:octicons-stop-16:{ .lg .middle } __Blocks__](#blocking)

    ----

    cattle_grid.auth allows you to manage a block list
    that is done on authentication level. This can be used
    as a first block list that contains the worst offenders.

- [:material-api:{ .lg .middle } __OpenAPI__](../assets/redoc.html?url=openapi_auth.json)

- [:material-book-cog:{ .log .middle } __Reference__](../reference/auth.md)

    ----

    Documentation on the functions

</div>

## Basic installation

First install cattle_grid from pypi via

```bash
pip install cattle_grid
```

To configure `cattle_grid.auth`, you need to supply
the actor id used to fetch public keys, e.g.

```bash
python -mcattle_grid.auth new-config\
    https://your_domain.example/cattle_grid_actor
```

!!! todo
    FIXME

where you have to replace `your_domain.example` with your domain
name.

### ActivityPub requests

Correctly signed ActivityPub requests contain the
`X-CATTLE-GRID-REQUESTER` header with the controller that signed
the requests, e.g.

```http
X-CATTLE-GRID-REQUESTER: https://controller.example/some/actor
```

Unsigned or incorrectly signed requests are rejected with 401
unauthorized.

!!! warning
    `cattle_grid.auth` only checks the headers. This means that
    the request body and thus digest needs to be checked by
    your application.

### HTML requests

Requests that should be forwarded to the html page
contain the `X-CATTLE-GRID-SHOULD-SERVE` header.

## Configuration

### Configuration file

!!! Question
    Should this become `config/auth.toml`

By inspecting `cattle_grid_auth.toml`, you can see that
a public and private key was generated for this actor, e.g.

```toml title="cattle_grid_auth.toml"
[auth]
enabled = true
actor_id = "http://cattle_grid/cattle_grid_actor"
actor_acct_id = "acct:4ILq9osJUscnVDwe@cattle_grid"
public_key = """
-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----
"""
private_key = """
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
"""
```

This finishes the configuration of cattle_grid.

### Configuring reject unsigned pure ActivityPub requests

We consider a request an ActivityPub request if it has the
accept header

```plain
accept: application/activity+json
```

or

```plain
accept: application/ld+json; profile="https://www.w3.org/ns/activitystreams"
```

or both. If a request has no other accept header pieces,
we consider it a __pure ActivityPub request__.

The default behavior of `cattle_grid.auth` is to reject unsigned
pure ActivityPub requests. You can disable this behavior by
setting

```toml title="cattle_grid_auth.toml"
[auth]
...
require_signature_for_activity_pub = false
```

Set the variable to `true` to keep the default behavior.

!!! info
    If unsigned requests are rejected for appropriate accept
    headers, it is reasonable behavior to serve the fallback
    option, whenever the `x-cattle-grid-requester` header is
    unset (or empty).

### Configuring the database

By adding

```toml title="cattle_grid_auth.toml"
db_uri = "sqlite://other.db"

[auth]
enabled = true
```

one can change the db file that cattle_grid.auth is using.
Similarly by setting

```toml title="cattle_grid_auth.toml"
db_uri = "postgres://postgres:pass@postgres"
```

one can set it to use a postgres database.

## Running cattle_grid

You can now run cattle grid via

```bash
uvicorn --factory cattle_grid.auth:create_app
```

Then one needs to run

```bash
python -mcattle_grid.config
```

For the exposed routes see [OpenAPI specification](../assets/redoc_auth.html).

!!! warning
    cattle_grid does not check that the digest is correct. This is the responsibility of
    your application. One can consider this a performance optimization, as it means that
    nginx only needs to transmit the headers to cattle_grid in order to get the authentication
    result.

## Blocking

The blocklist of cattle_grid.auth is another toml file.

```toml title="cattle_grid_block_list.toml"
auth.domain_blocks = [
    "bad.example",
    "worse.example"
]
```

By running

```bash
python -mcattle_grid.auth block
```

one can view the commands available for managing the blocklist.
