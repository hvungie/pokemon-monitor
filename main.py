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
    emoji = "🔥" if is_30th else "📢"
    title = f"{emoji} **NEW DROP** on {site_name}!"
    if is_30th:
        title += " (30th Anniversary detected!)"
    
    try:
        requests.post(DISCORD_WEBHOOK, json={
            "content": title + "\nCheck the site for new TCG preorders."
        })
    except:
        pass

def main():
    print(f"[{datetime.now()}] Pokémon TCG Preorder Monitor Started")
    print("Focused on new drops only - especially 30th Anniversary\n")
    
    while True:
        for site in SITES:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(site["url"], headers=headers, timeout=15)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                main_content = soup.get_text()[:10000]
                current_hash = hashlib.md5(main_content.encode('utf-8', errors='ignore')).hexdigest()
                
                if site["name"] in state and state[site["name"]] != current_hash:
                    print(f"[{datetime.now()}] New drop detected on {site['name']}")
                    # Check if 30th Anniversary is mentioned
                    is_30th = "30th" in main_content.lower() or "anniversary" in main_content.lower()
                    send_discord_alert(site["name"], is_30th)
                
                state[site["name"]] = current_hash
            except:
                continue
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
