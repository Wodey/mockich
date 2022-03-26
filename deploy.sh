#! /bin/bash

echo "pulling latest code"
git pull

echo "stopping server"
docker-compose down

echo "Building docker"
docker-compose up -d --build

echo "Logs..."
docker-compose logs -f -t


