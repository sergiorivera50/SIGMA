FROM python:3.10-slim-bullseye

# Update + Install System Dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential sqlite3 default-libmysqlclient-dev \
  && pip install --no-cache-dir --upgrade pip

# Install Python Dependencies
WORKDIR /auth
COPY ./requirements.txt /auth
RUN pip install --no-cache-dir -r /auth/requirements.txt

# Copy Application Source Code
COPY ./__init__.py /auth
COPY ./app /auth/app

# Create database path
# Later, manually initialise with -> flask init-data
RUN mkdir /auth/data

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
