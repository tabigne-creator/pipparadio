FROM ubuntu:22.04

# Installa pacchetti
RUN apt-get update && apt-get install -y \
    icecast2 \
    ffmpeg \
    python3 \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Crea utente non-root
RUN useradd -m -s /bin/bash radio

# Copia file
COPY icecast.xml /etc/icecast2/
COPY start.sh /app/
COPY streamer.py /app/

# Permessi
RUN chmod +x /app/start.sh && chown -R radio:radio /app

# Cambia utente
USER radio
WORKDIR /app

# Avvia
CMD ["/bin/bash", "/app/start.sh"]
