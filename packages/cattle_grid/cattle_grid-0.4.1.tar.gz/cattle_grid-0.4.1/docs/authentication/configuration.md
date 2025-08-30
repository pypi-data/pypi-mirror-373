# Configuration

Let's assume that cattle grid is running on its own domain
`cattlegrid.yourdomain.example`. Then you can give the
cattle grid actor the id `https://cattlegrid.yourdomain.example/actor`.

!!! info
    For how to use cattle_grid together with an application, see
    [the corresponding bovine_herd tutorial](https://bovine-herd.readthedocs.io/en/latest/tutorials/cattle_grid/).

## Setting up cattle grid

First cattle_grid can be installed from [PyPI](https://pypi.org/project/cattle-grid/) via

```bash
pip install cattle-grid
```

Then one can create the configuration file (including generating public and private keys)
using

```bash
python -mcattle_grid.auth.config
```

where you have to enter an actor id, We assume for this that you use
`https://cattlegrid.yourdomain.example/actor`.  The details for this
command are

<!-- ::: mkdocs-click
    :module: cattle_grid.auth.config
    :command: create_config
    :prog_name: python -m cattle_grid.auth.config
    :depth: 3 -->

The configuration is stored in the `cattle_grid.toml`. The details of
the config object are available [here][cattle_grid.config.auth.AuthConfig].

We furthermore, recommend that
you set up a [blocklist](blocking.md) using for example Seirdy's FediNuke by
running

```bash
python -mcattle_grid.auth.block
```

You can now run cattle_grid via

```bash
uvicorn --factory cattle_grid:create_app --uds /tmp/cattle_grid.sock
```

## systemd unit

To run cattle_grid as a systemd service, the unit file would look like

```systemd title="/etc/systemd/system/cattle_grid.service"
[Unit]
Description=cattle grid
After=network.target

[Service]
User=cattle_grid
Group=cattle_grid
Restart=always
Type=simple
WorkingDirectory=/opt/cattle_grid
ExecStart=uvicorn --factory cattle_grid:create_app --uds /tmp/cattle_grid.sock

[Install]
WantedBy=multi-user.target
```

## Reverse Proxies

The request flow in using a reverse proxy is explained
in [request flow](./request_flow.md).

### nginx

The development environment uses nginx as its reverse proxy. It is configured via

??? info "Development configuration"

    ```nginx title="/etc/nginx/conf.d/default.conf"
    --8<-- "./resources/dev/nginx.conf"
    ```

A summary of the steps now follows.

#### Serve the cattle_grid actor

```nginx
server {
    listen 80;
    server_name cattle_grid;

    location / {
        proxy_pass http://cattle_grid_app/auth/;
    }

    location = /auth {
        internal;
    }
}
```

This is used to serve the actor used to make requests for
public keys and its webfinger. `proxy_pass` should point to your application. `location = /auth` ensures
that auth requests cannot be verified from the outside.

#### Serving your application

```nginx
server {
    listen 80;
    server_name abel banach;

    location / {
        auth_request /auth;
        auth_request_set $requester $upstream_http_x_cattle_grid_requester;

        proxy_pass http://cattle_grid_app/ap/;
        proxy_set_header X-AP-Location "$scheme://$host$request_uri";
        proxy_set_header X-Cattle-Grid-Requester $requester;
    }

    ...
}
```

This is the first part of configuring your application. This
part serves the content. The `auth_request` directive
makes the authentication request to `cattle_grid.auth`.
`auth_request_set` makes the header available
in the following request. `proxy_pass` should point
to your application. `proxy_set_header` sets two
relevant headers.

#### Secure the auth endpoint

```nginx
location = /auth {
    internal;
    proxy_pass http://cattle_grid_app/auth/auth;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Original-Method $request_method;
    proxy_set_header X-Original-Host $host;
}
```

This is the second part. It tells to forward the
auth request to `cattle_grid.auth` and provides the
necessary information.

### caddy

A disabled option in `docker-compose.yml` can be used to run
banach through caddy. This is done with the following configuartion file.

??? info "Development configuration"

    ```caddy title="/etc/caddy/Caddyfile"
    --8<-- "./resources/dev/Caddyfile"
    ```

#### Serving your app

```nginx
:80 {
    ...

    vars ap_location "{scheme}://{host}{uri}"
    handle_path /* {
        rewrite * /ap{path}
        reverse_proxy cattle_grid_app:80 {
            header_up X-AP-Location "{vars.ap_location}"
        }
    }
}
```

The above snippet can be used to serve your application. Here `vars` is used to defined
the true location before rewriting ti and
sending to the proxied application.

#### Configuring authentication

The following block replaces the `...` in the above one.

```nginx
forward_auth cattle_grid_app:80 {
    uri /auth/auth

    header_up X-Original-URI {uri}
    header_up X-Original-Method {method}
    header_up X-Original-Host {host}

    copy_headers X-Cattle-Grid-Requester
}
```

The functionality is the same as for nginx.
