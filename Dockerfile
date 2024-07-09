FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Création du répertoire pour les ROMs
RUN mkdir -p /app/roms

# Variables d'environnement par défaut
ENV ROM_FILE=default.gbc
ENV ROM_PATH=/app/roms
ENV WEBSOCKET_HOST=0.0.0.0
ENV WEBSOCKET_PORT=8081
ENV EMULATION_FPS=60
ENV SCREEN_UPDATE_RATE=15
ENV COMPRESSION_ENABLED=True

# Exposer le port du serveur WebSocket
EXPOSE ${WEBSOCKET_PORT}

CMD ["python", "main.py"]