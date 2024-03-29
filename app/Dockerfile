FROM alpine:3.19

WORKDIR /app

RUN apk update && apk upgrade && apk add --no-cache python3 poetry py3-pip git

COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN git clone https://github.com/abacf/iut-stmalo-sae503 . && chmod +x /app/app.py && chmod +x /docker-entrypoint.sh &&  poetry install --no-root --no-cache --no-interaction && poetry cache clear pypi --all

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]