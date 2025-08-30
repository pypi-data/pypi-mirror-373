#!/usr/bin/env bash

rm -rf dist
mkdir dist


uv build --wheel ../.. --out-dir dist


