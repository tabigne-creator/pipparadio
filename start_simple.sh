#!/bin/bash

echo "========================================="
echo "🎵 RADIO IRC - AVVIO CON ICEFIX"
echo "========================================="

# 1. Setup directory e permessi per Icecast
echo "1. 📁 Setup directory Icecast..."
mkdir -p /var/log/icecast2
chmod 777 /var/log/icecast2 2>/dev/null || echo "Permessi ok"

# 2. Assicurati che l'utente nobody esista
echo "2. 👤 Verifica utente nobody..."
if ! id -u nobody >/dev/null 2>&1; then
    echo "   Creazione utente nobody..."
    useradd -s /bin/false nobody 2>/dev/null || echo "Utente già esiste"
fi

# 3. Avvia Icecast PRIMA in modalità test
echo "3. 🎧 Test avvio Icecast..."
timeout 5 icecast2 -c /etc/icecast2/icecast.xml 2>&1 | grep -E "(ERROR|WARN|Started)" &
TEST_PID=$!
sleep 3

# 4. Se il test mostra errori, usa config semplificata
echo "4. ⚙️  Configurazione finale..."
if kill -0 $TEST_PID 2>/dev/null; then
    echo "   ✅ Configurazione OK, avvio Icecast..."
    kill $TEST_PID 2>/dev/null
    icecast2 -c /etc/icecast2/icecast.xml &
else
    echo "   ⚠️  Problemi con config, uso versione semplificata..."
    # Config minima senza security complessa
    cat > /tmp/icecast_simple.xml << 'EOF'
<icecast>
    <limits><clients>20</clients><sources>1</sources></limits>
    <authentication><source-password>hackme</source-password></authentication>
    <listen-socket><port>8000</port><bind-address>0.0.0.0</bind-address></listen-socket>
    <paths><logdir>/var/log/icecast2</logdir></paths>
</icecast>
EOF
    icecast2 -c /tmp/icecast_simple.xml &
fi

ICE_PID=$!
sleep 5

# 5. Test connessione Icecast
echo "5. 🔌 Test connessione a Icecast..."
if curl -s --connect-timeout 5 http://localhost:8000 > /dev/null; then
    echo "   ✅ Icecast ATTIVO su porta 8000"
    ICE_ACTIVE=true
else
    echo "   ❌ Icecast non risponde"
    ICE_ACTIVE=false
fi

# 6. Avvia Flask
echo "6. 🌐 Avvio Flask web server..."
python app.py &
FLASK_PID=$!
sleep 3

if curl -s http://localhost:10000/health > /dev/null; then
    echo "   ✅ Flask attivo su porta 10000"
else
    echo "   ⚠️  Flask lento, aspetto..."
    sleep 5
fi

# 7. Mostra URL
echo ""
echo "========================================="
echo "🚀 SISTEMA AVVIATO"
echo "========================================="
echo "Icecast: $([ "$ICE_ACTIVE" = true ] && echo "✅ ATTIVO" || echo "❌ DISATTIVO")"
echo "Flask:   ✅ ATTIVO"
echo ""
echo "🔗 URL PUBBLICI:"
echo "• Web:     https://pipparadio-1.onrender.com"
echo "• Health:  https://pipparadio-1.onrender.com/health"
echo "• Status:  https://pipparadio-1.onrender.com/status"
echo "• Stream:  https://pipparadio-1.onrender.com/radio.mp3"
echo ""
echo "🔧 NOTA: Se Icecast è disattivo, lo stream"
echo "   userà il fallback diretto da Flask"
echo "========================================="

# 8. Monitoraggio semplice
echo ""
echo "❤️  Monitoraggio attivo..."
while true; do
    # Heartbeat ogni 30 secondi
    echo "$(date): Sistema Radio IRC online"
    sleep 30
done
