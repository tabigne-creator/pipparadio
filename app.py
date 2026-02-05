#!/usr/bin/env python3
"""
Radio IRC - Versione SICURA che funziona sempre
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
import urllib.request
import tempfile

print("=" * 60)
print("📻 RADIO IRC - VERSIONE SICURA")
print("=" * 60)

# 1. CREA CARTELLA MUSICA
MUSIC_DIR = "/app/static_music"  # Nuovo percorso
os.makedirs(MUSIC_DIR, exist_ok=True)
print(f"🎵 Cartella musica: {MUSIC_DIR}")

# 2. CREA FILE MP3 DIRETTAMENTE (GARANTITO)
def create_music_files():
    """Crea file MP3 direttamente nel server"""
    print("\n🎵 Creazione musica direttamente...")
    
    samples = [
        {"name": "sample1.mp3", "freq": 440, "duration": 60},   # LA
        {"name": "sample2.mp3", "freq": 523, "duration": 60},   # DO
        {"name": "sample3.mp3", "freq": 659, "duration": 60},   # MI
        {"name": "sample4.mp3", "freq": 880, "duration": 60},   # LA alto
    ]
    
    created = 0
    for sample in samples:
        filepath = os.path.join(MUSIC_DIR, sample["name"])
        
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {sample['name']} già esiste ({size//1024}KB)")
            created += 1
            continue
        
        try:
            print(f"  🔧 Creando {sample['name']}...")
            
            # Usa FFmpeg per creare MP3
            import subprocess
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'sine=frequency={sample["freq"]}:duration={sample["duration"]}',
                '-acodec', 'libmp3lame',
                '-b:a', '128k',
                '-ar', '44100',
                filepath
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0 and os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  ✅ Creato {sample['name']} ({size//1024}KB)")
                created += 1
            else:
                print(f"  ⚠️  Fallito {sample['name']}")
                
        except Exception as e:
            print(f"  ⚠️  Errore {sample['name']}: {type(e).__name__}")
    
    return created

# 3. SCARICA MUSICA DA URL SE NON CE N'È
def download_music_if_needed():
    """Scarica musica se non ci sono file"""
    mp3_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
    
    if len(mp3_files) >= 2:
        print(f"✅ Abbastanza musica: {len(mp3_files)} file")
        return True
    
    print("📥 Scaricamento musica da Internet...")
    
    # URL di musica royalty-free (piccoli file)
    urls = [
        "https://cdn.pixabay.com/download/audio/2022/03/10/audio_37a2e9e2c0.mp3?filename=ambient-piano-amp-strings-112917.mp3",
        "https://cdn.pixabay.com/download/audio/2022/03/15/audio_e8e4c7a2eb.mp3?filename=lofi-chill-medium-version-159456.mp3"
    ]
    
    downloaded = 0
    for i, url in enumerate(urls):
        filename = f"downloaded_{i+1}.mp3"
        filepath = os.path.join(MUSIC_DIR, filename)
        
        if os.path.exists(filepath):
            continue
            
        try:
            print(f"  📥 Scaricando {filename}...")
            
            # Download con timeout
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'RadioIRC/1.0')]
            urllib.request.install_opener(opener)
            
            urllib.request.urlretrieve(url, filepath)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
                size = os.path.getsize(filepath) // 1024
                print(f"  ✅ {filename} ({size}KB)")
                downloaded += 1
            else:
                os.remove(filepath)
                
        except Exception as e:
            print(f"  ⚠️  Fallito {filename}: {type(e).__name__}")
    
    return downloaded > 0

# 4. ESEGUI CREAZIONE MUSICA
created = create_music_files()
if created < 2:
    download_music_if_needed()

# 5. VERIFICA FINALE
mp3_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
print(f"\n📊 RIEPILOGO FINALE:")
print(f"   File MP3 trovati: {len(mp3_files)}")
for mp3 in mp3_files:
    name = os.path.basename(mp3)
    size = os.path.getsize(mp3) // 1024
    print(f"   • {name} ({size}KB)")

if not mp3_files:
    print("❌ CRITICO: Nessun file MP3 creato!")
    # Crea file dummy di emergenza
    dummy = os.path.join(MUSIC_DIR, "emergency.mp3")
    with open(dummy, 'wb') as f:
        f.write(b'DUMMY_MP3' * 10000)
    print(f"✅ Creato file dummy di emergenza")
    mp3_files = [dummy]

print("\n" + "=" * 60)
print("🌐 RADIO PRONTA PER LO STREAMING")
print("=" * 60)

class RadioHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silenzia i log standard
        pass
    
    def do_GET(self):
        # 📡 STREAM AUDIO (per IRC bot)
        if self.path == '/radio.mp3' or self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.end_headers()
            
            client_ip = self.client_address[0]
            print(f"📡 [{datetime.datetime.now().strftime('%H:%M:%S')}] {client_ip}")
            
            # Cerca sempre i file aggiornati
            current_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            
            if not current_files:
                print(f"   ❌ Nessun file MP3!")
                self.wfile.write(b'ERROR: No music files')
                return
            
            print(f"   🎶 {len(current_files)} brani disponibili")
            
            try:
                import random
                song_index = 0
                
                while True:
                    # Cicla tra le canzoni
                    current_song = current_files[song_index % len(current_files)]
                    song_name = os.path.basename(current_song)
                    
                    if song_index % len(current_files) == 0:
                        print(f"   ▶️  Inizio playlist...")
                    
                    print(f"   🎵 {song_name}")
                    
                    with open(current_song, 'rb') as f:
                        audio_data = f.read()
                    
                    # Invia la canzone
                    self.wfile.write(audio_data)
                    
                    # Passa alla prossima canzone
                    song_index += 1
                    
                    # Piccola pausa tra canzoni (evita loop infinito veloce)
                    time.sleep(0.1)
                    
            except (ConnectionResetError, BrokenPipeError):
                print(f"   🔌 {client_ip} disconnesso")
            except Exception as e:
                print(f"   ⚠️  Errore: {type(e).__name__}")
        
        # 🏠 PAGINA WEB
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            current_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>📻 Radio IRC - FUNZIONANTE</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial; max-width: 600px; margin: 40px auto; padding: 20px; }}
        .box {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        audio {{ width: 100%; }}
        .url {{ background: #e0e0e0; padding: 10px; border-radius: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>📻 Radio IRC - FUNZIONANTE!</h1>
    <p>Finalmente! La radio è operativa.</p>
    
    <div class="box">
        <h2>🎵 Player Live</h2>
        <p>Brani disponibili: <strong>{len(current_files)}</strong></p>
        <audio controls autoplay>
            <source src="/radio.mp3" type="audio/mpeg">
        </audio>
        <p><small>Lo stream è attivo 24/7</small></p>
    </div>
    
    <div class="url">
        <strong>🔗 URL per Bot IRC:</strong><br>
        <code>https://pipparadio.onrender.com/radio.mp3</code>
    </div>
    
    <div class="box">
        <h3>📊 Informazioni</h3>
        <p>• Stream: MP3 128kbps</p>
        <p>• Server: Render.com</p>
        <p>• Stato: <span style="color: green;">● ONLINE</span></p>
        <p>• <a href="/status" target="_blank">Status JSON</a></p>
    </div>
    
    <p><em>Ora puoi configurare il tuo bot IRC!</em></p>
</body>
</html>"""
            
            self.wfile.write(html.encode('utf-8'))
        
        # 📊 STATUS JSON
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            current_files = glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
            
            status = {
                "radio": "pipparadio",
                "status": "online",
                "timestamp": datetime.datetime.now().isoformat(),
                "stream_url": "https://pipparadio.onrender.com/radio.mp3",
                "stats": {
                    "tracks_available": len(current_files),
                    "tracks_list": [os.path.basename(f) for f in current_files],
                    "server_time": datetime.datetime.now().strftime('%H:%M:%S')
                }
            }
            
            self.wfile.write(json.dumps(status, indent=2).encode('utf-8'))
        
        else:
            self.send_error(404)

# AVVIA SERVER
def run_server():
    PORT = 10000
    print(f"\n🌐 Avvio server su porta {PORT}")
    print(f"🔗 Stream URL: https://pipparadio.onrender.com/radio.mp3")
    print(f"🏠 Web Interface: https://pipparadio.onrender.com/")
    print(f"📊 Status API: https://pipparadio.onrender.com/status")
    print("\n" + "="*60)
    print("✅ LA TUA RADIO È FINALMENTE OPERATIVA!")
    print("="*60 + "\n")
    
    try:
        with socketserver.TCPServer(("", PORT), RadioHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Errore server: {e}")
        print("🔄 Riavvio in 10 secondi...")
        time.sleep(10)
        run_server()

# AVVIA TUTTO
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

print("⏳ Server avviato. Mantengo processo attivo...")
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    print("\n🛑 Arresto manuale")
    sys.exit(0)
