FROM python:3.9-slim

# Installa FFmpeg (solo per creare file audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copia i file
COPY app.py /app/
COPY requirements.txt /app/

# Cartella di lavoro
WORKDIR /app

# Installa dipendenze Python (nessuna in questo caso)
RUN pip install --no-cache-dir -r requirements.txt

# Esponi la porta che userà l'app
EXPOSE 10000

# Avvia l'app
CMD ["python", "app.py"]
