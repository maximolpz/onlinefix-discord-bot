import requests

url = "https://www.elenemigos.com/app/beamngdrive-descargar-gratis/19818"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, headers=headers)

print(r.status_code)
print(r.text[:200])
print("OnlineFix" in r.text)