import http.server
import socketserver
import threading
import time
import os

print("=== RADIO SERVER AVVIATO ===")

# 1. Genera un file MP3 di silenzio/tone se non esiste
AUDIO_FILE = "/app/radio.mp3"
if not os.path.exists(AUDIO_FILE):
    print(f"Creazione {AUDIO_FILE}...")
    os.system(f'ffmpeg -f lavfi -i "anullsrc=r=44100:cl=mono" -t 3600 -acodec libmp3lame -b:a 128k {AUDIO_FILE} 2>/dev/null')
    print(f"File creato: {os.path.getsize(AUDIO_FILE)} bytes")

# 2. Crea un handler HTTP che serve lo stream MP3
class RadioHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/radio.mp3' or self.path == '/stream':
            # Intestazioni per streaming audio
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.send_header('Pragma', 'no-cache')
            
            # Leggi il file audio (lo rileggiamo in loop per stream infinito)
            file_size = os.path.getsize(AUDIO_FILE)
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
            # Invia il file audio in loop (per stream 24/7)
            while True:
                try:
                    with open(AUDIO_FILE, 'rb') as f:
                        self.wfile.write(f.read())
                except (ConnectionResetError, BrokenPipeError):
                    break  # Client disconnesso
                    
        elif self.path == '/':
            # Pagina HTML semplice con player
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>Radio IRC</title></head>
            <body>
                <h1>📻 Radio IRC Stream</h1>
                <audio controls autoplay>
                    <source src="/radio.mp3" type="audio/mpeg">
                    Il tuo browser non supporta l'audio.
                </audio>
                <p><a href="/radio.mp3">Link diretto stream</a></p>
                <p>Per IRC bot: https://pipparadio.onrender.com/radio.mp3</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/status':
            # Endpoint per bot IRC
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            status = {
                "status": "online",
                "listeners": 1,
                "song": "Radio IRC Stream",
                "url": "https://pipparadio.onrender.com/radio.mp3"
            }
            self.wfile.write(json.dumps(status).encode())
            
        else:
            self.send_error(404)

# 3. Avvia il server HTTP su porta 10000 (Render lo mapperà a 80)
def run_server():
    port = 10000  # Porta interna, Render la mapperà automaticamente
    with socketserver.TCPServer(("", port), RadioHandler) as httpd:
        print(f"Radio server in ascolto su porta {port}")
        print(f"Stream URL: http://localhost:{port}/radio.mp3")
        httpd.serve_forever()

# 4. Avvia server in thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# 5. Mantieni il processo attivo
print("=== RADIO ATTIVA ===")
print("In attesa di connessioni...")
while True:
    time.sleep(3600)
