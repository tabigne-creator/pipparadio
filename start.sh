#!/bin/bash
echo "=== AVVIO RADIO ==="

# Avvia Icecast in background
echo "1. Avvio Icecast..."
icecast2 -c /etc/icecast2/icecast.xml &

# Attendi che Icecast sia pronto
echo "2. Attendo Icecast..."
sleep 5

# Avvia lo streamer Python dal percorso corretto
echo "3. Avvio streamer Python..."
python3 /app/streamer.py

echo "=== RADIO ATTIVA ==="
