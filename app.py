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
# 1. CONFIGURAZIONE INIZIALE - IGNORA IL FILE 'music' PROBLEMATICO
# ============================================================================

# Directory base dell'applicazione
BASE_DIR = "/app"
os.chdir(BASE_DIR)

print(f"📍 Directory: {os.getcwd()}")
print(f"📁 Contenuto iniziale: {os.listdir('.')}")

# 👉 USIAMO UN NOME DIVERSO per evitare conflitti con il file 'music' esistente
MUSIC_STORAGE = "/app/radio_tracks"  # NOME DIVERSO!
SILENT_TRACK = "/app/silent_stream.mp3"

# Se esiste il file problematico 'music', lo ignoriamo
if os.path.exists("/app/music") and os.path.isfile("/app/music"):
    print(f"⚠️  Ignoro file 'music' esistente")
    print(f"⚠️  Userò invece: {MUSIC_STORAGE}")

# Crea la NOSTRA cartella musicale (nome diverso)
try:
    os.makedirs(MUSIC_STORAGE, exist_ok=True)
    print(f"✅ Cartella musica creata: {MUSIC_STORAGE}")
except:
    print(f"✅ Cartella musica già esistente: {MUSIC_STORAGE}")

# ============================================================================
# 2. PREPARAZIONE CONTENUTO AUDIO (SILENZIO + MUSICA DI ESEMPIO)
# ============================================================================

def create_silent_track():
    """Crea un file MP3 di silenzio per lo streaming"""
    print("\n🎵 Preparazione audio base...")
    
    if os.path.exists(SILENT_TRACK):
        size = os.path.getsize(SILENT_TRACK)
        print(f"✅ Traccia silenzio esistente: {size:,} bytes")
        return True
    
    # Crea 30 minuti di silenzio (Render Free ha limiti)
    try:
        import subprocess
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=mono',
            '-t', '1800',  # 30 minuti
            '-acodec', 'libmp3lame',
            '-b:a', '128k',
            SILENT_TRACK
        ]
        
        print(f"   Comando FFmpeg: {' '.join(cmd[:6])}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(SILENT_TRACK):
            size = os.path.getsize(SILENT_TRACK)
            print(f"✅ Traccia silenzio creata: {size:,} bytes")
            
            # Duplica per avere più contenuto
            if size < 5 * 1024 * 1024:  # Se meno di 5MB
                with open(SILENT_TRACK, 'ab') as f:
                    original = open(SILENT_TRACK, 'rb').read()
                    for _ in range(3):  # Triplica
                        f.write(original)
                
                new_size = os.path.getsize(SILENT_TRACK)
                print(f"✅ Traccia estesa: {new_size:,} bytes")
            return True
            
    except Exception as e:
        print(f"⚠️  Nota FFmpeg: {type(e).__name__}")
    
    # Fallback: crea file vuoto
    try:
        with open(SILENT_TRACK, 'wb') as f:
            f.write(b'FAKE_MP3_HEADER' * 1000)
        print(f"✅ Traccia fallback creata")
        return True
    except:
        return False

def download_sample_music():
    """Scarica musica di esempio se la cartella è vuota"""
    import glob
    mp3_files = glob.glob(os.path.join(MUSIC_STORAGE, "*.mp3"))
    
    if mp3_files:
        print(f"✅ {len(mp3_files)} file MP3 trovati in {MUSIC_STORAGE}")
        return True
    
    print("🎵 Download musica di esempio...")
    
    # Piccoli file audio royalty-free (effetti sonori)
    samples = [
        {
            "name": "chill_beat.mp3",
            "url": "https://assets.mixkit.co/music/preview/mixkit-chill-hop-01-965.mp3"
        },
        {
            "name": "ambient_pad.mp3",
            "url": "https://assets.mixkit.co/music/preview/mixkit-ambient-pad-01-969.mp3"
        }
    ]
    
    downloaded = 0
    
    for sample in samples:
        filepath = os.path.join(MUSIC_STORAGE, sample["name"])
        
        if os.path.exists(filepath):
            continue
            
        try:
            print(f"  📥 Scaricando {sample['name']}...")
            
            # Metodo semplice per scaricare
            import urllib.request
            import ssl
            
            # Crea contesto SSL che ignora certificati (per semplicità)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                sample["url"],
                headers={'User-Agent': 'RadioIRC/1.0'}
            )
            
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
                downloaded += 1
                size_kb = os.path.getsize(filepath) // 1024
                print(f"  ✅ {sample['name']} ({size_kb}KB)")
            else:
                try:
                    os.remove(filepath)
                except:
                    pass
                    
        except Exception as e:
            print(f"  ⚠️  Salto {sample['name']}: {e}")
            continue
    
    if downloaded > 0:
        print(f"✅ {downloaded} brani di esempio scaricati")
        return True
    
    print("⚠️  Nessun brano scaricato. Userò solo silenzio.")
    return False

