# report builder

to run

```bash
docker compose up
```

in this directory

Then

```bash
docker run --rm -ti -v .:/data --workdir /data\
    --env UV_PROJECT_ENVIRONMENT=/tmp/venv\
    --env CATTLE_GRID_MQ=cattle_grid_mq\
    --network test\
    ghcr.io/astral-sh/uv:python3.11-alpine /bin/sh
```

in your checked out cattle grid version
