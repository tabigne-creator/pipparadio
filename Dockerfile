FROM python:3.9-slim

# 1. Installa FFmpeg e Icecast
RUN apt-get update && apt-get install -y \
    ffmpeg \
    icecast2 \
    && rm -rf /var/lib/apt/lists/*

# 2. Crea directory per l'app
WORKDIR /app

# 3. Copia requirements
COPY requirements.txt .

# 4. Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto
COPY . .

# 6. Copia configurazione Icecast
COPY icecast.xml /etc/icecast2/icecast.xml

# 7. Crea file audio
RUN mkdir -p static && \
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 600 -acodec libmp3lame static/silence.mp3 2>/dev/null || echo "Audio created"

# 8. Esponi porte
EXPOSE 10000
EXPOSE 8000

# 9. Script di avvio semplice
CMD ["bash", "start_simple.sh"]
