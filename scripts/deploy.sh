#!/bin/bash

SERVICES_DIR="services"

# Find all directories named "deploy/" within the "services/" directory
DEPLOY_DIRS=($(find "$SERVICES_DIR" -type d -name "deploy"))

# Display the list of services to be deployed
echo "The following services will be deployed:"
for DEPLOY_DIR in "${DEPLOY_DIRS[@]}"; do
    # Extract the directory name between "services/" and "/deploy"
    SERVICE_NAME=$(echo "$DEPLOY_DIR" | awk -F "$SERVICES_DIR/" '{print $2}' | awk -F "/deploy" '{print $1}')
    # Build the deployment file path
    DEPLOY_PATH="$SERVICES_DIR/$SERVICE_NAME/deploy"
    echo "  - $SERVICE_NAME ($DEPLOY_PATH)"
done

# Ask for confirmation before proceeding
echo -n "Do you want to proceed with the deployment? (y/n): "
read CHOICE
if [[ "$CHOICE" =~ ^[Yy]$ ]]; then
    echo
    # Deploy each service
    for DEPLOY_DIR in "${DEPLOY_DIRS[@]}"; do
        # Extract the directory name between "services/" and "/deploy"
        SERVICE_NAME=$(echo "$DEPLOY_DIR" | awk -F "$SERVICES_DIR/" '{print $2}' | awk -F "/deploy" '{print $1}')
        # Build the deployment file path
        DEPLOY_PATH="$SERVICES_DIR/$SERVICE_NAME/deploy"
        # Run "kubectl apply" command with the deployment file path
        kubectl apply -f "$DEPLOY_PATH"
    done
    echo
    echo "Deployment completed successfully."
else
    echo "Deployment cancelled."
fi
