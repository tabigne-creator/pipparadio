#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - DEBUG MODE"
echo "========================================="

# 0. Mostra info sistema
echo "0. 📊 Informazioni sistema:"
echo "   Hostname: $(hostname)"
echo "   Working dir: $(pwd)"
echo "   Free memory: $(free -m | awk 'NR==2{print $4}')MB"

# 1. Verifica file Icecast
echo "1. 🔍 Verifica file Icecast..."
if [ -f /etc/icecast2/icecast.xml ]; then
    echo "   ✅ icecast.xml trovato"
    echo "   Porta configurata: $(grep '<port>' /etc/icecast2/icecast.xml)"
else
    echo "   ❌ icecast.xml NON trovato!"
    # Crea config minima
    cat > /etc/icecast2/icecast.xml << EOF
<icecast>
    <limits>
        <clients>10</clients>
        <sources>1</sources>
    </limits>
    <authentication>
        <source-password>hackme</source-password>
    </authentication>
    <listen-socket>
        <port>8000</port>
        <bind-address>0.0.0.0</bind-address>
    </listen-socket>
</icecast>
EOF
    echo "   📝 Creato file minimale"
fi

# 2. Crea directory per log con permessi
echo "2. 📁 Setup directory..."
mkdir -p /var/log/icecast2
chmod 777 /var/log/icecast2 2>/dev/null || true

# 3. Prova Icecast in foreground per vedere errori
echo "3. 🎧 Avvio Icecast (foreground)..."
timeout 10 icecast2 -c /etc/icecast2/icecast.xml 2>&1 | head -20 &
ICE_PID=$!
sleep 3

# 4. Controlla se Icecast risponde
echo "4. 🔌 Test connessione Icecast..."
if curl -s --connect-timeout 5 http://localhost:8000 > /dev/null; then
    echo "   ✅ Icecast ATTIVO su localhost:8000"
    ICE_ACTIVE=true
else
    echo "   ❌ Icecast NON risponde"
    echo "   📝 Log Icecast (ultime 5 righe):"
    icecast2 -c /etc/icecast2/icecast.xml -b 2>&1 | tail -5 &
    ICE_PID=$!
    sleep 2
    ICE_ACTIVE=false
fi

# 5. Avvia Flask in ogni caso
echo "5. 🌐 Avvio Flask..."
python app.py &
FLASK_PID=$!
sleep 2

if curl -s http://localhost:10000/health > /dev/null; then
    echo "   ✅ Flask attivo su porta 10000"
else
    echo "   ⚠️  Flask non risponde, riprovo..."
    pkill -f "python app.py" 2>/dev/null
    sleep 1
    python app.py &
    FLASK_PID=$!
    sleep 3
fi

# 6. Mostra stato finale
echo ""
echo "========================================="
echo "📊 STATO FINALE"
echo "========================================="
echo "Icecast running: $ICE_ACTIVE"
echo "Flask running:   $(curl -s -o /dev/null -w "%{http_code}" http://localhost:10000/health)"
echo ""
echo "🔗 URL ESTERNI (Render):"
echo "• Web:     https://pipparadio-1.onrender.com"
echo "• Health:  https://pipparadio-1.onrender.com/health"
echo "• Status:  https://pipparadio-1.onrender.com/status"
echo "• Test:    https://pipparadio-1.onrender.com/test"
echo ""
echo "🔗 URL INTERNI (container):"
echo "• Flask:   http://localhost:10000"
echo "• Icecast: http://localhost:8000"
echo "========================================="

# 7. Se Icecast non funziona, usa fallback
if [ "$ICE_ACTIVE" = "false" ]; then
    echo ""
    echo "⚠️  SOLUZIONE ALTERNATIVA:"
    echo "Icecast non funziona, Flask servirà file audio direttamente"
    echo "Lo stream sarà disponibile su: /radio.mp3"
fi

# 8. Mantieni attivo
echo ""
echo "🔄 Monitoraggio attivo..."
while true; do
    echo "$(date): ❤️  Heartbeat - Container attivo"
    sleep 60
done
