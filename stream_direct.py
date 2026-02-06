#!/usr/bin/env python3
"""
Streaming audio diretto via Flask (senza Icecast)
"""

from flask import Flask, Response
import time

app = Flask(__name__)

# Genera stream audio semplice
def generate_audio():
    # Header MP3 minimale (silenzio)
    mp3_header = bytes([
        0xFF, 0xFB, 0x90, 0x64, 0x00, 0x0F, 0xF0, 0x00,
        0x00, 0x69, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00,
        0x0D, 0x20, 0x00, 0x00, 0x01, 0x00, 0x00, 0x01,
        0xA4, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x34,
        0x80, 0x00, 0x00, 0x04
    ])
    
    # Loop infinito di silenzio
    while True:
        yield mp3_header
        time.sleep(0.1)  # 10 FPS

@app.route('/stream.mp3')
def audio_stream():
    return Response(
        generate_audio(),
        mimetype='audio/mpeg',
        headers={
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
