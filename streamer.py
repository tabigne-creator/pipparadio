import subprocess
import time
import os
import signal
import sys

# Gestisce l'arresto pulito
def signal_handler(sig, frame):
    print("\nArresto ricevuto. Uscita...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

print("=== RADIO STREAMER AVVIATO ===")
print(f"Directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

# 1. Crea file di silenzio se non esiste (10 secondi, loop infinito)
SILENCE_FILE = "/app/silence.mp3"
if not os.path.exists(SILENCE_FILE):
    print(f"Creazione {SILENCE_FILE}...")
    cmd_create = [
        'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1:duration=10',
        '-acodec', 'libmp3lame', '-b:a', '128k', SILENCE_FILE
    ]
    subprocess.run(cmd_create, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("File creato.")

# 2. COMANDO FFMPEG PER STREAMING CONTINUO (LOOP INFINITO)
STREAM_CMD = [
    'ffmpeg',
    '-stream_loop', '-1',      # LOOP INFINITO del file sorgente
    '-re',                     # Velocità reale
    '-i', SILENCE_FILE,        # File da streammare
    '-acodec', 'libmp3lame',
    '-b:a', '128k',            # Bitrate 128k
    '-content_type', 'audio/mpeg',
    '-f', 'mp3',
    'icecast://source:hackme@localhost:80/radio.mp3'
]

print("Comando FFmpeg:", ' '.join(STREAM_CMD))
print("=== INIZIO TRASMISSIONE 24/7 ===")
print("Premi Ctrl+C nel terminale per fermare (se in locale).")

# 3. Loop INFINITO: se FFmpeg si ferma, lo riavvia
while True:
    try:
        print(f"[{time.ctime()}] Avvio FFmpeg...")
        # Esegue FFmpeg e aspetta che finisca (non dovrebbe mai finire se non per errore)
        process = subprocess.Popen(STREAM_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()  # Aspetta che il processo termini
        
        # Se arriviamo qui, FFmpeg si è fermato
        print(f"[{time.ctime()}] FFmpeg si è fermato.")
        print(f"Codice uscita: {process.returncode}")
        if stderr:
            print("Ultimi errori FFmpeg:", stderr[-500:] if len(stderr) > 500 else stderr)
        
        # Aspetta 5 secondi prima di riprovare
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nInterrotto manualmente.")
        break
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        time.sleep(10)

print("=== STREAMER TERMINATO ===")
