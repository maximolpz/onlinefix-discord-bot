import os
import requests
from bs4 import BeautifulSoup

URL = "https://onlinefix-proxy.maximonahuellopez.workers.dev/"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SEEN_FILE = "seen_posts.txt"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf8") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf8") as f:
        for url in sorted(seen):
            f.write(url + "\n")


def send_discord(title, url, description, image):

    payload = {
        "embeds": [
            {
                "title": title,
                "url": url,
                "description": description,
                "color": 5763719,
                "image": {
                    "url": image
                },
                "footer": {
                    "text": "Nuevo juego OnlineFix - ElEnemigos"
                }
            }
        ]
    }

    r = requests.post(WEBHOOK, json=payload)

    print("Discord:", r.status_code)

    return r.status_code == 204


def main():

    print("Descargando página...")

    html = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    ).text

    soup = BeautifulSoup(html, "lxml")

    cards = soup.select("div.game-card")

    print("Cards encontradas:", len(cards))

    if not cards:
        print("No encontré juegos.")
        return

    seen = load_seen()

    nuevos = 0

    # Recorremos del más viejo al más nuevo
    for card in reversed(cards):

        a = card.find("a")

        if not a:
            continue

        link = "https://www.elenemigos.com" + a["href"]

        if link in seen:
            continue

        titulo = ""

        h2 = card.find("h2")
        if h2:
            titulo = h2.get_text(strip=True)

        descripcion = ""

        p = card.find("p")
        if p:
            descripcion = p.get_text(strip=True)

        imagen = ""

        img = card.find("img")
        if img:
            imagen = img.get("src", "")

        print("Nuevo:", titulo)

        if send_discord(
            titulo,
            link,
            descripcion,
            imagen
        ):
            seen.add(link)
            nuevos += 1

    save_seen(seen)

    print("Nuevos enviados:", nuevos)


if __name__ == "__main__":
    main()