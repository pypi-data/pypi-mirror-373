FROM python:3.13-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /apps
COPY . /apps

RUN --mount=type=cache,target=/var/lib/apt/,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=tmpfs,target=/var/log/apt/ \
    apt update \
    && apt install -y git \
    && python -m pip install --upgrade pip build \
    && python -m build .

# ------------------------------------------------------------------------------

FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN --mount=type=bind,target=/context,from=builder,source=/apps \
    --mount=type=cache,target=/var/lib/apt/,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=tmpfs,target=/var/log/apt/ \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && echo "LANG=en_US.UTF-8" >> /etc/locale.conf \
    && apt-get update \
    && apt-get -y upgrade \
    && apt-get -y --no-install-recommends install \
        gcc \
        libpq-dev \
        locales \
        procps \
    && locale-gen en_US.UTF.8 \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --compile --no-cache-dir /context/dist/*.whl

ENTRYPOINT ["kraken-infinity-grid", "run"]

LABEL title="Kraken Infinity Grid"
LABEL maintainer="Benjamin Thomas Schwertfeger contact@b-schwertfeger.de"
LABEL description="The Infinity Grid Trading Algorithm for the Kraken Cryptocurrency Exchange."
LABEL documentation="https://kraken-infinity-grid.readthedocs.io/en/stable"
LABEL image.url="https://github.com/btschwerfeger/kraken-infinity-grid"
