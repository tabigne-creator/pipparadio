import subprocess
import time
import os
import sys

print("=== RADIO STREAMER - DEBUG DETTAGLIATO ===")

# 1. TEST BASE: Il sistema funziona?
print("1. Test comandi di base...")
for cmd in [['ffmpeg', '-version'], ['which', 'ffmpeg'], ['curl', '--version']]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        print(f"   {' '.join(cmd)}: OK (code {result.returncode})")
        if cmd[0] == 'ffmpeg' and result.stdout:
            print(f"   FFmpeg trovato: {result.stdout.splitlines()[0]}")
    except Exception as e:
        print(f"   {' '.join(cmd)}: FALLITO - {e}")

# 2. TEST ICECAST: Risponde?
print("\n2. Test connessione Icecast...")
icecast_tests = [
    ['curl', '-s', '-o', '/dev/null', '-w', 'HTTP: %{http_code}', 'http://localhost:80/'],
    ['curl', '-s', 'http://localhost:80/']
]
for test in icecast_tests:
    try:
        result = subprocess.run(test, capture_output=True, text=True, timeout=10)
        print(f"   {' '.join(test[:3])}: {result.stdout.strip()}")
        if result.stderr:
            print(f"   Stderr: {result.stderr[:100]}")
    except Exception as e:
        print(f"   {' '.join(test[:3])}: FALLITO - {e}")

# 3. CREA FILE AUDIO SICURO (formato corretto)
print("\n3. Creazione file audio di test...")
TEST_FILE = "/app/test_audio.mp3"
# Crea 30 secondi di tono a 440Hz (LA) - formato MP3 garantito
create_cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi',
    '-i', 'sine=frequency=440:duration=30',
    '-acodec', 'libmp3lame',
    '-b:a', '128k',
    '-ar', '44100',
    '-ac', '2',
    TEST_FILE
]
print(f"   Comando: {' '.join(create_cmd)}")
try:
    result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
    print(f"   Creazione file: {'SUCCESSO' if result.returncode == 0 else 'FALLITO'}")
    if result.returncode != 0:
        print(f"   Errori FFmpeg: {result.stderr[:300]}")
    if os.path.exists(TEST_FILE):
        print(f"   File creato: {TEST_FILE}, Dimensione: {os.path.getsize(TEST_FILE)} bytes")
except Exception as e:
    print(f"   Creazione file FALLITA: {e}")

# 4. TEST STREAMING SEMPLICE (prima senza Icecast, poi con)
print("\n4. Test streaming step-by-step...")

# Test A: FFmpeg può leggere il file?
print("   A) Test lettura file locale...")
test_read_cmd = ['ffmpeg', '-i', TEST_FILE, '-f', 'null', '-']
try:
    result = subprocess.run(test_read_cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("      ✅ File audio valido e leggibile")
    else:
        print(f"      ❌ FFmpeg non può leggere il file: {result.stderr[:200]}")
except Exception as e:
    print(f"      ❌ Errore test lettura: {e}")

# Test B: Prova a inviare a Icecast (VERSIONE SEMPLICE)
print("   B) Test connessione a Icecast (timeout 15s)...")
# Usa un comando FFmpeg SUPER semplice e standard
stream_cmd_simple = [
    'ffmpeg',
    '-re',                     # Read input at native frame rate
    '-i', TEST_FILE,           # Input file
    '-acodec', 'copy',         # Just copy the stream, no re-encoding
    '-f', 'mp3',               # Force MP3 format
    'icecast://source:hackme@localhost:80/radio.mp3'
]

print(f"   Comando: {' '.join(stream_cmd_simple)}")
print("   --- INIZIO OUTPUT FFMPEG LIVE (timeout 15s) ---")
try:
    # Esegui con timeout per vedere l'output immediato
    process = subprocess.Popen(
        stream_cmd_simple,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Unisci stdout e stderr
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Leggi output in tempo reale per 15 secondi
    for i in range(15):
        line = process.stdout.readline()
        if line:
            print(f"      [{i+1}s] {line.strip()}")
        time.sleep(1)
        
        # Controlla se il processo è già morto
        if process.poll() is not None:
            print(f"      FFmpeg terminato con codice: {process.poll()}")
            break
    
    # Termina il processo dopo 15 secondi
    process.terminate()
    try:
        process.wait(timeout=5)
    except:
        process.kill()
        
except Exception as e:
    print(f"      ❌ Errore esecuzione FFmpeg: {e}")

print("   --- FINE TEST ---")

# 5. INFORMAZIONI FINALI DI DEBUG
print("\n5. Informazioni di sistema:")
print(f"   Directory corrente: {os.getcwd()}")
print(f"   Contenuto /app: {os.listdir('/app')}")
print(f"   User ID: {os.getuid()}, Group ID: {os.getgid()}")
print(f"   Python path: {sys.executable}")

print("\n=== DEBUG COMPLETATO ===")
print("Il container rimarrà attivo per 5 minuti per controllare i log...")
time.sleep(300)
print("=== FINE ===")
