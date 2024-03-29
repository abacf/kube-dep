#!/bin/ash
# shellcheck shell=dash

if [ -z "$REDIS_HOST" ]; then
  REDIS_HOST="127.0.0.1"
fi

if [ -z "$REDIS_PORT" ]; then
  REDIS_PORT=6379
fi

if [ -z "$QUEUE_NAME" ]; then
  QUEUE_NAME="DEFAUT"
fi

if [ -z "$ENV" ]; then
  ENV="dev"
fi

cd /app || exit 1
poetry run ./app.py --redis-host "$REDIS_HOST" --redis-port "$REDIS_PORT" --queue-name "$QUEUE_NAME" --env "$ENV"