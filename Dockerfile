FROM python:3.9-slim

# Installa FFmpeg (solo per creare file audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crea file audio di 5 minuti
RUN mkdir -p static && \
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 300 -acodec libmp3lame static/silence.mp3 2>/dev/null || true

EXPOSE 10000

CMD ["bash", "start_simple.sh"]
