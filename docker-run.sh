#!/bin/bash
# Run with: ./docker-run.sh
# Handles Docker permission issues automatically

cd "$(dirname "$0")"

# Check if docker works directly
if docker info &>/dev/null; then
    docker compose up --build
else
    echo "⚠ Docker needs group permissions, using sg docker..."
    sg docker -c "docker compose up --build"
fi
