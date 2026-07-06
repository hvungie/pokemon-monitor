from flask import Flask
import threading
import requests
from bs4 import BeautifulSoup
import time
import hashlib
from datetime import datetime
import os

app = Flask(__name__)

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

SITES = [
    {"name": "Mind Games", "url": "https://mindgames.com.au/search?q=pokemon"},
    {"name": "Big W", "url": "https://www.bigw.com.au/search?q=pokemon"},
    {"name": "The Gamesmen", "url": "https://www.gamesmen.com.au/trading-cards/brand/pokemon-trading-card-game"},
    {"name": "Cherry Collectables", "url": "https://cherrycollectables.com.au/search?q=pokemon"},
    {"name": "JToys", "url": "https://jtoys.com.au/search?q=pokemon"},
    {"name": "More Than Meeples", "url": "https://morethanmeeples.com.au/search?q=pokemon"},
    {"name": "GamesCube", "url": "https://gamescube.com.au/search?q=pokemon"},
]

state = {}

@app.route('/')
def home():
    return "Pokémon TCG Preorder Monitor is running 24/7 ✅"

def send_discord_alert(site_name, is_30th=False):
    emoji = "🔥" if is_30th else "📢"
    msg = f"{emoji} **NEW DROP** on {site_name}!"
    if is_30th:
        msg += " (30th Anniversary detected!)"
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        pass

def monitor_loop():
    print(f"[{datetime.now()}] Monitor loop started")
    while True:
        for site in SITES:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(site["url"], headers=headers, timeout=15)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text().lower()
                current_hash = hashlib.md5(text.encode('utf-8', errors='ignore')).hexdigest()
                
                if site["name"] in state and state[site["name"]] != current_hash:
                    is_30th = any(phrase in text for phrase in ["30th anniversary", "30th celebration", "pokemon 30th"])
                    print(f"New drop on {site['name']}")
                    send_discord_alert(site["name"], is_30th)
                
                state[site["name"]] = current_hash
            except:
                continue
        time.sleep(300)

# Start monitor in background
threading.Thread(target=monitor_loop, daemon=True).start()

if __name__ == "__main__":
    print("Starting Pokémon Monitor Web Service...")
    app.run(host='0.0.0.0', port=10000)
