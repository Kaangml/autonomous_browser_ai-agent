FROM Comingsoon
# FROM python:3.11-slim AS builder

# WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     wget \
#     gnupg \
#     ca-certificates \
#     fonts-liberation \
#     libasound2 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libatspi2.0-0 \
#     libcups2 \
#     libdbus-1-3 \
#     libdrm2 \
#     libgbm1 \
#     libgtk-3-0 \
#     libnspr4 \
#     libnss3 \
#     libwayland-client0 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxfixes3 \
#     libxkbcommon0 \
#     libxrandr2 \
#     xdg-utils \
#     && rm -rf /var/lib/apt/lists/*
# COPY pyproject.toml .

# RUN uv sync 
