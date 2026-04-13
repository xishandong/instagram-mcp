# instagram-mcp Dockerfile
# Runs the MCP SSE server via uvicorn/starlette on port 8000.

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for running Chromium (zendriver) in headless mode.
# NOTE: Package names vary slightly across Debian releases; these are the common ones.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    chromium \
    chromium-driver \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY instagram_mcp ./instagram_mcp

EXPOSE 8000

# Defaults to 127.0.0.1 inside container by your code; we override via config mount.
# If you don't mount a config, it will still listen on 127.0.0.1 inside container,
# which is not reachable from docker port mapping.
# So: mount /root/.instagram-mcp/config.json with server.host=0.0.0.0.
CMD ["python", "-m", "instagram_mcp.server"]

