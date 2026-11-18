import os
import requests

WEBHOOK = os.environ["WEBHOOK"]

r = requests.get(
    "https://api.coingecko.com/api/v3/simple/price",
    params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
)
data = r.json()

pesan = (
    f"BTC: ${data['bitcoin']['usd']:,}\n"
    f"ETH: ${data['ethereum']['usd']:,}"
)
requests.post(WEBHOOK, json={"content": pesan})
