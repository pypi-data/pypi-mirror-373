# Installation

## Dependencies

cattle_grid has a few external dependencies:

- RabbitMQ. For MQTTv5 support, you need at least 3.13 (or 4.0).
- PostgreSQL. I use version 14 and 17. Not sure what requirements are.
- A reverse proxy, e.g. nginx
- python3.11 or higher

## Installing

Furthermore, to run cattle_grid, you need python and well pip.

### Configuring nginx

cattle_grid requires a reverse proxy to handle settings and manage
authentication requests. We note that cattle_grid is separated
into a part that handles authentication request and one that
handles ActivityPub.

??? info "Sample configuration"

    ```nginx
    --8<-- "./resources/report_builder/nginx.conf"
    ```

#### Authentication

We need an endpoint to expose the public key fetch actor, e.g.

```nginx
location /cattle_grid_actor {
    proxy_pass http://cattle_grid/auth/cattle_grid_actor;
}
```

and then configure the internal authentication endpoint

```nginx
location = /auth {
    internal;
    proxy_pass http://cattle_grid/auth/auth;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Original-Method $request_method;
    proxy_set_header X-Original-Host $host;
}
```

#### ActivityPub

We expose the following endpoints for ActivityPub

```nginx
location ~ /(actor|inbox|outbox|.well-known|followers|following|object) {
    auth_request /auth;
    auth_request_set $requester $upstream_http_x_cattle_grid_requester;

    proxy_set_header X-AP-Location "$scheme://$host$request_uri";
    proxy_set_header X-Cattle-Grid-Requester $requester;

    rewrite /(.*) /ap/$1 break;
    proxy_pass http://cattle_grid;
}
```

extensions such as simple storage can then be exposed by

```nginx
location /simple_storage/ {
    auth_request /auth;
    auth_request_set $requester $upstream_http_x_cattle_grid_requester;

    proxy_pass http://cattle_grid/simple_storage;
    proxy_set_header X-AP-Location "$scheme://$host$request_uri";
    proxy_set_header X-Cattle-Grid-Requester $requester;
}
```

### Configuring Rabbitmq

You should create a user for cattle_grid and give it sufficient
permissions

```bash
rabbitmqctl add_user cattle_grid $PASSWORD
rabbitmqctl set_permissions cattle_grid ".*" ".*" ".*"
```

This will be sufficient for cattle_grid to function. The connection is configured via the configuration file, e.g.

```toml title="cattle_grid.toml"
amqp_uri = "amqp://cattle_grid:$PASSWORD@rabbitmq:5672/"
```

#### cattle_grid as a RabbitMQ auth backend

See [RabbitMQ Reference](./reference_account/account.rabbitmq.md) for how to configure RabbitMQ to allow access with cattle_grid accounts.

#### Web MQTT and RabbitMQ

Install the [RabbitMQ Web MQTT extension](https://www.rabbitmq.com/docs/web-mqtt). This will expose a websocket endpoint on port `15675`. To configure nginx to forward this websocket through HTTPS use

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    ...

    location /ws/ {
        proxy_pass http://rabbitmq:15675;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_read_timeout 86400; 
        # neccessary to avoid websocket timeout disconnect
        proxy_send_timeout 86400; 
        # neccessary to avoid websocket timeout disconnect
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

### Configuring postgres

cattle_grid needs a username with password,
this cna then be configured via

```toml title="cattle_grid.toml"
db_uri = "postgres://postgres:pass@cattle_grid_db"
```

Tables are automatically created and updated on cattle_grid start.

### App + Processor vs Just App

Cattle_grid is split into two processes

- The app based on FastAPI that serves HTTP requests. It can be run via `uvicorn --factory cattle_grid.app:create_app`.
- The processor based on Faststream, which can be run via `faststream cattle_grid.processor:app`.

If you wish to run a single process, you can set

```toml title="cattle_grid.toml"
processor_in_app = true
```

which will run the processing inside the app.

## Configuring cattle_grid

cattle_grid has the concept of __Accounts__, which are used for basic access control of the user with respect to cattle_grid. By running

```bash
python -m cattle_grid account new NAME PASSWORD
```

one can create a new account. See [accounts](./accounts.md) for more details about accounts and how to configure them.

### Logging

One can configure logging in the `[logging]` section
of one of the config files, e.g.

```toml title="config/logging.toml"
[logging]

"cattle_grid.auth.router" = "debug"
"cattle_grid.activity_pub.server" = "debug"```
```

The syntax is

```toml
"logger name" = "level"
```

where the logger name is the python package name.
