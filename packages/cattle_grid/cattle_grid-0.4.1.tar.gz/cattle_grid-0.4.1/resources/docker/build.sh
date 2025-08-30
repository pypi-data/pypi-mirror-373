#!/usr/bin/env bash

set -eux

DOCKER_DIR=resources/docker

rm -rf dist
uv build --wheel

rm ${DOCKER_DIR}/*.whl

cp dist/*.whl ${DOCKER_DIR}/
cd ${DOCKER_DIR}

tag=$(uv run hatch version)
docker_tag=helgekr/cattle_grid:$tag
latest_tag=helgekr/cattle_grid:latest

docker buildx build --platform linux/arm64,linux/amd64  -t $docker_tag -t $latest_tag --build-arg tag=$tag  --push .