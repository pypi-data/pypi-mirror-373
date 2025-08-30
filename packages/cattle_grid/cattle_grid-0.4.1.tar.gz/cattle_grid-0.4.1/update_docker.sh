#!/usr/bin/env bash

set -eux

REQUIREMENTS_FILE=resources/docker_dev/requirements.txt

uv export --no-editable --no-emit-project --no-hashes > $REQUIREMENTS_FILE

sed -i '/argon2-cffi-bindings==21.2.0/d' $REQUIREMENTS_FILE

docker compose build