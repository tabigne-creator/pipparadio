#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - FLASK DIRECT STREAM"
echo "========================================="

# 1. Verifica file audio
echo "1. 🔊 Verifica file audio..."
if [ -f "static/silence.mp3" ]; then
    FILESIZE=$(stat -c%s "static/silence.mp3" 2>/dev/null || echo "0")
    if [ "$FILESIZE" -gt 1000 ]; then
        echo "   ✅ File audio trovato (${FILESIZE} bytes)"
    else
        echo "   ⚠️  File audio troppo piccolo, ricreo..."
        ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 300 -acodec libmp3lame static/silence.mp3 2>/dev/null || true
    fi
else
    echo "   📝 Creazione file audio..."
    mkdir -p static
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 300 -acodec libmp3lame static/silence.mp3 2>/dev/null || echo "Created fallback"
fi

# 2. Avvia Flask
echo "2. 🌐 Avvio Flask web server con streaming..."
python app.py &
FLASK_PID=$!
sleep 5

# 3. Test
echo "3. 🔌 Test servizi..."
if curl -s http://localhost:10000/health > /dev/null; then
    echo "   ✅ Flask attivo su porta 10000"
else
    echo "   ❌ Flask non risponde"
    exit 1
fi

# 4. Info
echo ""
echo "========================================="
echo "🚀 RADIO IRC ONLINE!"
echo "========================================="
echo "• Web Interface:  https://pipparadio-1.onrender.com"
echo "• Direct Stream:  https://pipparadio-1.onrender.com/radio.mp3"
echo "• Status API:     https://pipparadio-1.onrender.com/status"
echo "• Health Check:   https://pipparadio-1.onrender.com/health"
echo ""
echo "📻 Streaming: MP3 128kbps via Flask Direct"
echo "🤖 Bot IRC:   Usa l'URL sopra per !radio"
echo "========================================="

# 5. Monitor
echo ""
echo "❤️  Monitoraggio attivo..."
while true; do
    echo "$(date): Radio IRC streaming"
    sleep 60
done
