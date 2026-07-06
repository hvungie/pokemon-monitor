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
    return "Pokémon TCG Pre-Order Monitor is running 24/7 ✅"

def send_discord_alert(site_name, products, is_30th=False):
    emoji = "🔥" if is_30th else "✅"
    msg = f"{emoji} **PRE-ORDER READY** on {site_name}!\n"
    if is_30th:
        msg += "**30th Anniversary detected!**\n"
    
    for p in products[:3]:  # Limit to 3 items
        msg += f"• {p['title']}\n  Price: {p['price']}\n  Link: {p['link']}\n\n"
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except:
        pass

def is_preorder_ready(text):
    ready = ["pre order now", "pre-order now", "add to cart", "buy now", "in stock", "preorder now"]
    not_ready = ["coming soon", "notify me when", "sold out"]
    return any(r in text.lower() for r in ready) and not any(n in text.lower() for n in not_ready)

def get_products(soup):
    products = []
    items = soup.find_all(['li', 'div'], class_=lambda x: x and any(c in str(x).lower() for c in ['product', 'item']))
    for item in items:
        title = item.find(['h2', 'h3', 'a'])
        title = title.get_text(strip=True) if title else ""
        if not any(k in title.lower() for k in ["pokemon", "tcg"]):
            continue
        price = item.find(class_=lambda x: x and 'price' in str(x).lower())
        price = price.get_text(strip=True) if price else "N/A"
        link = item.find('a', href=True)
        link = link['href'] if link else ""
        if link and not link.startswith('http'):
            link = "https://example.com" + link
        products.append({'title': title, 'price': price, 'link': link})
    return products

def monitor_loop():
    print("Monitor started - strict pre-order detection")
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
                    if is_preorder_ready(text):
                        products = get_products(soup)
                        is_30th = any(x in text for x in ["30th anniversary", "30th celebration", "pokemon 30th"])
                        send_discord_alert(site["name"], products, is_30th)
                        print(f"Alert sent for {site['name']}")
                
                state[site["name"]] = current_hash
            except:
                continue
        time.sleep(300)

threading.Thread(target=monitor_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
