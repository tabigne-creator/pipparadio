#!/usr/bin/env python3
"""
Radio Server 24/7 per IRC
Stream audio infinito su https://pipparadio.onrender.com/radio.mp3
"""

import http.server
import socketserver
import threading
import time
import os
import sys
import json
import datetime

print("=" * 60)
print("📻 RADIO IRC SERVER - AVVIO")
print("=" * 60)

# ============================================================================
# 1. CONFIGURAZIONE INIZIALE E SETUP SISTEMA
# ============================================================================

# Directory base dell'applicazione
BASE_DIR = "/app"
os.chdir(BASE_DIR)

print(f"📍 Directory: {os.getcwd()}")
print(f"📁 Contenuto iniziale: {os.listdir('.')}")

# Crea cartella per musica (gestisce qualsiasi situazione)
MUSIC_DIR = "/app/music"
try:
    # Se esiste un FILE chiamato 'music', lo rinomina
    if os.path.exists(MUSIC_DIR) and os.path.isfile(MUSIC_DIR):
        backup_name = f"{MUSIC_DIR}_backup_{int(time.time())}"
        os.rename(MUSIC_DIR, backup_name)
        print(f"⚠️  File 'music' rinominato in: {backup_name}")
    
    # Crea la cartella (se non esiste)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    print(f"✅ Cartella music: {MUSIC_DIR}")
    
except Exception as e:
    print(f"⚠️  Nota sulla cartella music: {e}")

# File MP3 di default (silenzio)
DEFAULT_AUDIO = "/app/default_silence.mp3"

# ============================================================================
# 2. CREAZIONE CONTENUTO AUDIO DI DEFAULT
# ============================================================================

