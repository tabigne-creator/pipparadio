#!/usr/bin/env python3
"""
Server web per Radio IRC
- Pagina web con player audio
- API status per il bot IRC
- Health check per Render
"""

from flask import Flask, jsonify, render_template_string
import time
import os
import socket

app = Flask(__name__)

# Configurazione
RADIO_NAME = "Radio IRC"
STREAM_URL = "/radio.mp3"  # Reindirizza a Icecast
STATUS_ENDPOINT = "https://pipparadio.onrender.com/status"

# Template HTML semplice
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ radio_name }}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .player {
            text-align: center;
            margin: 30px 0;
        }
        audio {
            width: 100%;
            max-width: 500px;
            margin: 20px auto;
        }
        .info-box {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .links a {
            display: inline-block;
            background: white;
            color: #764ba2;
            padding: 10px 20px;
            margin: 10px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: transform 0.3s;
        }
        .links a:hover {
            transform: translateY(-3px);
        }
        .status {
            text-align: center;
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 {{ radio_name }}</h1>
        
        <div class="player">
            <p>Streaming 24/7 per il canale IRC</p>
            <audio controls autoplay>
                <source src="{{ stream_url }}" type="audio/mpeg">
                Il tuo browser non supporta l'audio.
            </audio>
        </div>
        
        <div class="info-box">
            <h3>📡 Informazioni</h3>
            <p>• Formato: MP3 128kbps</p>
            <p>• Stato: <span id="status">Online</span></p>
            <p>• Server: Render.com</p>
            <p>• Bot IRC attivo su Libera.chat</p>
        </div>
        
        <div class="links" style="text-align: center;">
            <a href="{{ stream_url }}" download>📥 Scarica Stream</a>
            <a href="/status" target="_blank">📊 API Status</a>
            <a href="https://render.com" target="_blank">🚀 Hosting</a>
        </div>
        
        <div class="status">
            <p>Server time: {{ server_time }}</p>
            <p>ID: {{ server_id }}</p>
        </div>
    </div>
    
    <script>
        // Aggiorna lo stato ogni 30 secondi
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = data.status;
                })
                .catch(() => {
                    document.getElementById('status').innerText = 'Checking...';
                });
        }
        
        // Aggiorna all'avvio e ogni 30 secondi
        updateStatus();
        setInterval(updateStatus, 30000);
        
        // Auto-riproduci se l'audio si ferma
        document.addEventListener('DOMContentLoaded', function() {
            const audio = document.querySelector('audio');
            audio.addEventListener('ended', function() {
                this.currentTime = 0;
                this.play();
            });
        });
    </script>
</body>
</html>
'''

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
    # Su Render, Icecast sarà sulla stessa macchina
    return "", 302, {'Location': 'http://localhost:80/radio.mp3'}

@app.route('/status')
def status():
    """API status per il bot IRC"""
    return jsonify({
        "status": "online",
        "radio_name": RADIO_NAME,
        "stream_url": "https://pipparadio.onrender.com/radio.mp3",
        "timestamp": time.time(),
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "server_id": socket.gethostname(),
        "stats": {
            "tracks_available": 1,
            "listeners": 0,
            "bitrate": "128kbps",
            "format": "MP3"
        }
    })

@app.route('/health')
def health():
    """Health check per Render"""
    return "OK", 200

@app.route('/api/nowplaying')
def now_playing():
    """Endpoint per il now playing (sempre silenzio in questo caso)"""
    return jsonify({
        "title": "24/7 Radio Stream",
        "artist": "Radio IRC",
        "album": "Continuous Playback",
        "duration": 3600
    })

if __name__ == '__main__':
    print("🚀 Avvio server web Radio IRC...")
    print(f"📻 Nome radio: {RADIO_NAME}")
    print(f"🔗 Stream URL: {STREAM_URL}")
    print("🌐 Server in ascolto su porta 10000")
    
    app.run(host='0.0.0.0', port=10000, debug=False)
