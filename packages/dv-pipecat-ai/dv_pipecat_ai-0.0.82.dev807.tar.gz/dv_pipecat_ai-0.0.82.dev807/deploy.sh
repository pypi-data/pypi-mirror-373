#!/bin/bash

# Step 1: Get the container ID of the running 'ringg-chatbot' container
container_id=$(sudo docker ps -a --filter "ancestor=ringg-chatbot" --format "{{.ID}}")

# Step 2: Pull the latest code from the repository
echo "Pulling the latest code..."
git pull

# Step 3: Build the Docker image
echo "Building the Docker image..."
sudo docker build  -t ringg-chatbot -f examples/ringg-chatbot/Dockerfile .

# Step 4: Stop the running container if it exists
# if [ -n "$container_id" ]; then
#     echo "Stopping the current container (ID: $container_id)..."
#     sudo docker stop "$container_id"
# else
#     echo "No existing container found for ringg-chatbot."
# fi
sudo docker stop -t 240 $(sudo docker ps -q)
if [ -n "$container_id" ]; then
    echo "deleting the current container (ID: $container_id)..."
    echo "Saving logs to /tmp/ringg-chatbot-logs.txt"
    sudo docker logs "$container_id" > /tmp/ringg-chatbot-logs.txt 2>&1
    sudo docker rm "$container_id"
else
    echo "No existing container found for ringg-chatbot."
fi

# Step 5: Run the Docker container with the specified settings
# Obtain the host machine's primary IP address and pass it to the container
HOST_IP=$(hostname -I | awk '{print $1}')
echo "Detected host IP: $HOST_IP"
echo "Starting a new container..."
sudo docker run -e HOST_IP=$HOST_IP -p 8765:8765 -d ringg-chatbot

echo "Deployment completed successfully."
