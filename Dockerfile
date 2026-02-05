FROM ubuntu:22.04

# 1. Installa i pacchetti
RUN apt-get update && apt-get install -y \
    icecast2 \
    ffmpeg \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# 2. Crea un utente dedicato 'radio' (Risolve errore "run as root")
RUN useradd -m -s /bin/bash radio

# 3. Crea struttura directory e imposta i permessi
RUN mkdir -p /music /app && chown -R radio:radio /music /app

# 4. Copia i file di configurazione nell'immagine
COPY icecast.xml /etc/icecast2/icecast.xml
COPY start.sh /app/
COPY streamer.py /app/

# 5. Rendi eseguibile lo script e imposta il proprietario
RUN chmod +x /app/start.sh && chown -R radio:radio /app

# 6. Esponi la porta 80
EXPOSE 80

# 7. Cambia utente (IMPORTANTE: non più root)
USER radio
WORKDIR /app

# 8. Comando di avvio
CMD ["/bin/bash", "/app/start.sh"]
