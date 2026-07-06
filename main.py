import requests
from bs4 import BeautifulSoup
import time
import hashlib
from datetime import datetime
import os

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

SITES = [
    {"name": "M&G", "url": "https://www.m-g.com.au/?s=pokemon+&post_type=product"},
    {"name": "Big W", "url": "https://www.bigw.com.au/search?q=pokemon"},
    {"name": "Target", "url": "https://www.target.com.au/search?searchTerm=pokemon"},
    {"name": "Gameology", "url": "https://www.gameology.com.au/collections/tcg-preorders?q=pokemon"},
    {"name": "The Gamesmen", "url": "https://www.gamesmen.com.au/trading-cards/brand/pokemon-trading-card-game"},
    {"name": "Cherry Collectables", "url": "https://cherrycollectables.com.au/search?q=pokemon"},
    {"name": "Rogue Collectables", "url": "https://roguecollectables.com.au/search?q=pokemon"},
    {"name": "Games Empire", "url": "https://www.gamesempire.com.au/search?q=pokemon"},
    {"name": "JToys", "url": "https://jtoys.com.au/search?q=pokemon"},
    {"name": "More Than Meeples", "url": "https://morethanmeeples.com.au/search?q=pokemon"},
]

state = {}

def send_discord_alert(site_name):
    try:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"🚨 **NEW POKÉMON DROP** on {site_name}!\nGo check for preorders now."
        })
    except:
        pass

def main():
    print(f"[{datetime.now()}] Full Pokémon Monitor Running (10 sites)")
    print("Only alerting on meaningful changes...\n")
    
    while True:
        for site in SITES:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(site["url"], headers=headers, timeout=15)
                if resp.status_code != 200:
                    continue
                
                # Cleaner content hash to reduce noise
                soup = BeautifulSoup(resp.text, 'html.parser')
                main_content = soup.get_text()[:8000]  # Focus on main area
                current_hash = hashlib.md5(main_content.encode('utf-8', errors='ignore')).hexdigest()
                
                if site["name"] in state and state[site["name"]] != current_hash:
                    print(f"[{datetime.now()}] Change detected on {site['name']}")
                    send_discord_alert(site["name"])
                
                state[site["name"]] = current_hash
            except:
                continue
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
