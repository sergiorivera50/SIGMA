#!/bin/bash


# Set the services directory for the project
BASE_DIR=$(cd "$(dirname "$0")" && cd .. && pwd)
SERVICES_DIR="$BASE_DIR/services"

# Build and tag all Docker images
docker build -t sigma-auth:latest $SERVICES_DIR/auth
docker build -t sigma-registry:latest $SERVICES_DIR/registry
docker build -t sigma-inference:latest $SERVICES_DIR/inference
docker build -t sigma-controller:latest $SERVICES_DIR/controller
docker build -t sigma-gateway:latest $SERVICES_DIR/gateway
