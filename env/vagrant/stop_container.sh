#! /bin/sh

CONTAINER_ID="$1"

docker stop "$CONTAINER_ID"
docker wait "$CONTAINER_ID"
docker rm "$CONTAINER_ID"
