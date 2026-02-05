import subprocess
import time
import os

print("=== STREAMER IN ATTESA ===")
print("In attesa che Icecast sia pronto...")

# Attendi 30 secondi per permettere a Icecast/server web di stabilizzarsi
time.sleep(30)

print("Ora provo a connettermi a Icecast...")

# COMANDO FFMPEG SEMPLICE - SOLO UN TENTATIVO PER DEBUG
stream_cmd = [
    'ffmpeg',
    '-re',
    '-i', '/app/silence.mp3',
    '-acodec', 'libmp3lame', '-b:a', '128k',
    '-f', 'mp3',
    'icecast://source:hackme@localhost:80/radio.mp3'
]

print("Eseguo:", ' '.join(stream_cmd))
result = subprocess.run(stream_cmd, capture_output=True, text=True)
print("FFmpeg output:", result.stdout[:500])
print("FFmpeg errors:", result.stderr[:500])
print(f"Return code: {result.returncode}")

print("=== FINE TEST ===")
time.sleep(3600)  # Tieni il container attivo
