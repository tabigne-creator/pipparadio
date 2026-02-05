#!/usr/bin/env python3
"""
Streamer audio continuo per Icecast
Stream infinito di silenzio o audio loop
"""

import subprocess
import time
import os
import signal
import sys
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Streamer")

class AudioStreamer:
    def __init__(self):
        self.process = None
        self.running = False
        
        # Configurazione
        self.icecast_host = "localhost"
        self.icecast_port = "8000"  # Usa 8000 invece di 80 per evitare conflitti
        self.mount_point = "/radio.mp3"
        self.password = "hackme"
        self.source_name = "radio-irc"
        
        # File audio
        self.audio_file = "static/silence.mp3"
        
        # Contatore di riavvii
        self.restart_count = 0
        self.max_restarts = 10
        
    def check_audio_file(self):
        """Verifica che il file audio esista"""
        if not os.path.exists(self.audio_file):
            logger.error(f"File audio non trovato: {self.audio_file}")
            logger.info("Creazione file di silenzio temporaneo...")
            
            # Crea directory se non esiste
            os.makedirs("static", exist_ok=True)
            
            # Crea 10 minuti di silenzio come fallback
            try:
                cmd = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', 'anullsrc=r=44100:cl=stereo',
                    '-t', '600',  # 10 minuti
                    '-q:a', '9',
                    '-acodec', 'libmp3lame',
                    self.audio_file
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Creato file: {self.audio_file}")
                return True
            except Exception as e:
                logger.error(f"Impossibile creare file audio: {e}")
                return False
        return True
    
    def build_ffmpeg_command(self):
        """Costruisci il comando FFmpeg"""
        stream_url = f"icecast://source:{self.password}@{self.icecast_host}:{self.icecast_port}{self.mount_point}"
        
        cmd = [
            'ffmpeg',
            '-re',  # Leggi alla velocità reale
            '-stream_loop', '-1',  # Loop infinito
            '-i', self.audio_file,
            '-c:a', 'libmp3lame',
            '-b:a', '128k',
            '-content_type', 'audio/mpeg',
            '-f', 'mp3',
            stream_url
        ]
        
        # Aggiungi metadati
        metadata = [
            '-metadata', f'title=Radio IRC 24/7',
            '-metadata', f'artist=Radio Stream',
            '-metadata', f'genre=Various',
            '-metadata', f'description=Continuous radio stream for IRC'
        ]
        
        return cmd + metadata
    
    def start_stream(self):
        """Avvia lo streaming"""
        if not self.check_audio_file():
            logger.error("Impossibile procedere senza file audio")
            return False
        
        cmd = self.build_ffmpeg_command()
        logger.info(f"Avvio streaming: {' '.join(cmd[:10])}...")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            self.running = True
            logger.info(f"FFmpeg avviato con PID: {self.process.pid}")
            
            # Monitora output in background
            self.monitor_output()
            
            return True
            
        except Exception as e:
            logger.error(f"Errore avvio FFmpeg: {e}")
            return False
    
    def monitor_output(self):
        """Leggi output di FFmpeg in background"""
        import threading
        
        def read_output(stream, stream_name):
            for line in iter(stream.readline, ''):
                if line.strip():
                    # Filtra messaggi utili
                    if "time=" in line or "bitrate=" in line:
                        logger.debug(f"FFmpeg {stream_name}: {line.strip()}")
        
        # Thread per stderr
        stderr_thread = threading.Thread(
            target=read_output,
            args=(self.process.stderr, "stderr"),
            daemon=True
        )
        stderr_thread.start()
    
    def stop_stream(self):
        """Ferma lo streaming"""
        if self.process and self.running:
            logger.info("Arresto streaming...")
            self.running = False
            
            # Invia SIGTERM
            self.process.terminate()
            
            # Attendi fino a 5 secondi
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg non risponde, invio SIGKILL")
                self.process.kill()
            
            logger.info("Streaming arrestato")
    
    def restart_stream(self):
        """Riavvia lo streaming"""
        self.restart_count += 1
        
        if self.restart_count > self.max_restarts:
            logger.error(f"Troppi riavvii ({self.restart_count}), fermo definitivo")
            return False
        
        logger.info(f"Riavvio streaming ({self.restart_count}/{self.max_restarts})")
        self.stop_stream()
        time.sleep(2)  # Attesa tra riavvii
        return self.start_stream()
    
    def run(self):
        """Loop principale"""
        logger.info("=" * 50)
        logger.info("🎵 AVVIO STREAMER AUDIO")
        logger.info("=" * 50)
        
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Attendi che Icecast sia pronto
        logger.info("Attesa Icecast...")
        time.sleep(15)
        
        if not self.start_stream():
            logger.error("Impossibile avviare lo streaming")
            return
        
        # Loop principale
        while self.running:
            try:
                # Controlla se il processo è ancora attivo
                if self.process and self.process.poll() is not None:
                    logger.warning(f"FFmpeg terminato con codice: {self.process.returncode}")
                    
                    if not self.restart_stream():
                        break
                
                # Attesa breve
                time.sleep(5)
                
                # Log heartbeat ogni 30 secondi
                if int(time.time()) % 30 == 0:
                    logger.info("🎶 Streaming attivo...")
                
            except KeyboardInterrupt:
                logger.info("Interruzione da tastiera")
                break
            except Exception as e:
                logger.error(f"Errore nel loop: {e}")
                time.sleep(10)
        
        self.cleanup()
    
    def signal_handler(self, signum, frame):
        """Gestisce segnali di sistema"""
        logger.info(f"Ricevuto segnale {signum}, arresto...")
        self.running = False
        self.stop_stream()
    
    def cleanup(self):
        """Pulizia prima di uscire"""
        logger.info("Pulizia risorse...")
        self.stop_stream()
        logger.info("Streamer terminato")

def main():
    """Funzione principale"""
    print("\n" + "="*60)
    print("🎧 RADIO IRC - STREAMER AUDIO")
    print("="*60)
    
    print("\n📋 CONFIGURAZIONE:")
    print(f"   • Host: localhost:8000")
    print(f"   • Mount: /radio.mp3")
    print(f"   • Bitrate: 128k MP3")
    print(f"   • Loop: infinito")
    
    print("\n🚀 Avvio in 5 secondi...")
    time.sleep(5)
    
    streamer = AudioStreamer()
    streamer.run()

if __name__ == "__main__":
    main()
