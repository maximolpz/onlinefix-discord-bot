import os
import requests
from bs4 import BeautifulSoup

URL = "https://elenemigos.com/tag/onlinefix"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

LAST_FILE = "last_post.txt"


def get_last():
    if not os.path.exists(LAST_FILE):
        return ""

    with open(LAST_FILE, "r", encoding="utf8") as f:
        return f.read().strip()


def save_last(url):
    with open(LAST_FILE, "w", encoding="utf8") as f:
        f.write(url)


headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers).text

soup = BeautifulSoup(html, "lxml")

card = soup.select_one("div.game-card")

if card is None:
    print("No encontré ningún juego.")
    quit()

a = card.find("a")

link = "https://elenemigos.com" + a["href"]

titulo = card.find("h2").text.strip()

descripcion = card.find("p").text.strip()

imagen = card.find("img")["src"]

ultimo = get_last()

if ultimo == link:
    print("No hay novedades.")
    quit()

payload = {
    "embeds": [
        {
            "title": titulo,
            "url": link,
            "description": descripcion,
            "color": 65280,
            "image": {
                "url": imagen
            },
            "footer": {
                "text": "Nuevo juego OnlineFix"
            }
        }
    ]
}

r = requests.post(WEBHOOK, json=payload)

print(r.status_code)

if r.status_code == 204:
    save_last(link)