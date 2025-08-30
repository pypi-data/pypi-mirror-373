# BDD Tests and reporting Reporting

!!! warning
    This code is meant for testing and not to be enabled
    in a production setting.

## Running BDD tests

cattle_grid uses a set of Gherkin tests provided by
[fediverse-features](https://codeberg.org/helge/fediverse-features). They are currently configured
using

```toml title="fediverse-features.toml"
--8<-- "./fediverse-features.toml"
```

First download the features via

```bash
uv sync --frozen
uv run fediverse-features
```

Second start the docker containers and the runner

```bash
docker compose up --wait
docker compose run --rm cattle_grid_app /bin/sh
```

Starting the containers will take some time. The BDD tests can
then be run via

```bash
behave
```

## Configuration

Reporting can be enabled by setting

```toml title="cattle_grid.toml"
enable_reporting = true
```

Generated reports are stored in the `reports` directory.
A somewhat current set of reports is available
at [cattle_grid_reports](https://helge.codeberg.page/cattle_grid_reports/).

::: cattle_grid.testing.reporter
