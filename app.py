#!/usr/bin/env python3
"""
Server web per Radio IRC
- Pagina web con player audio
- API status per il bot IRC
- Health check per Render
"""

from flask import Flask, jsonify, render_template_string, redirect
import time
import os
import socket
import subprocess

app = Flask(__name__)

# Configurazione
RADIO_NAME = "Radio IRC"
STREAM_URL = "/radio.mp3"  # Reindirizza a Icecast
ICE_HOST = "localhost"
ICE_PORT = "8000"

# Template HTML
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ radio_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: inline-block;
        }
        .subtitle {
            color: #a0a0c0;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        .player-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        audio {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            border-radius: 10px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .info-card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }
        .info-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .status-bar {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.9rem;
            color: #a0a0c0;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .online-dot {
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        @media (max-width: 768px) {
            .container { padding: 20px; }
            h1 { font-size: 2.2rem; }
            .btn-group { flex-direction: column; }
            .btn { width: 100%; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎵 {{ radio_name }}</h1>
            <p class="subtitle">Streaming audio 24/7 per la comunità IRC</p>
        </header>
        
        <div class="player-container">
            <h2>🎧 Ascolta in diretta</h2>
            <audio controls autoplay loop>
                <source src="{{ stream_url }}" type="audio/mpeg">
                Il tuo browser non supporta l'elemento audio.
            </audio>
            <p style="margin-top: 15px; color: #a0a0c0;">
                Formato: MP3 128kbps | Stream continuo
            </p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📡 Informazioni Tecniche</h3>
                <p>• Server: Icecast 2</p>
                <p>• Bitrate: 128 kbps</p>
                <p>• Formato: MP3</p>
                <p>• Canali: Stereo</p>
            </div>
            <div class="info-card">
                <h3>🚀 Hosting</h3>
                <p>• Piattaforma: Render.com</p>
                <p>• Uptime: 24/7</p>
                <p>• Regione: Automatica</p>
                <p>• Piano: Free Tier</p>
            </div>
            <div class="info-card">
                <h3>🤖 Integrazione IRC</h3>
                <p>• Bot: RadioBot</p>
                <p>• Server: Libera.chat</p>
                <p>• Comandi: !radio, !status</p>
                <p>• Canale: #radio-irc</p>
            </div>
        </div>
        
        <div class="btn-group">
            <a href="{{ stream_url }}" class="btn" download>
                <span>📥</span> Scarica Stream
            </a>
            <a href="/status" class="btn btn-secondary" target="_blank">
                <span>📊</span> API Status
            </a>
            <a href="/test" class="btn btn-secondary">
                <span>🔧</span> System Test
            </a>
            <a href="https://github.com" class="btn btn-secondary" target="_blank">
                <span>🐙</span> GitHub
            </a>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="online-dot"></span>
                <span>Stato: <strong id="statusText">Online</strong></span>
            </div>
            <div class="status-item">
                <span>🆔</span>
                <span>Server: {{ server_id }}</span>
            </div>
            <div class="status-item">
                <span>🕐</span>
                <span>Ora: {{ server_time }}</span>
            </div>
            <div class="status-item">
                <span>👂</span>
                <span>Listeners: <span id="listenerCount">0</span></span>
            </div>
        </div>
    </div>
    
    <script>
        async function updateStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                document.getElementById('statusText').textContent = 
                    data.status.charAt(0).toUpperCase() + data.status.slice(1);
                document.getElementById('listenerCount').textContent = 
                    data.stats.listeners || 0;
                
                // Aggiorna ogni 30 secondi
                setTimeout(updateStatus, 30000);
            } catch (error) {
                console.log('Status update failed:', error);
                document.getElementById('statusText').textContent = 'Offline';
                setTimeout(updateStatus, 10000);
            }
        }
        
        // Inizializza
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus();
            
            // Gestione riproduzione automatica
            const audio = document.querySelector('audio');
            audio.addEventListener('error', function() {
                console.log('Audio error, trying alternative source...');
                this.src = '/radio.mp3?t=' + new Date().getTime();
                this.load();
            });
            
            // Aggiorna ora locale ogni minuto
            function updateLocalTime() {
                const now = new Date();
                document.querySelectorAll('.local-time').forEach(el => {
                    el.textContent = now.toLocaleTimeString();
                });
            }
            setInterval(updateLocalTime, 60000);
            updateLocalTime();
        });
    </script>
