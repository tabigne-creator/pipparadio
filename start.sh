#!/bin/bash

echo "========================================="
echo "🎵  RADIO IRC - AVVIO SISTEMA"
echo "========================================="

# Crea directory per log
mkdir -p /var/log/icecast2
chown -R icecast2:icecast2 /var/log/icecast2

# Avvia Icecast
echo "1. 🎧 Avvio Icecast server..."
icecast2 -c /etc/icecast2/icecast.xml &
ICECAST_PID=$!
sleep 5

# Controlla se Icecast è attivo
if ps -p $ICECAST_PID > /dev/null; then
    echo "   ✅ Icecast attivo (PID: $ICECAST_PID)"
else
    echo "   ❌ Icecast non avviato"
    exit 1
fi

# Attendi che Icecast sia pronto
echo "2. ⏳ Attesa preparazione Icecast..."
sleep 10

# Avvia Flask web server
echo "3. 🌐 Avvio server web Flask..."
python app.py &
FLASK_PID=$!
sleep 3

if ps -p $FLASK_PID > /dev/null; then
    echo "   ✅ Flask attivo (PID: $FLASK_PID)"
    echo "   🔗 Web server: http://localhost:10000"
else
    echo "   ⚠️  Flask non avviato correttamente"
fi

# Avvia streamer audio
echo "4. 🔊 Avvio streamer audio..."
python streamer.py &
STREAMER_PID=$!
sleep 2

if ps -p $STREAMER_PID > /dev/null; then
    echo "   ✅ Streamer attivo (PID: $STREAMER_PID)"
else
    echo "   ⚠️  Streamer non avviato"
fi

echo ""
echo "========================================="
echo "🚀 SISTEMA AVVIATO CON SUCCESSO!"
echo "========================================="
echo ""
echo "📊 SERVIZI ATTIVI:"
echo "   • Icecast:    http://localhost:8000"
echo "   • Web UI:     http://localhost:10000"
echo "   • Stream:     http://localhost:10000/radio.mp3"
echo "   • API Status: http://localhost:10000/status"
echo ""
echo "📝 LOG:"
echo "   tail -f /var/log/supervisor/*.log"
echo ""
echo "🛑 Per fermare: Ctrl+C"
echo "========================================="

# Mantieni il container attivo
wait
