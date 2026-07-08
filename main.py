import os
import requests

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

payload = {
    "content": "@everyone\n\n✅ Prueba del bot desde GitHub Actions."
}

r = requests.post(WEBHOOK, json=payload)

print(r.status_code)
print(r.text)