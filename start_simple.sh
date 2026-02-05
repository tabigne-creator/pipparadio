#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - AVVIO SISTEMA"
echo "========================================="

# 1. Avvia Icecast in background
echo "1. 🎧 Avvio Icecast..."
icecast2 -c /etc/icecast2/icecast.xml &
sleep 5

# 2. Controlla Icecast
if curl -s http://localhost:8000 > /dev/null; then
    echo "   ✅ Icecast attivo su porta 8000"
else
    echo "   ⚠️  Icecast non risponde"
fi

# 3. Avvia Flask
echo "2. 🌐 Avvio server web Flask..."
python app.py &
sleep 3

# 4. Info
echo ""
echo "========================================="
echo "🚀 SISTEMA AVVIATO!"
echo "========================================="
echo "• Web UI:    http://0.0.0.0:10000"
echo "• Icecast:   http://localhost:8000"
echo "• Stream:    http://localhost:8000/radio.mp3"
echo "========================================="

# 5. Mantieni container attivo
wait
