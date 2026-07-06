import requests
from bs4 import BeautifulSoup
import time
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

KEYWORDS = ["pokemon", "tcg", "etb", "elite trainer", "booster", "pre-order", "preorder", "30th", "anniversary", "celebration"]

def send_discord_alert(site_name, products, is_30th=False):
    color = 0xff0000 if is_30th else 0x00aa00
    title = f"🔥 {site_name} - 30th Anniversary Found!" if is_30th else f"📢 {site_name} - Pokémon Preorder"
    
    embed = {
        "title": title,
        "color": color,
        "description": f"Found {len(products)} relevant item(s)",
        "timestamp": datetime.now().isoformat(),
        "fields": []
    }
    
    for p in products[:5]:
        embed["fields"].append({
            "name": p['title'][:100],
            "value": f"**Price:** {p['price']}\n**Link:** {p['link']}"
        })
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
        print(f"[{datetime.now()}] Alert sent - {site_name}")
    except:
        pass

def find_products(html, site_name):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(['li', 'div', 'article'], class_=lambda x: x and any(c in str(x).lower() for c in ['product', 'item']))
    found = []
    is_30th = False
    
    for item in items:
        title_tag = item.find(['h2', 'h3', 'a'])
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        if not any(kw.lower() in title.lower() for kw in KEYWORDS):
            continue
            
        price_tag = item.find(class_=lambda x: x and 'price' in str(x).lower())
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        
        link_tag = item.find('a', href=True)
        link = link_tag['href'] if link_tag else ""
        if link and not link.startswith('http'):
            link = f"https://{site_name.lower().replace(' ', '')}.com.au{link if link.startswith('/') else '/' + link}"
        
        found.append({'title': title, 'price': price, 'link': link})
        if any(kw.lower() in title.lower() for kw in ["30th", "anniversary"]):
            is_30th = True
    return found, is_30th

def main():
    print(f"[{datetime.now()}] Clean Pokémon Preorder Monitor Started")
    while True:
        for site in SITES:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(site["url"], headers=headers, timeout=15)
                if resp.status_code == 200:
                    products, is_30th = find_products(resp.text, site["name"])
                    if products:
                        print(f"Found on {site['name']}")
                        send_discord_alert(site["name"], products, is_30th)
            except:
                continue
        time.sleep(120)

if __name__ == "__main__":
    main()