# Esegue preparazione audio
create_silent_track()
download_sample_music()

# ============================================================================
# 3. HANDLER HTTP PRINCIPALE - STREAM 24/7
# ============================================================================

class RadioHandler(http.server.BaseHTTPRequestHandler):
    """Gestisce tutte le richieste HTTP per la radio"""
    
    # Disabilita logging standard
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        """Gestisce richieste GET"""
        
        # 📡 STREAM AUDIO PRINCIPALE (per IRC bot)
        if self.path == '/radio.mp3' or self.path == '/stream':
            self.stream_audio()
            
        # 🏠 PAGINA PRINCIPALE CON PLAYER
        elif self.path == '/':
            self.show_homepage()
            
        # 📊 STATO PER BOT IRC (JSON)
        elif self.path == '/status':
            self.show_status()
            
        # ❓ HEALTH CHECK
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            
        else:
            self.send_error(404, "Pagina non trovata")
    
    def stream_audio(self):
        """Streamma audio in loop infinito 24/7"""
        client_ip = self.client_address[0]
        print(f"📡 [{datetime.datetime.now().strftime('%H:%M:%S')}] "
              f"Nuova connessione da {client_ip}")
        
        try:
            # Intestazioni per streaming MP3
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            
            bytes_sent = 0
            start_time = time.time()
            chunk_counter = 0
            
            # 🔄 LOOP INFINITO DI STREAMING
            while True:
                # 1. CERCA MUSICA REALE
                import glob
                music_files = glob.glob(os.path.join(MUSIC_STORAGE, "*.mp3"))
                
                if music_files:
                    # Suona musica reale
                    import random
                    current_song = random.choice(music_files)
                    song_name = os.path.basename(current_song)
                    
                    # Log solo la prima volta per ogni canzone
                    if chunk_counter == 0:
                        print(f"   🎶 [{client_ip}] Riproduco: {song_name}")
                    
                    with open(current_song, 'rb') as f:
                        song_data = f.read()
                    
                    # Invia la canzone in loop
                    while True:
                        self.wfile.write(song_data)
                        bytes_sent += len(song_data)
                        chunk_counter += 1
                        
                        # Log ogni 10MB
                        if bytes_sent % (10 * 1024 * 1024) < 1024:
                            elapsed = time.time() - start_time
                            mb_sent = bytes_sent // (1024 * 1024)
                            print(f"   📊 [{client_ip}] {mb_sent}MB "
                                  f"({elapsed:.0f}s) - {song_name}")
                
                # 2. FALLBACK: SILENZIO
                else:
                    # Streamma silenzio
                    if chunk_counter == 0:
                        print(f"   🔇 [{client_ip}] Streaming silenzio")
                    
                    with open(SILENT_TRACK, 'rb') as f:
                        silent_data = f.read()
                    
                    while True:
                        self.wfile.write(silent_data)
                        bytes_sent += len(silent_data)
                        chunk_counter += 1
                        
                        # Log ogni minuto
                        if int(time.time() - start_time) % 60 == 0:
                            mb_sent = bytes_sent // (1024 * 1024)
                            elapsed_min = int((time.time() - start_time) // 60)
                            print(f"   🔊 [{client_ip}] Silenzio: "
                                  f"{mb_sent}MB in {elapsed_min}min")
                        
                        time.sleep(0.01)
                        
        except (ConnectionResetError, BrokenPipeError) as e:
            # Client disconnesso - normale
            elapsed = time.time() - start_time
            mb_sent = bytes_sent // (1024 * 1024)
            print(f"🔌 [{datetime.datetime.now().strftime('%H:%M:%S')}] "
                  f"{client_ip} disconnesso dopo {elapsed:.0f}s "
                  f"({mb_sent}MB inviati)")
        except Exception as e:
            print(f"⚠️  [{datetime.datetime.now().strftime('%H:%M:%S')}] "
                  f"Errore con {client_ip}: {type(e).__name__}")
    
    def show_homepage(self):
        """Mostra pagina HTML con player"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        import glob
        music_files = glob.glob(os.path.join(MUSIC_STORAGE, "*.mp3"))
        music_count = len(music_files)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>📻 Radio IRC - Stream 24/7</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }}
        .box {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        audio {{ width: 100%; }}
        .url {{ background: #e0e0e0; padding: 10px; border-radius: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>📻 Radio IRC Stream</h1>
    <p>Il tuo server radio è attivo e funzionante!</p>
    
    <div class="box">
        <h2>🎵 Player Live</h2>
        <p>{music_count} brani disponibili</p>
        <audio controls autoplay>
            <source src="/radio.mp3" type="audio/mpeg">
        </audio>
    </div>
    
    <div class="url">
        <strong>🔗 URL per Bot IRC:</strong><br>
        https://pipparadio.onrender.com/radio.mp3
    </div>
    
    <div class="box">
        <h3>📊 Informazioni</h3>
        <p>• Stream: MP3 128kbps 44.1kHz</p>
        <p>• Stato: <span id="status">Online</span></p>
        <p>• <a href="/status" target="_blank">Status JSON</a></p>
    </div>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def show_status(self):
        """Restituisce stato in JSON per bot IRC"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        import glob
        music_files = glob.glob(os.path.join(MUSIC_STORAGE, "*.mp3"))
        
        status = {
            "radio": "pipparadio",
            "status": "online",
            "timestamp": datetime.datetime.now().isoformat(),
            "stream_url": "https://pipparadio.onrender.com/radio.mp3",
            "stats": {
                "tracks_available": len(music_files),
                "uptime_seconds": int(time.time() - server_start_time),
                "server_time": datetime.datetime.now().strftime('%H:%M:%S')
            }
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))

