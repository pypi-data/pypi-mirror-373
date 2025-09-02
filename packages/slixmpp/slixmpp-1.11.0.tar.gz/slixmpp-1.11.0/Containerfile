# A container for Woodpecker CI
# This it NOT meant to be used in any other context
FROM debian:trixie-slim AS woodpecker

ENV UV_LINK_MODE=copy
ENV PATH=.venv/bin:$PATH

RUN apt update && apt install cargo gpg -y

COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

# install different python versions and populate the pypi cache,
# this way woodpecker does not have to make network calls unless
# we change the dependencies

COPY pyproject.toml uv.lock .

RUN for VER in 3.9 3.10 3.11 3.12 3.13; do \
        uv python install $VER ; \
        uv python pin $VER ; \
        uv sync --frozen --all-groups --no-install-project ; \
	done

# This container is used to build slixmpp wheels for MUSL-based distributions.
# For other linux distros, we use the maturin-provided base images instead.
FROM quay.io/pypa/musllinux_1_2_x86_64 as musl-wheels-amd64

RUN apk add maturin
RUN apk add cargo
RUN mkdir /io
WORKDIR /io

FROM quay.io/pypa/musllinux_1_2_aarch64 as musl-wheels-arm64

RUN apk add maturin
RUN apk add cargo
RUN mkdir /io
WORKDIR /io
