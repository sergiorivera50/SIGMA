FROM python:3.10-slim-bullseye

# Update + Install System Dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests build-essential \
  && pip install --no-cache-dir --upgrade pip

# Set PYTHONPATH environment variable
ENV PYTHONPATH "${PYTHONPATH}:/"

# Install Python Dependencies
WORKDIR /gateway
COPY ./requirements.txt /gateway
RUN pip install --no-cache-dir -r /gateway/requirements.txt

# Copy Application Source Code
COPY ./__init__.py /gateway
COPY ./app /gateway/app

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:create_app()"]
