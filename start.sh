#!/bin/bash
echo "=== AVVIO RADIO ==="
echo "1. Avvio Icecast..."
icecast2 -c /etc/icecast2/icecast.xml &
sleep 5
echo "2. Avvio Streamer Python..."
python3 /app/streamer.py
