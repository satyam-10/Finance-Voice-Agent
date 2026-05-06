# Single-image deployment: frontend + token server + agent worker
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project — this includes:
#   - agent.py, config.py, prompts.py, smoke_test.py
#   - agents/, tools/, providers/, data/  (your existing structure)
#   - server.py            (the token server)
#   - static/index.html    (the frontend)
COPY . .

# Pre-download LiveKit's VAD model so first request is fast
RUN python main.py download-files

# Supervisor manages both processes in one container
COPY supervisord.conf /etc/supervisor/conf.d/markets.conf

# Azure App Service expects port 8080
EXPOSE 8080

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/markets.conf"]
