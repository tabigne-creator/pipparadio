import subprocess
import time
import os

print("=== AVVIO STREAMER ===")

# 1. Crea un file audio di silenzio se non esiste
SILENCE_FILE = "/music/silence.mp3"
if not os.path.exists(SILENCE_FILE):
    print("Creazione file di silenzio...")
    # Crea 1 ora di silenzio (frequenza 1Hz, impercettibile)
    cmd_create = [
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1:duration=3600',
        '-acodec', 'libmp3lame', '-b:a', '128k', SILENCE_FILE
    ]
    subprocess.run(cmd_create, check=False)

# 2. Comando FFmpeg per streammare in loop
stream_cmd = [
    'ffmpeg',
    '-stream_loop', '-1',  # Loop infinito
    '-re',                 # Leggi alla velocità reale
    '-i', SILENCE_FILE,    # File sorgente
    '-acodec', 'libmp3lame', '-b:a', '128k',  # Codifica MP3
    '-content_type', 'audio/mpeg',
    '-f', 'mp3',
    'icecast://source:hackme@localhost:80/radio.mp3'  # IMPORTANTE: porta 80
]

print("Inizio streaming loop...")
print(f"Streaming su: icecast://localhost:80/radio.mp3")

# 3. Esegui in loop (se ffmpeg si ferma, riavvia)
while True:
    try:
        print("Avvio FFmpeg...")
        result = subprocess.run(stream_cmd, capture_output=True, text=True)
        print(f"FFmpeg uscito con codice: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout[:200]}...")
        if result.stderr:
            print(f"Errori: {result.stderr[:200]}...")
    except Exception as e:
        print(f"Errore esecuzione FFmpeg: {e}")
    
    print("Riavvio in 5 secondi...")
    time.sleep(5)

