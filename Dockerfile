FROM python:3.11-slim

WORKDIR /app

# Install hermes-agent with API server support
RUN pip install -U pip && pip install hermes-agent aiohttp

# Create necessary directories
RUN mkdir -p /root/.hermes/memories /root/.hermes/skills

# Copy configuration
COPY config.yaml /root/.hermes/config.yaml

# Copy memory and user profile
COPY memory_export.md /root/.hermes/memories/MEMORY.md
COPY user_export.md /root/.hermes/memories/USER.md

# Copy skills
COPY skills_export /root/.hermes/skills/

# Create entrypoint script that reads model from env vars
RUN printf '#!/bin/bash\n\
echo "=== Hermes Agent Cloud ==="\n\
echo "Memory: $(wc -l < /root/.hermes/memories/MEMORY.md) lines loaded"\n\
echo "Skills: $(ls /root/.hermes/skills/ 2>/dev/null | wc -l) directories"\n\
if [ -n "$MODEL_DEFAULT" ]; then\n\
  echo "Overriding model: $MODEL_DEFAULT"\n\
  CONFIG=/root/.hermes/config.yaml\n\
  if grep -q "default:" "$CONFIG"; then\n\
    sed -i "s|^  default:.*|  default: $MODEL_DEFAULT|" "$CONFIG"\n\
  fi\n\
fi\n\
if [ -n "$PROVIDER" ]; then\n\
  echo "Overriding provider: $PROVIDER"\n\
  if grep -q "provider:" "$CONFIG"; then\n\
    sed -i "s|^  provider:.*|  provider: $PROVIDER|" "$CONFIG"\n\
  fi\n\
fi\n\
echo "Starting gateway..."\n\
exec hermes gateway run\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8642

ENTRYPOINT ["/entrypoint.sh"]
