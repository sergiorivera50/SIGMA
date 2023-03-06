#!/bin/bash

# Configuration variables
DOCKERHUB_ACCOUNT=sergiorivera50

# Set the services directory for the project
BASE_DIR=$(cd "$(dirname "$0")" && cd .. && pwd)
SERVICES_DIR="$BASE_DIR/services"

# Build and tag all Docker images
docker build -t $DOCKERHUB_ACCOUNT/sigma-auth:latest $SERVICES_DIR/auth
docker build -t $DOCKERHUB_ACCOUNT/sigma-registry:latest $SERVICES_DIR/registry
docker build -t $DOCKERHUB_ACCOUNT/sigma-inference:latest $SERVICES_DIR/inference

# Push all Docker images
docker push $DOCKERHUB_ACCOUNT/sigma-auth:latest
docker push $DOCKERHUB_ACCOUNT/sigma-registry:latest
docker push $DOCKERHUB_ACCOUNT/sigma-inference:latest
