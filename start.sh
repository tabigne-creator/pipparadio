#!/bin/bash
echo "=== DEBUG AVVIO RADIO ==="
echo "1. Controllo utente corrente..."
whoami
id

echo "2. Controllo se Icecast è già in esecuzione..."
netstat -tlnp 2>/dev/null | grep :80 || echo "Nessun servizio sulla porta 80"

echo "3. Controllo file di configurazione Icecast..."
ls -la /etc/icecast2/icecast.xml
echo "Contenuto prime 10 righe:"
head -10 /etc/icecast2/icecast.xml

echo "4. Provo ad avviare Icecast in modalità DEBUG..."
icecast2 -c /etc/icecast2/icecast.xml -b -v &
ICECAST_PID=$!
sleep 3

echo "5. Controllo se Icecast è vivo..."
if ps -p $ICECAST_PID > /dev/null; then
    echo "✅ Icecast è in esecuzione (PID: $ICECAST_PID)"
    echo "Controllo porta 80..."
    curl -s -o /dev/null -w "Codice HTTP: %{http_code}\n" http://localhost:80/ || echo "Curl fallito"
else
    echo "❌ Icecast NON è in esecuzione"
    echo "Ultimi errori Icecast (se presenti):"
    journalctl -u icecast2 --no-pager -n 20 2>/dev/null || echo "Journal non disponibile"
fi

echo "6. Avvio streamer Python..."
echo "Directory corrente per Python: $(pwd)"
ls -la
python3 --version

# Avvia streamer.py dal percorso corretto
if [ -f "/app/streamer.py" ]; then
    echo "Trovato /app/streamer.py"
    cd /app
    exec python3 streamer.py
else
    echo "ERRORE: /app/streamer.py non trovato!"
    echo "Cercando streamer.py in altre location..."
    find / -name "streamer.py" 2>/dev/null
    sleep 3600  # Mantiene il container attivo per debugging
fi
