#!/bin/sh

pip install redis fakeredis

uvicorn --factory cattle_grid:create_app --host 0.0.0.0 --port 80