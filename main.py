import os
import requests
from bs4 import BeautifulSoup


URL = "https://www.elenemigos.com/tag/onlinefix"

BASE_URL = "https://www.elenemigos.com"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SEEN_FILE = "seen_posts.txt"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}



def get_seen():

    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(
            line.strip()
            for line in f.readlines()
            if line.strip()
        )



def save_seen(seen):

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for item in sorted(seen):
            f.write(item + "\n")



def get_page():

    print("Descargando página...")


    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )


    print(
        "STATUS:",
        response.status_code
    )


    print(
        "HTML LENGTH:",
        len(response.text)
    )


    if response.status_code != 200:
        print(
            response.text[:300]
        )
        return None


    return response.text



def send_discord(
    titulo,
    url,
    descripcion,
    imagen
):

    payload = {
        "embeds": [
            {
                "title": titulo,
                "url": url,
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
        json=payload,
        timeout=30
    )


    print(
        "Discord:",
        response.status_code
    )


    return response.status_code == 204



def main():

    if not WEBHOOK:
        print(
            "ERROR: Falta DISCORD_WEBHOOK"
        )
        return



    html = get_page()


    if not html:
        return



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
        print(
            "No encontré juegos."
        )
        return



    seen = get_seen()


    nuevos = []



    for card in cards:

        a = card.find("a")

        if not a:
            continue


        link = BASE_URL + a.get("href")


        if link not in seen:
            nuevos.append(card)



    print(
        "Nuevos:",
        len(nuevos)
    )



    if not nuevos:

        print(
            "No hay novedades."
        )
        return



    for card in reversed(nuevos):


        a = card.find("a")

        link = BASE_URL + a["href"]



        titulo = card.find("h2")

        if titulo:
            titulo = titulo.text.strip()
        else:
            titulo = "Sin título"



        descripcion = card.find("p")

        if descripcion:
            descripcion = descripcion.text.strip()
        else:
            descripcion = ""



        imagen = card.find("img")

        if imagen:
            imagen = imagen.get("src", "")
        else:
            imagen = ""



        enviado = send_discord(
            titulo,
            link,
            descripcion,
            imagen
        )


        if enviado:
            seen.add(link)



    save_seen(seen)


    print(
        "Historial actualizado."
    )



if __name__ == "__main__":
    main()