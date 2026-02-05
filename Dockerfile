FROM python:3.9-slim

# Installa FFmpeg, Icecast e dipendenze di sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    icecast2 \
    supervisor \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crea directory per l'app
WORKDIR /app

# Prima copia i requirements per cache efficiente
COPY requirements.txt .

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutti i file dell'app
COPY . .

# Copia configurazione Icecast
COPY icecast.xml /etc/icecast2/icecast.xml

# Crea file di silenzio se non esiste
RUN if [ ! -f static/silence.mp3 ]; then \
    echo "Creazione file di silenzio..." && \
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 3600 -q:a 9 -acodec libmp3lame static/silence.mp3 2>/dev/null || \
    echo "FFmpeg potrebbe non aver funzionato, useremo un file placeholder"; \
    fi

# Crea directory per log e assicura permessi
RUN mkdir -p /var/log/icecast2 /var/log/supervisor \
    && chown -R icecast2:icecast2 /var/log/icecast2 \
    && chmod 755 start.sh

# Configurazione Supervisor per gestire processi multipli
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Esponi le porte
EXPOSE 10000  # Flask web server
EXPOSE 8000   # Icecast HTTP
EXPOSE 80     # Icecast alternativa

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Avvia con Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
