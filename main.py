import os
import requests
from bs4 import BeautifulSoup


URL = "https://elenemigos.com/tag/onlinefix"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SEEN_FILE = "seen_posts.txt"

BASE_URL = "https://elenemigos.com"


def get_seen():

    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf8") as f:
        return set(f.read().splitlines())


def save_seen(posts):

    with open(SEEN_FILE, "w", encoding="utf8") as f:
        for post in posts:
            f.write(post + "\n")



headers = {
    "User-Agent": "Mozilla/5.0"
}


html = requests.get(URL, headers=headers).text

soup = BeautifulSoup(html, "lxml")


cards = soup.select("div.game-card")


if not cards:
    print("No encontré juegos")
    exit()



seen = get_seen()

new_posts = []


for card in cards:

    a = card.find("a")

    if not a:
        continue


    link = BASE_URL + a["href"]


    if link not in seen:
        new_posts.append(card)



if not new_posts:

    print("No hay novedades.")
    exit()



# Publicar los nuevos

for card in reversed(new_posts):

    a = card.find("a")

    link = BASE_URL + a["href"]

    titulo = card.find("h2").text.strip()

    descripcion = card.find("p").text.strip()

    imagen = card.find("img")["src"]


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


    r = requests.post(
        WEBHOOK,
        json=payload
    )


    print(titulo, r.status_code)


    if r.status_code == 204:
        seen.add(link)



save_seen(seen)