def create_silence_mp3():
    """Crea un file MP3 di silenzio (60 minuti)"""
    print("\n🎵 Creazione audio di default...")
    
    # Usa FFmpeg per creare silenzio MP3
    # Nota: su Render Free, potremmo avere limiti di tempo per FFmpeg
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=mono',  # Silenzio puro
        '-t', '600',  # 10 minuti (Render Free potrebbe limitare processi lunghi)
        '-acodec', 'libmp3lame',
        '-b:a', '128k',
        '-ar', '44100',
        '-ac', '1',  # Mono
        DEFAULT_AUDIO
    ]
    
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(DEFAULT_AUDIO):
            size = os.path.getsize(DEFAULT_AUDIO)
            print(f"✅ Audio creato: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
            # Duplica il file per avere più contenuto
            if size < 2 * 1024 * 1024:  # Se meno di 2MB
                with open(DEFAULT_AUDIO, 'ab') as f:
                    f.write(open(DEFAULT_AUDIO, 'rb').read())
                print(f"✅ Audio esteso: {os.path.getsize(DEFAULT_AUDIO):,} bytes")
        else:
            print(f"⚠️  FFmpeg potrebbe aver avuto problemi")
            if result.stderr:
                print(f"   Errori: {result.stderr[:200]}")
            
    except Exception as e:
        print(f"⚠️  Nota FFmpeg: {type(e).__name__}")

# Crea il file audio solo se non esiste
if not os.path.exists(DEFAULT_AUDIO):
    create_silence_mp3()
else:
    size = os.path.getsize(DEFAULT_AUDIO)
    print(f"✅ Audio esistente: {size:,} bytes")

# ============================================================================
# 3. HANDLER HTTP PRINCIPALE
# ============================================================================

class RadioHTTPHandler(http.server.BaseHTTPRequestHandler):
    """Gestisce tutte le richieste HTTP per la radio"""
    
    # Disabilita logging di ogni richiesta (troppo rumoroso)
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        """Gestisce richieste GET"""
        
        # 📡 ENDPOINT: STREAM AUDIO PRINCIPALE
        if self.path == '/radio.mp3' or self.path == '/stream':
            self.handle_audio_stream()
            
        # 🏠 ENDPOINT: PAGINA PRINCIPALE CON PLAYER
        elif self.path == '/':
            self.handle_homepage()
            
        # 📊 ENDPOINT: STATO PER BOT IRC (JSON)
        elif self.path == '/status':
            self.handle_status()
            
        # 🔧 ENDPOINT: INFORMAZIONI TECNICHE
        elif self.path == '/info':
            self.handle_info()
            
        # ❓ ENDPOINT: HEALTH CHECK
        elif self.path == '/health':
            self.handle_health()
            
        # 📁 ENDPOINT: LISTA FILE MUSICA
        elif self.path == '/music':
            self.handle_music_list()
            
        else:
            self.send_error(404, "Endpoint non trovato")
    
    # ============================================================================
    # 4. METODI HANDLER SPECIFICI
    # ============================================================================
    
    def handle_audio_stream(self):
        """Streamma audio in loop infinito 24/7"""
        print(f"📡 [{datetime.datetime.now().strftime('%H:%M:%S')}] "
              f"Nuovo ascoltatore: {self.client_address[0]}")
        
        try:
            # Intestazioni per streaming MP3
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            
            # Importante: NON inviare Content-Length per streaming infinito
            self.end_headers()
            
            bytes_sent = 0
            start_time = time.time()
            
            # 🔄 LOOP INFINITO DI STREAMING
            while True:
                # PRIMA SCELTA: Musica dalla cartella /music
                music_files = self.get_music_files()
                if music_files:
                    # Streamma un file musicale casuale
                    import random
                    song_file = random.choice(music_files)
                    print(f"   🎶 Playing: {os.path.basename(song_file)}")
                    
                    with open(song_file, 'rb') as f:
                        while True:
                            chunk = f.read(16384)  # 16KB chunks
                            if not chunk:
                                break  # Fine file
                            
                            self.wfile.write(chunk)
                            bytes_sent += len(chunk)
                            
                            # Log ogni 5MB
                            if bytes_sent % (5 * 1024 * 1024) == 0:
                                elapsed = time.time() - start_time
                                kbps = (bytes_sent * 8 / 1024) / elapsed if elapsed > 0 else 0
                                print(f"   📊 Stream: {bytes_sent//(1024*1024)}MB "
                                      f"({kbps:.0f} kbps)")
                
                # SECONDA SCELTA: Silenzio di default (loop)
                else:
                    # Leggi il file di default in loop
                    with open(DEFAULT_AUDIO, 'rb') as f:
                        audio_data = f.read()
                    
                    while True:
                        self.wfile.write(audio_data)
                        bytes_sent += len(audio_data)
                        
                        # Log ogni minuto
                        if int(time.time() - start_time) % 60 == 0:
                            print(f"   🔊 Silenzio stream: {bytes_sent//(1024*1024)}MB "
                                  f"({int(time.time() - start_time)//60} min)")
                        
                        # Piccola pausa per non saturare la CPU
                        time.sleep(0.01)
                        
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            # Client disconnesso - normale per streaming
            elapsed = time.time() - start_time
            print(f"🔌 [{datetime.datetime.now().strftime('%H:%M:%S')}] "
                  f"Disconnesso dopo {elapsed:.1f}s: "
                  f"{bytes_sent//1024}KB inviati")
        except Exception as e:
            print(f"⚠️  Errore stream: {type(e).__name__}: {e}")
    
    def handle_homepage(self):
        """Pagina HTML con player integrato"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        music_files = self.get_music_files()
        music_count = len(music_files)
        
        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📻 Radio IRC - Stream 24/7</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ 
            font-size: 2.8em; 
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .subtitle {{ 
            font-size: 1.2em; 
            opacity: 0.9;
            margin-bottom: 30px;
        }}
        .player-box {{ 
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
        }}
        audio {{ 
            width: 100%; 
            border-radius: 10px;
            margin: 15px 0;
        }}
        .url-box {{ 
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }}
        .stats {{ 
            display: flex;
            gap: 20px;
            margin-top: 25px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            flex: 1;
            min-width: 150px;
        }}
        .links {{ margin-top: 30px; }}
        .links a {{
            color: #a3e4ff;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            display: inline-block;
            transition: all 0.3s;
        }}
        .links a:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📻 Radio IRC Stream</h1>
        <p class="subtitle">Stream audio 24/7 per il tuo canale IRC</p>
        
        <div class="player-box">
            <h2>🎵 Player Live</h2>
            <p>La radio è attiva {music_count} brani disponibili</p>
            <audio controls autoplay>
                <source src="/radio.mp3" type="audio/mpeg">
                Il tuo browser non supporta l'elemento audio.
            </audio>
            <p><small>Il player potrebbe avere un ritardo di 10-30 secondi</small></p>
        </div>
        
        <div class="url-box">
            <strong>🔗 URL Stream per Bot IRC:</strong><br>
            <code>https://pipparadio.onrender.com/radio.mp3</code>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📁 File</h3>
                <p>{music_count} brani in libreria</p>
            </div>
            <div class="stat-card">
                <h3>⏱️ Uptime</h3>
                <p>24/7 garantito</p>
            </div>
            <div class="stat-card">
                <h3>🔧 Formato</h3>
                <p>MP3 • 128kbps • 44.1kHz</p>
            </div>
        </div>
        
        <div class="links">
            <a href="/radio.mp3" target="_blank">🎧 Link diretto stream</a>
            <a href="/status" target="_blank">📊 Status JSON</a>
            <a href="/info" target="_blank">🔧 Informazioni tecniche</a>
            <a href="/music" target="_blank">📁 Lista musica</a>
        </div>
    </div>
    
    <script>
        // Auto-refresh dello stato ogni 30 secondi
        setInterval(() => {{
            fetch('/status')
                .then(r => r.json())
                .then(data => {{
                    console.log('Radio status:', data.status);
                }});
        }}, 30000);
        
        // Monitora errori del player
        const audio = document.querySelector('audio');
        audio.addEventListener('error', (e) => {{
            console.error('Audio error:', audio.error);
            alert('Problema con lo stream. Ricarica la pagina.');
        }});
    </script>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def handle_status(self):
        """Restituisce stato in JSON per bot IRC"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        status = {
            "radio": "pipparadio",
            "status": "online",
            "stream_url": "https://pipparadio.onrender.com/radio.mp3",
            "timestamp": datetime.datetime.now().isoformat(),
            "server_time": time.time(),
            "stats": {
                "music_files": len(self.get_music_files()),
                "default_audio_size": os.path.getsize(DEFAULT_AUDIO) if os.path.exists(DEFAULT_AUDIO) else 0,
                "server_uptime": int(time.time() - server_start_time),
                "python_version": sys.version.split()[0]
            },
            "endpoints": {
                "home": "/",
                "stream": "/radio.mp3",
                "status": "/status",
                "info": "/info",
                "health": "/health"
            },
            "irc_bot_example": {
                "command": "!radio",
                "response": "Ascolta la radio: https://pipparadio.onrender.com/radio.mp3"
            }
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))
    
    def handle_info(self):
        """Informazioni tecniche dettagliate"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        info = {
            "system": {
                "platform": sys.platform,
                "python": sys.version,
                "cwd": os.getcwd(),
                "files_in_app": os.listdir('.'),
                "music_dir_exists": os.path.exists(MUSIC_DIR),
                "music_dir_content": os.listdir(MUSIC_DIR) if os.path.exists(MUSIC_DIR) else []
            },
            "audio": {
                "default_file": DEFAULT_AUDIO,
                "default_file_exists": os.path.exists(DEFAULT_AUDIO),
                "default_file_size": os.path.getsize(DEFAULT_AUDIO) if os.path.exists(DEFAULT_AUDIO) else 0,
                "music_files_count": len(self.get_music_files()),
                "music_files_list": [os.path.basename(f) for f in self.get_music_files()]
            },
            "network": {
                "server_port": SERVER_PORT,
                "server_start_time": datetime.datetime.fromtimestamp(server_start_time).isoformat(),
                "current_time": datetime.datetime.now().isoformat()
            }
        }
        
        self.wfile.write(json.dumps(info, indent=2).encode('utf-8'))
    
    def handle_health(self):
        """Endpoint per health check"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK - Radio Server 24/7\n")
    
    def handle_music_list(self):
        """Lista file musicali disponibili"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        music_files = self.get_music_files()
        music_list = []
        
        for filepath in music_files:
            try:
                size = os.path.getsize(filepath)
                music_list.append({
                    "filename": os.path.basename(filepath),
                    "size_bytes": size,
                    "size_mb": size / (1024 * 1024),
                    "path": filepath
                })
            except:
                pass
        
        result = {
            "count": len(music_list),
            "total_size_mb": sum(item["size_mb"] for item in music_list),
            "files": music_list
        }
        
        self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
    
    def get_music_files(self):
        """Restituisce lista file MP3 nella cartella music"""
        if not os.path.exists(MUSIC_DIR):
            return []
        
        import glob
        mp3_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
        return [f for f in mp3_files if os.path.isfile(f) and os.path.getsize(f) > 1024]

# ============================================================================
# 5. AVVIO SERVER HTTP
# ============================================================================

SERVER_PORT = 10000
server_start_time = time.time()

def run_http_server():
    """Avvia il server HTTP principale"""
    print(f"\n🌐 AVVIO SERVER HTTP su porta {SERVER_PORT}")
    print(f"   • Local:    http://localhost:{SERVER_PORT}/")
    print(f"   • Stream:   http://localhost:{SERVER_PORT}/radio.mp3")
    print(f"   • Status:   http://localhost:{SERVER_PORT}/status")
    
    try:
        with socketserver.TCPServer(("", SERVER_PORT), RadioHTTPHandler) as httpd:
            print(f"\n✅ SERVER ATTIVO!")
            print("=" * 60)
            print("📻 LA TUA RADIO È PRONTA PER IRC!")
            print("=" * 60)
            print(f"\n🔗 PER IL TUO BOT IRC:")
            print(f"   URL stream: https://pipparadio.onrender.com/radio.mp3")
            print(f"   Status API: https://pipparadio.onrender.com/status")
            print(f"\n🎵 Per aggiungere musica:")
            print(f"   1. Carica file MP3 nella cartella /music")
            print(f"   2. La radio li rileverà automaticamente")
            print(f"\n🔄 Server in ascolto... (Ctrl+C per fermare)")
            
            httpd.serve_forever()
            
    except Exception as e:
        print(f"\n❌ ERRORE SERVER: {type(e).__name__}: {e}")
        print("Riavvio in 10 secondi...")
        time.sleep(10)
        run_http_server()  # Riavvio automatico

# ============================================================================
# 6. AVVIO APPLICAZIONE
# ============================================================================

if __name__ == "__main__":
    try:
        # Avvia server in thread separato
        server_thread = threading.Thread(target=run_http_server, daemon=True)
        server_thread.start()
        
        # Mantieni il processo attivo
        print(f"\n⏳ Mantengo processo attivo...")
        while True:
            # Log ogni ora di attività
            uptime = time.time() - server_start_time
            if uptime % 3600 < 5:  # Ogni ora circa
                hours = int(uptime // 3600)
                print(f"🕐 Uptime: {hours} ore ({uptime:.0f} secondi)")
            
            time.sleep(60)  # Controlla ogni minuto
            
    except KeyboardInterrupt:
        print(f"\n🛑 Arresto richiesto dall'utente")
        print(f"⏱️  Uptime totale: {time.time() - server_start_time:.0f} secondi")
        sys.exit(0)
