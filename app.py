import http.server
import socketserver
import threading
import time
import os
import sys

print("=== RADIO SERVER AVVIATO ===")
print(f"Python: {sys.version}")
print(f"Directory corrente: {os.getcwd()}")
print(f"Contenuto iniziale: {os.listdir('.')}")

# ============================================
# 1. GESTIONE CARTELLA MUSIC (IN FALLIBILE)
# ============================================
MUSIC_FOLDER = "/app/music"

# Se esiste un FILE (non cartella) chiamato 'music', lo rinominiamo
if os.path.exists("/app/music") and os.path.isfile("/app/music"):
    new_name = "/app/music_old_file_backup"
    os.rename("/app/music", new_name)
    print(f"⚠️  Trovato FILE 'music' -> rinominato in '{new_name}'")

# Crea la cartella music (se non esiste)
os.makedirs(MUSIC_FOLDER, exist_ok=True)
print(f"✅ Cartella music garantita: {MUSIC_FOLDER}")
print(f"   Contenuto music: {os.listdir(MUSIC_FOLDER)}")

# ============================================
# 2. CREA FILE AUDIO DI DEFAULT (SILENZIO)
# ============================================
AUDIO_FILE = "/app/radio.mp3"

if not os.path.exists(AUDIO_FILE):
    print(f"🎵 Creazione file audio di default (silenzio)...")
    # Crea 2 ore di silenzio assoluto
    cmd = 'ffmpeg -f lavfi -i "anullsrc=r=44100:cl=mono" -t 7200 -acodec libmp3lame -b:a 128k /app/radio.mp3 2>&1'
    result = os.system(cmd)
    if result == 0:
        print(f"✅ File audio creato: {os.path.getsize(AUDIO_FILE)} bytes")
    else:
        print(f"⚠️  FFmpeg potrebbe aver avuto problemi (codice: {result})")
else:
    print(f"✅ File audio già esistente: {os.path.getsize(AUDIO_FILE)} bytes")

# ============================================
# 3. HANDLER HTTP PER LA RADIO
# ============================================
class RadioHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Riduci il logging per pulire i log
        pass
    
    def do_GET(self):
        if self.path == '/radio.mp3' or self.path == '/stream':
            # STREAM AUDIO
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.end_headers()
            
            print(f"📡 Streaming audio a {self.client_address[0]}")
            
            # Stream infinito del file audio
            while True:
                try:
                    with open(AUDIO_FILE, 'rb') as f:
                        while True:
                            chunk = f.read(8192)  # Leggi in blocchi da 8KB
                            if not chunk:
                                f.seek(0)  # Torna all'inizio del file
                                continue
                            self.wfile.write(chunk)
                except (ConnectionResetError, BrokenPipeError, OSError):
                    print(f"🔌 Client disconnesso: {self.client_address[0]}")
                    break
                    
        elif self.path == '/':
            # PAGINA HTML CON PLAYER
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>📻 Radio IRC</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
                    .player { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    audio { width: 100%; }
                    .url-box { background: #e9e9e9; padding: 10px; border-radius: 5px; font-family: monospace; }
                </style>
            </head>
            <body>
                <h1>📻 Radio IRC Stream</h1>
                <p>Il tuo server radio è attivo e funzionante!</p>
                
                <div class="player">
                    <h3>🎵 Player Live</h3>
                    <audio controls autoplay>
                        <source src="/radio.mp3" type="audio/mpeg">
                        Il tuo browser non supporta l'elemento audio.
                    </audio>
                </div>
                
                <div class="url-box">
                    <strong>URL Stream per IRC Bot:</strong><br>
                    https://pipparadio.onrender.com/radio.mp3
                </div>
                
                <p><a href="/radio.mp3" download>📥 Scarica stream</a> | 
                   <a href="/status">📊 Status JSON</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/status':
            # ENDPOINT STATUS PER BOT IRC
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            import json
            import datetime
            
            status = {
                "radio": "pipparadio",
                "status": "online",
                "url": "https://pipparadio.onrender.com/radio.mp3",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_info": {
                    "python": sys.version.split()[0],
                    "directory": os.getcwd(),
                    "files_in_music": len(os.listdir(MUSIC_FOLDER))
                }
            }
            self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))
            
        else:
            self.send_error(404, "Pagina non trovata")

# ============================================
# 4. AVVIO SERVER HTTP
# ============================================
def run_server():
    PORT = 10000
    print(f"🌐 Avvio server HTTP su porta {PORT}...")
    
    with socketserver.TCPServer(("", PORT), RadioHandler) as httpd:
        print(f"✅ Server in ascolto su http://0.0.0.0:{PORT}")
        print(f"   • Player: http://localhost:{PORT}/")
        print(f"   • Stream: http://localhost:{PORT}/radio.mp3")
        print(f"   • Status: http://localhost:{PORT}/status")
        print("\n" + "="*50)
        print("📻 LA TUA RADIO È PRONTA PER IRC!")
        print("="*50 + "\n")
        
        httpd.serve_forever()

# ============================================
# 5. AVVIO TUTTO
# ============================================
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Mantieni il processo attivo
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    print("\n🛑 Server arrestato")
