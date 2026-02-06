#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - FLASK DIRECT STREAM"
echo "========================================="

# 1. Verifica file audio
echo "1. 🔊 Setup audio..."
if [ ! -f "static/silence.mp3" ] || [ ! -s "static/silence.mp3" ]; then
    echo "   📝 Creazione file audio..."
    mkdir -p static
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 300 -acodec libmp3lame static/silence.mp3 2>/dev/null || echo "Audio placeholder"
else
    echo "   ✅ File audio esistente"
fi

# 2. Avvia Flask
echo "2. 🌐 Avvio server Flask..."
python app.py &
FLASK_PID=$!
sleep 5

# 3. Test
echo "3. 🔌 Test connessione..."
if curl -s http://localhost:10000/health > /dev/null; then
    echo "   ✅ Server attivo"
else
    echo "   ⚠️  Server lento, aspetto..."
    sleep 5
fi

# 4. Info
echo ""
echo "========================================="
echo "🚀 RADIO ONLINE!"
echo "========================================="
echo "• Web:     https://pipparadio-1.onrender.com"
echo "• Stream:  https://pipparadio-1.onrender.com/radio.mp3"
echo "• Status:  https://pipparadio-1.onrender.com/status"
echo "• Health:  https://pipparadio-1.onrender.com/health"
echo ""
echo "📻 Streaming: MP3 via Flask Direct"
echo "🤖 Bot IRC: Pronto per !radio comando"
echo "========================================="

# 5. Monitor
echo ""
echo "❤️  Sistema attivo..."
while true; do
    sleep 60
    echo "$(date): Radio IRC streaming"
done
