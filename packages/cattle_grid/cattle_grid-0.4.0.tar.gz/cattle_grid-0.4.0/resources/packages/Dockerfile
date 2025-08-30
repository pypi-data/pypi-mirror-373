FROM helgekr/bovine

RUN apk add curl

COPY dist/*.whl .
RUN --mount=type=cache,target=/root/.cache/  pip install *.whl

COPY *.toml .