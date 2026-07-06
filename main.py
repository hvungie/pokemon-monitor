import requests
from bs4 import BeautifulSoup
import time
import hashlib
from datetime import datetime
import os

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

def send_discord_alert(site_name, is_30th=False):
    if is_30th:
        content = f"🔥 **30TH ANNIVERSARY DROP** on {site_name}!\nGo check now!"
    else:
        content = f"📢 New Pokémon TCG drop on {site_name}"
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": content})
    except:
        pass

def main():
    print(f"[{datetime.now()}] Pokémon TCG Monitor Started")
    print("Strict 30th Anniversary detection\n")
    
    while True:
        for site in SITES:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(site["url"], headers=headers, timeout=15)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                current_hash = hashlib.md5(page_text.encode('utf-8', errors='ignore')).hexdigest()
                
                if site["name"] in state and state[site["name"]] != current_hash:
                    # Strict 30th check
                    is_30th = any(phrase in page_text for phrase in [
                        "30th anniversary", "30th celebration", "pokemon 30th", 
                        "30 anniversary", "celebration etb", "30th etb"
                    ])
                    
                    print(f"[{datetime.now()}] Change on {site['name']} {'(30th!)' if is_30th else ''}")
                    send_discord_alert(site["name"], is_30th)
                
                state[site["name"]] = current_hash
            except:
                continue
        time.sleep(300)

if __name__ == "__main__":
    main()
