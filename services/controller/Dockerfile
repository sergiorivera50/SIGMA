FROM python:3.11

COPY ./manifests /src/manifests
COPY handlers.py /src/handlers.py
COPY requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /src/requirements.txt

CMD kopf run /src/handlers.py --verbose
