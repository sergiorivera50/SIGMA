FROM python:3.10-slim-bullseye

# Update + Install System Dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests build-essential \
  && pip install --no-cache-dir --upgrade pip

# Set PYTHONPATH environment variable
ENV PYTHONPATH "${PYTHONPATH}:/"

# Install Python Dependencies
WORKDIR /registry
COPY ./requirements.txt /registry
RUN sed '/tensorflow-macos/d' requirements.txt > tmp.txt && mv tmp.txt requirements.txt
RUN pip install --no-cache-dir tensorflow
RUN pip install --no-cache-dir -r /registry/requirements.txt

# Copy Application Source Code
COPY ./__init__.py /registry
COPY ./app /registry/app

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
