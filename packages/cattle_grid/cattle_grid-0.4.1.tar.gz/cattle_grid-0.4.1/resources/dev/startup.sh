#!/bin/sh

uv export --no-editable --no-emit-project > /tmp/requirements.txt
pip install -r /tmp/requirements.txt
pip install ./muck_out*

exec "$@"