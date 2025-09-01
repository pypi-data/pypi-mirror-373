FROM alpine:latest AS base

RUN apk add --no-cache \
    ca-certificates \
    gettext \
    openssl \
    bash \
    curl \
    python3 \
    python3-dev \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

FROM base AS app

WORKDIR /app

COPY ./src/slugkit ./src/slugkit
COPY ./pyproject.toml README.md LICENSE uv.lock ./

RUN uv sync

FROM app AS final

# Host, port and path are set in the environment variables
# SLUGKIT_MCP_HOST, SLUGKIT_MCP_PORT, SLUGKIT_MCP_PATH
# Default values are 0.0.0.0, 5000, /mcp
CMD ["/bin/uv", "run", \
    "slugkit-mcp", "--transport", "http" ]
