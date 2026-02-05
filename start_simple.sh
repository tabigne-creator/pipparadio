#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - AVVIO SISTEMA"
echo "========================================="

# 1. Avvia Icecast in background
echo "1. 🎧 Avvio Icecast..."
icecast2 -c /etc/icecast2/icecast.xml &
ICE_PID=$!
sleep 5

# 2. Controlla Icecast
echo "2. 🔍 Controllo Icecast..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "   ✅ Icecast attivo su porta 8000"
else
    echo "   ⚠️  Icecast non risponde"
    echo "   🔧 Tentativo di riavvio..."
    kill $ICE_PID 2>/dev/null
    sleep 2
    icecast2 -c /etc/icecast2/icecast.xml &
    sleep 5
fi

# 3. Avvia Flask
echo "3. 🌐 Avvio server web Flask..."
python app.py &
FLASK_PID=$!
sleep 3

# 4. Controlla Flask
if curl -s http://localhost:10000/health > /dev/null; then
    echo "   ✅ Flask attivo su porta 10000"
else
    echo "   ⚠️  Flask non risponde"
fi

# 5. Info
echo ""
echo "========================================="
echo "🚀 SISTEMA AVVIATO!"
echo "========================================="
echo "• Web UI:    http://0.0.0.0:10000"
echo "• Icecast:   http://localhost:8000"
echo "• Stream:    http://localhost:8000/radio.mp3"
echo "• Health:    http://localhost:10000/health"
echo "========================================="
echo ""
echo "📻 Lo stream potrebbe essere silenzioso"
echo "   (solo file di test per ora)"
echo "========================================="

# 6. Mantieni container attivo
# Monitora i processi
while sleep 30; do
    if ! kill -0 $ICE_PID 2>/dev/null; then
        echo "⚠️  Icecast fermato, riavvio..."
        icecast2 -c /etc/icecast2/icecast.xml &
        ICE_PID=$!
    fi
    
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "⚠️  Flask fermato, riavvio..."
        python app.py &
        FLASK_PID=$!
    fi
    
    echo "❤️  Heartbeat - Sistema attivo"
done
