#!/bin/bash

# Step 1: Find the container ID of the running or stopped 'ringg-chatbot' container
container_id=$(sudo docker ps -a --filter "ancestor=ringg-chatbot" --format "{{.ID}}")

# Step 2: Check if a container exists
if [ -n "$container_id" ]; then
    # Step 3: Check if the container is already running
    container_status=$(sudo docker inspect --format="{{.State.Status}}" "$container_id")
    if [ "$container_status" == "running" ]; then
        echo "Restarting the existing container (ID: $container_id)..."
        sudo docker restart -t 60 "$container_id"
    else
        echo "Starting the existing container (ID: $container_id)..."
        sudo docker start "$container_id"
    fi
    echo "Container restarted/started successfully."
else
    echo "No existing container found for ringg-chatbot. Please run the deployment script first."
fi