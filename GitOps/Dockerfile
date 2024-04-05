FROM alpine:3.19

COPY * /app/

RUN apk update && apk upgrade && apk add --no-cache python3 poetry py3-pip git

WORKDIR /app

RUN poetry install --no-root --no-cache --no-interaction