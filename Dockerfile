FROM python:3.12-slim

# RUN apt install gcc libpq (no longer needed bc we use psycopg2-binary)

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src
ENV PYTHONPATH=/src FLASK_APP=allocation.entrypoints.flask_app FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80