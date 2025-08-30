ARG python_tag=3.11
FROM helgekr/bovine:python${python_tag}
ARG tag=0.2.1
RUN apk add curl
RUN pip install cattle_grid==${tag}
