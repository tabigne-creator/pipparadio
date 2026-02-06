#!/usr/bin/env python3
"""
Server web per Radio IRC con streaming diretto
"""

from flask import Flask, jsonify, render_template_string, Response
import time
import os
import socket

app = Flask(__name__)

# Configurazione
RADIO_NAME = "Radio IRC"
SITE_URL = "https://pipparadio-1.onrender.com"

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
                <source src="/radio.mp3" type="audio/mpeg">
                Il tuo browser non supporta l'elemento audio.
            </audio>
            <p style="margin-top: 15px; color: #a0a0c0;">
                Formato: MP3 128kbps | Stream continuo
            </p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📡 Informazioni Tecniche</h3>
                <p>• Server: Flask Direct Stream</p>
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
                <p>• Comandi
