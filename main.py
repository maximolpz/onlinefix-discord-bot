import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


URL = "https://elenemigos.com/tag/onlinefix"

BASE_URL = "https://elenemigos.com"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SEEN_FILE = "seen_posts.txt"


def get_seen():

    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf8") as f:
        return set(f.read().splitlines())


def save_seen(seen):

    with open(SEEN_FILE, "w", encoding="utf8") as f:
        for url in sorted(seen):
            f.write(url + "\n")



def get_html():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        )


        print("Abriendo página...")

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        # Esperar que carguen las tarjetas
        try:
            page.wait_for_selector(
                "div.game-card",
                timeout=30000
            )
        except:
            print("No apareció game-card")


        html = page.content()


        browser.close()


        return html



def send_discord(
    titulo,
    link,
    descripcion,
    imagen
):

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


    response = requests.post(
        WEBHOOK,
        json=payload
    )


    return response.status_code



def main():

    if not WEBHOOK:
        print("Falta DISCORD_WEBHOOK")
        return


    html = get_html()


    soup = BeautifulSoup(
        html,
        "lxml"
    )


    cards = soup.select(
        "div.game-card"
    )


    print(
        "Cards encontradas:",
        len(cards)
    )


    if not cards:
        print("No encontré juegos.")
        return



    seen = get_seen()


    print(
        "Posts guardados:",
        len(seen)
    )


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
        return



    print(
        "Posts nuevos:",
        len(new_posts)
    )



    # Publicar del más antiguo al más nuevo

    for card in reversed(new_posts):


        a = card.find("a")

        link = BASE_URL + a["href"]


        titulo = card.find("h2").text.strip()


        descripcion = ""

        p = card.find("p")

        if p:
            descripcion = p.text.strip()



        imagen = ""

        img = card.find("img")

        if img:
            imagen = img.get("src", "")



        status = send_discord(
            titulo,
            link,
            descripcion,
            imagen
        )


        print(
            titulo,
            status
        )


        if status == 204:
            seen.add(link)



    save_seen(seen)


    print("Historial actualizado.")



if __name__ == "__main__":
    main()