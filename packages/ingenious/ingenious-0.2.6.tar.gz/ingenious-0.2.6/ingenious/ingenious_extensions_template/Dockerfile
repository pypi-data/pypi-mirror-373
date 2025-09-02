# syntax=docker/dockerfile:1
# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install system dependencies and Microsoft ODBC drivers
# Required for pyodbc to connect to Azure SQL Database
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    unixodbc \
    unixodbc-dev \
    ca-certificates \
    build-essential \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && mkdir -p /etc/odbc \
    && cp /opt/microsoft/msodbcsql18/etc/odbcinst.ini /etc/odbc/odbcinst.ini \
    && echo '/opt/microsoft/msodbcsql18/lib64' >> /etc/ld.so.conf.d/mssql.conf \
    && ldconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN uv sync --locked --no-dev

# Make startup script executable
RUN chmod +x /app/start.sh

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Create necessary directories for Ingenious Extensions
RUN mkdir -p /app/tmp /app/.tmp /app/ingenious_extensions

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set ODBC-related environment variables
ENV ODBCSYSINI=/etc/odbc
ENV ODBCINI=/etc/odbc/odbc.ini

# Uvicorn configuration for FastAPI
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8081
ENV UVICORN_WORKERS=4
ENV UVICORN_TIMEOUT_KEEP_ALIVE=5
ENV UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=60

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Expose the port the app runs on (default Ingenious REST API port)
EXPOSE 8081

# Run the Ingenious FastAPI application with uvicorn
CMD ["/app/start.sh"]
