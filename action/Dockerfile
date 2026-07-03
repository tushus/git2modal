# Dockerfile
# Container image for the Git2Modal GitHub Action
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/git2modal/action"
LABEL org.opencontainers.image.description="Deploy Python code to Modal.com on git push"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install the Modal CLI
RUN pip install --no-cache-dir "modal>=0.60.0" pyyaml

# Copy action entrypoint
COPY entrypoint.sh /entrypoint.sh
COPY modal_deploy.py /modal_deploy.py
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]