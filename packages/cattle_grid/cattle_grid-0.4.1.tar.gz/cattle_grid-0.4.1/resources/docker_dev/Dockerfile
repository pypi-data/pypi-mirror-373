FROM helgekr/bovine:0.5.18-python3.11


RUN apk add curl git postgresql
RUN pip install uv

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install muck_out