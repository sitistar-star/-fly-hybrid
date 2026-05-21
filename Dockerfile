FROM python:3.11

WORKDIR /app

# Install hermes-agent
RUN pip install -U pip && pip install hermes-agent

# Create config directory
RUN mkdir -p /root/.hermes/logs

# Copy configuration
COPY config.yaml /root/.hermes/config.yaml

# Entrypoint
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'echo "=== Hermes Agent Cloud ==="' >> /entrypoint.sh && \
    echo 'exec hermes gateway run' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 8642

ENTRYPOINT ["/entrypoint.sh"]
