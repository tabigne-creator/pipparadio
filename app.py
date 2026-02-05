#!/usr/bin/env python3
"""
Bot IRC per Radio pipparadio
"""

import irc.bot
import requests
import time
import threading

class RadioBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        # ⚠️ MODIFICA QUESTI 3 VALORI! ⚠️
        server = "irc.libera.chat"      # Server IRC
        channel = "#tucanale"           # Canale (con #)
        nickname = "RadioBot"           # Nome del bot
        
        irc.bot.SingleServerIRCBot.__init__(self, [(server, 6667)], nickname, channel)
        
        # URL della TUA radio
        self.radio_url = "https://pipparadio.onrender.com/radio.mp3"
        self.status_url = "https://pipparadio.onrender.com/status"
        self.home_url = "https://pipparadio.onrender.com/"
        
        print(f"🤖 RadioBot per {self.radio_url}")
        print(f"📡 Server: {server}")
        print(f"📢 Canale: {channel}")
    
    def on_welcome(self, connection, event):
        """Quando il bot si connette al server"""
        print(f"✅ Connesso a IRC")
        connection.join(self.channel)
        
        # Annuncia la radio
        welcome_msg = f"📻 Radio attiva! Ascolta: {self.radio_url}"
        connection.privmsg(self.channel, welcome_msg)
        
        # Avvia aggiornamento automatico ogni minuto
        self.start_status_updates()
    
    def start_status_updates(self):
        """Aggiorna periodicamente lo stato"""
        def update_loop():
            while True:
                try:
                    response = requests.get(self.status_url, timeout=5)
                    data = response.json()
                    
                    tracks = data["stats"]["tracks_available"]
                    status_msg = f"📊 Radio online | Brani: {tracks} | {self.radio_url}"
                    
                    # Invia ogni 30 minuti
                    self.connection.privmsg(self.channel, status_msg)
                    
                except Exception as e:
                    print(f"⚠️  Errore status: {e}")
                
                time.sleep(1800)  # 30 minuti
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def on_pubmsg(self, connection, event):
        """Risponde ai messaggi nel canale"""
        message = event.arguments[0].lower()
        sender = event.source.split('!')[0]
        
        # COMANDO: !radio
        if message == "!radio" or message.startswith("!radio "):
            reply = f"{sender}: 🎧 Ascolta la radio: {self.radio_url}"
            connection.privmsg(self.channel, reply)
        
        # COMANDO: !status
        elif message == "!status" or message.startswith("!status "):
            try:
                response = requests.get(self.status_url, timeout=5)
                data = response.json()
                
                tracks = data["stats"]["tracks_available"]
                server_time = data["stats"]["server_time"]
                
                status_msg = f"📊 Brani: {tracks} | Server: {server_time} | {self.radio_url}"
                connection.privmsg(self.channel, status_msg)
                
            except:
                connection.privmsg(self.channel, f"{sender}: 📻 Radio online!")
        
        # COMANDO: !help
        elif message == "!help" or message.startswith("!help "):
            help_text = f"{sender}: Comandi: !radio !status !help !info"
            connection.privmsg(self.channel, help_text)
        
        # COMANDO: !info
        elif message == "!info" or message.startswith("!info "):
            info_text = f"{sender}: 📻 pipparadio | Stream 24/7 MP3 128kbps | Host: Render.com"
            connection.privmsg(self.channel, info_text)

def main():
    print("="*50)
    print("🚀 AVVIO RADIO BOT PER IRC")
    print("="*50)
    
    print("\n⚠️  PRIMA DI AVVIARE:")
    print("1. Modifica server/channel/nickname nello script")
    print("2. Installa dipendenze: pip install irc requests")
    print("3. Esegui: python radio_bot.py")
    
    print("\n📋 CONFIGURAZIONE ATTIVALE:")
    print(f"   • Stream URL: https://pipparadio.onrender.com/radio.mp3")
    print(f"   • Status API: https://pipparadio.onrender.com/status")
    print(f"   • Pagina web: https://pipparadio.onrender.com/")
    
    # Chiedi conferma
    input("\nPremi INVIO per avviare il bot (Ctrl+C per fermare)...")
    
    try:
        bot = RadioBot()
        bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Bot fermato")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()