</body>
</html>'''

@app.route('/')
def home():
    """Pagina principale con player audio"""
    return render_template_string(
        HTML_TEMPLATE,
        radio_name=RADIO_NAME,
        stream_url=STREAM_URL,
        server_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        server_id=socket.gethostname()
    )

@app.route('/radio.mp3')
def radio_stream():
    """Reindirizza allo stream Icecast"""
    return redirect(f"http://{ICE_HOST}:{ICE_PORT}/radio.mp3", code=302)

@app.route('/status')
def status():
    """API status per il bot IRC"""
    try:
        # Prova a verificare se Icecast è attivo
        listeners = 0
        try:
            import urllib.request
            import json
            icecast_stats_url = f"http://{ICE_HOST}:{ICE_PORT}/status-json.xsl"
            with urllib.request.urlopen(icecast_stats_url, timeout=2) as response:
                data = json.load(response)
                if 'icestats' in data and 'source' in data['icestats']:
                    listeners = data['icestats']['source'].get('listeners', 0)
        except:
            pass
        
        return jsonify({
            "status": "online",
            "radio_name": RADIO_NAME,
            "stream_url": f"http://{ICE_HOST}:{ICE_PORT}/radio.mp3",
            "timestamp": time.time(),
            "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_id": socket.gethostname(),
            "stats": {
                "tracks_available": 1,
                "listeners": listeners,
                "bitrate": "128kbps",
                "format": "MP3",
                "icecast_port": ICE_PORT,
                "flask_port": 10000
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health')
def health():
    """Health check per Render"""
    try:
        # Verifica che i servizi siano attivi
        import urllib.request
        # Verifica Flask
        with urllib.request.urlopen(f"http://localhost:10000/", timeout=2) as response:
            if response.getcode() == 200:
                return "OK", 200
    except:
        pass
    return "SERVICE UNAVAILABLE", 503

@app.route('/test')
def test():
    """Pagina di test con info sistema"""
    system_info = {
        "python_version": os.sys.version,
        "hostname": socket.gethostname(),
        "platform": os.sys.platform,
        "working_dir": os.getcwd(),
        "flask_port": 10000,
        "icecast_port": ICE_PORT,
        "timestamp": time.time(),
        "services": {}
    }
    
    # Verifica FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        system_info['services']['ffmpeg'] = {
            "installed": result.returncode == 0,
            "version": result.stdout.split('\n')[0][:50] if result.stdout else "Unknown"
        }
    except:
        system_info['services']['ffmpeg'] = {"installed": False}
    
    # Verifica Icecast
    try:
        import urllib.request
        with urllib.request.urlopen(f"http://{ICE_HOST}:{ICE_PORT}/", timeout=5) as response:
            system_info['services']['icecast'] = {
                "running": True,
                "status_code": response.getcode()
            }
    except:
        system_info['services']['icecast'] = {"running": False}
    
    return jsonify(system_info)

@app.route('/api/nowplaying')
def now_playing():
    """Endpoint per il now playing"""
    return jsonify({
        "title": "24/7 Radio Stream",
        "artist": "Radio IRC",
        "album": "Continuous Playback",
        "duration": 3600,
        "bitrate": 128,
        "samplerate": 44100,
        "channels": 2,
        "format": "MP3"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 RADIO IRC - WEB SERVER")
    print("=" * 60)
    print(f"📻 Radio: {RADIO_NAME}")
    print(f"🔗 Stream: http://{ICE_HOST}:{ICE_PORT}/radio.mp3")
    print(f"🌐 Web UI: http://0.0.0.0:10000")
    print(f"📊 API: http://0.0.0.0:10000/status")
    print(f"❤️  Health: http://0.0.0.0:10000/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=10000, debug=False)
