import os
import subprocess
from glob import glob

# Crea un file audio di silenzio se non ci sono MP3
if not os.path.exists('/music/silence.mp3'):
    subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1', '-t', '3600', '/music/silence.mp3'])

while True:
    # Streamma il file di silenzio in loop
    cmd = [
        'ffmpeg', '-re', '-i', '/music/silence.mp3',
        '-acodec', 'libmp3lame', '-b:a', '128k',
        '-content_type', 'audio/mpeg',
        '-f', 'mp3', 'icecast://source:hackme@localhost:8000/radio.mp3'
    ]
    subprocess.run(cmd)
