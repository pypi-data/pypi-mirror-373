#!/usr/bin/env bash

uv run datamodel-codegen \
    --input-file-type jsonschema \
    --output-model-type  pydantic_v2.BaseModel \
    --use-schema-description \
    --use-field-description \
    --use-title-as-name \
    --collapse-root-model \
    --reuse-model \
    --use-subclass-enum \
    --input resources/schema/gateway.schema.json \
    --output cattle_grid/gateway/data_types.py


uv run datamodel-codegen \
    --input-file-type jsonschema \
    --output-model-type  pydantic_v2.BaseModel \
    --use-schema-description \
    --use-field-description \
    --input resources/activity_message.schema.json \
    --output cattle_grid/model/__init__.py

uv run datamodel-codegen \
    --input-file-type jsonschema \
    --output-model-type  pydantic_v2.BaseModel \
    --use-schema-description \
    --use-field-description \
    --input resources/managing.schema.json \
    --output cattle_grid/manage/models.py

uv run datamodel-codegen \
    --input-file-type jsonschema \
    --output-model-type  pydantic_v2.BaseModel \
    --use-schema-description \
    --use-field-description \
    --use-title-as-name \
    --collapse-root-model \
    --reuse-model \
    --use-subclass-enum \
    --use-union-operato \
    --input resources/schema/activity_pub.schema.json \
    --output cattle_grid/gateway/activity_pub_types

