#!/usr/bin/env python3
"""
Radio SEMPLICE - Cerca MP3 in /app/music e streamma
"""

import http.server
import socketserver
import threading
import time
import os
import sys
import json
import datetime
import glob

print("=" * 60)
print("📻 RADIO SEMPLICE - CERCO MP3")
print("=" * 60)

# PERCORSO ASSOLUTO dove sono i tuoi file
MUSIC_DIR = "/app/music"
print(f"🔍 Cerco MP3 in: {MUSIC_DIR}")

# 1. CREA CARTELLA se non esiste
if not os.path.exists(MUSIC_DIR):
    print(f"📁 Creo cartella: {MUSIC_DIR}")
    os.makedirs(MUSIC_DIR, exist_ok=True)

# 2. LISTA TUTTI I FILE
print(f"\n📁 Contenuto di {MUSIC_DIR}:")
try:
    files = os.listdir(MUSIC_DIR)
    if not files:
        print("   ❌ Cartella VUOTA - nessun file MP3")
    else:
        for f in files:
            full_path = os.path.join(MUSIC_DIR, f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                print(f"   📄 {f} - {size:,} bytes")
except Exception as e:
    print(f"   ⚠️ Errore: {e}")

# 3. CERCA SOLO MP3
mp3_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
mp3_files += glob.glob(os.path.join(MUSIC_DIR, "*.MP3"))  # anche maiuscole

print(f"\n🎵 File .mp3/.MP3 trovati: {len(mp3_files)}")
if mp3_files:
    for mp3 in mp3_files[:10]:  # Mostra primi 10
        name = os.path.basename(mp3)
        size = os.path.getsize(mp3) // 1024  # KB
        print(f"   ✅ {name} ({size}KB)")
else:
    print("   ❌ Nessun file MP3 trovato!")

# 4. CREA FILE DI SILENZIO se non ci sono MP3
SILENT_FILE = "/app/silence.mp3"
if not mp3_files and not os.path.exists(SILENT_FILE):
    print("\n🔇 Creo file silenzio di backup...")
    try:
        # Crea 10 minuti di silenzio
        import subprocess
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=mono',
            '-t', '600',  # 10 minuti
            '-acodec', 'libmp3lame', '-b:a', '128k',
            SILENT_FILE
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        print(f"✅ Creato {SILENT_FILE}")
    except:
        print("⚠️  FFmpeg fallito")

print("\n" + "=" * 60)
print("🌐 SERVER RADIO PRONTO")
print("=" * 60)

class RadioHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 📡 STREAM AUDIO
        if self.path == '/radio.mp3' or self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.end_headers()
            
            print(f"📡 [{datetime.datetime.now().strftime('%H:%M:%S')}] Connessione")
            
            # CERCA SEMPRE I FILE AGGIORNATI
            current_mp3 = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            current_mp3 += glob.glob(os.path.join(MUSIC_DIR, "*.MP3"))
            
            if current_mp3:
                print(f"   🎶 {len(current_mp3)} brani disponibili")
                # Suona i file MP3
                import random
                while True:
                    song = random.choice(current_mp3)
                    print(f"   ▶️  {os.path.basename(song)}")
                    with open(song, 'rb') as f:
                        self.wfile.write(f.read())
            else:
                print(f"   🔇 Streaming silenzio")
                # Fallback a silenzio
                if os.path.exists(SILENT_FILE):
                    with open(SILENT_FILE, 'rb') as f:
                        silence = f.read()
                    while True:
                        self.wfile.write(silence)
                else:
                    # Se non c'è neanche silenzio, invia dati finti
                    while True:
                        self.wfile.write(b'\x00' * 8192)
                        time.sleep(0.1)
        
        # 🏠 PAGINA WEB
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            current_mp3 = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            current_mp3 += glob.glob(os.path.join(MUSIC_DIR, "*.MP3"))
            
            html = f"""<html><body>
                <h1>📻 Radio IRC</h1>
                <p>Brani trovati: {len(current_mp3)}</p>
                <audio controls autoplay>
                    <source src="/radio.mp3" type="audio/mpeg">
                </audio>
                <p><a href="/radio.mp3">Link stream per IRC</a></p>
                <p><a href="/status">Status JSON</a></p>
            </body></html>"""
            self.wfile.write(html.encode())
        
        # 📊 STATUS JSON
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            current_mp3 = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            current_mp3 += glob.glob(os.path.join(MUSIC_DIR, "*.MP3"))
            
            status = {
                "status": "online",
                "tracks": len(current_mp3),
                "stream": "https://pipparadio.onrender.com/radio.mp3",
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(status, indent=2).encode())
        
        else:
            self.send_error(404)

# AVVIA SERVER
def run():
    port = 10000
    print(f"\n🌐 Server in ascolto su porta {port}")
    print(f"🔗 Stream: https://pipparadio.onrender.com/radio.mp3")
    print(f"🏠 Pagina: https://pipparadio.onrender.com/")
    
    with socketserver.TCPServer(("", port), RadioHandler) as httpd:
        httpd.serve_forever()

# Avvia in thread
threading.Thread(target=run, daemon=True).start()

print("\n✅ Radio attiva! Premi Ctrl+C per fermare")
while True:
    time.sleep(3600)
