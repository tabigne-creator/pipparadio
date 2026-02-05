#!/bin/bash
echo "=== AVVIO RADIO CON SERVER WEB ==="

# 1. Avvia Icecast (in background)
echo "1. Avvio Icecast..."
icecast2 -c /etc/icecast2/icecast.xml &
ICECAST_PID=$!
sleep 5

# 2. Controlla se Icecast è vivo
if ps -p $ICECAST_PID > /dev/null; then
    echo "✅ Icecast attivo (PID: $ICECAST_PID)"
else
    echo "❌ Icecast fallito"
fi

# 3. AVVIA UN SERVER WEB SEMPLICE SU PORTA 8080 (per Render)
echo "2. Avvio server web beacon su porta 8080..."
python3 - << 'EOF'
import http.server
import socketserver
import threading

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Radio OK')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = b"""
            <html><body>
            <h1>Radio IRC Stream</h1>
            <p>Icecast is running.</p>
            <p>Stream URL: <a href="/radio.mp3">/radio.mp3</a></p>
            </body></html>
            """
            self.wfile.write(html)

def run_server():
    port = 8080
    with socketserver.TCPServer(("", port), HealthHandler) as httpd:
        print(f"Server beacon in ascolto su porta {port}")
        httpd.serve_forever()

# Avvia server in thread separato
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print("Server web beacon attivo")
EOF &
SERVER_PID=$!

# 4. Aspetta un secondo per il server
sleep 2

# 5. Controlla se il server web è attivo
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server web beacon attivo (Render dovrebbe rilevare la porta 8080)"
else
    echo "⚠️  Server web non partito"
fi

# 6. FINALMENTE avvia lo streamer
echo "3. Avvio streamer audio..."
cd /app
exec python3 streamer.py
