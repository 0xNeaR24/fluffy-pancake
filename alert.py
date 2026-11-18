import json
import os
import requests

WEBHOOK = os.environ["WEBHOOK"]
AMBANG = 3.0  # persen perubahan yang memicu alert
FILE = "harga.json"

KOIN = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "solana": "SOL",
    "near": "NEAR",
    "pi-network": "PI",
}


def fmt(x):
    return f"${x:,.2f}" if x >= 1 else f"${x:,.4f}"


try:
    with open(FILE) as f:
        dasar = json.load(f)
except FileNotFoundError:
    dasar = {}

r = requests.get(
    "https://api.coingecko.com/api/v3/simple/price",
    params={"ids": ",".join(KOIN), "vs_currencies": "usd"},
    timeout=30,
)
r.raise_for_status()
data = r.json()

manual = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
alert, ringkas = [], []

for cid, sim in KOIN.items():
    harga = data.get(cid, {}).get("usd")
    if harga is None:
        continue
    ringkas.append(f"{sim}: {fmt(harga)}")
    awal = dasar.get(cid)
    if awal is None:
        dasar[cid] = harga
        continue
    persen = (harga - awal) / awal * 100
    if abs(persen) >= AMBANG:
        panah = "📈" if persen > 0 else "📉"
        alert.append(
            f"{panah} {sim}: {fmt(harga)} ({persen:+.1f}% dari {fmt(awal)})"
        )
        dasar[cid] = harga

with open(FILE, "w") as f:
    json.dump(dasar, f)

if alert:
    requests.post(WEBHOOK, json={"content": "\n".join(alert)})
elif manual:
    requests.post(
        WEBHOOK, json={"content": "Tes manual:\n" + "\n".join(ringkas)}
    )