# ============================================================================
# 4. AVVIO SERVER HTTP
# ============================================================================

SERVER_PORT = 10000
server_start_time = time.time()

def start_server():
    """Avvia il server HTTP"""
    print(f"\n🌐 Avvio server su porta {SERVER_PORT}")
    print(f"   • Local: http://localhost:{SERVER_PORT}/")
    print(f"   • Stream: http://localhost:{SERVER_PORT}/radio.mp3")
    print(f"   • Status: http://localhost:{SERVER_PORT}/status")
    print(f"\n🔗 PER IL BOT IRC:")
    print(f"   URL: https://pipparadio.onrender.com/radio.mp3")
    print(f"\n" + "=" * 60)
    print("📻 LA TUA RADIO È PRONTA!")
    print("=" * 60 + "\n")
    
    try:
        with socketserver.TCPServer(("", SERVER_PORT), RadioHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Errore server: {e}")
        print("🔄 Riavvio in 10 secondi...")
        time.sleep(10)
        start_server()

# ============================================================================
# 5. AVVIO APPLICAZIONE
# ============================================================================

if __name__ == "__main__":
    # Avvia server in thread separato
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print(f"\n⏳ Server avviato. Uptime:")
    
    # Mantieni processo attivo
    try:
        while True:
            uptime = time.time() - server_start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            # Log ogni 5 minuti
            if minutes % 5 == 0 and uptime % 300 < 10:
                print(f"   🕐 Uptime: {hours}h {minutes}m ({int(uptime)}s)")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Arresto manuale")
        print(f"⏱️  Uptime totale: {time.time() - server_start_time:.0f} secondi")
        sys.exit(0)
