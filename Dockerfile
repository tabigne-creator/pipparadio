FROM python:3.9-slim

# 1. Installa solo l'essenziale
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. NON installare icecast2 per ora (problemi di permessi su Render)
# 3. NON usare supervisor (troppo complesso per free tier)

WORKDIR /app

# 4. Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto il resto
COPY . .

# 6. Crea file audio semplice
RUN ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 60 -acodec libmp3lame static/silence.mp3 2>/dev/null || true

# 7. Esponi solo la porta di Flask
EXPOSE 10000

# 8. Avvio SEMPLICE - solo Flask per test
CMD ["python", "app.py"]
