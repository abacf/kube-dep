FROM alpine:3.19 AS build

ARG KLUCTL_VERSION=2.24.1

RUN apk update && apk add --no-cache wget~=1.21.4

RUN wget --progress=dot:giga https://github.com/kluctl/kluctl/releases/download/v${KLUCTL_VERSION}/kluctl_v${KLUCTL_VERSION}_linux_amd64.tar.gz && tar -xvf kluctl_v${KLUCTL_VERSION}_linux_amd64.tar.gz

FROM bitnami/minideb:bookworm AS runtime

COPY * /app/
COPY --from=build /kluctl /usr/local/bin/kluctl

RUN install_packages python3 python3-poetry

WORKDIR /app

RUN poetry install --no-root --no-cache --no-interaction && chmod +x /app/gitops-sync.py

ENTRYPOINT [ "/app/gitops-sync.py" ]