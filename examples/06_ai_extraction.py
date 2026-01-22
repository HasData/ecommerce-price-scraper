import requests
from decimal import Decimal
import re
import json
import csv

# HasData API with AI extraction for complex pricing patterns
API_KEY = "YOUR_HASDATA_API_KEY"
TARGET_URL = "https://www.amazon.com/Under-Armour-Iso-Chill-Adjustable-Reflective/dp/B0C138SH1L/?th=1&psc=1"

payload = {
    "url": TARGET_URL,
    "proxyType": "residential",
    "proxyCountry": "US",
    "jsRendering": True,
    "aiExtractRules": {
        "price_data": {
            "type": "list",
            "output": {
                "product_variant": {
                    "type": "string",
                    "description": "Current product or product variant"
                },
                "current_price": {
                    "type": "string",
                    "description": "Current selling price with currency symbol"
                },
                "original_price": {
                    "type": "string", 
                    "description": "Original price before discount if available"
                },
                "currency": {
                    "type": "string",
                    "description": "ISO 4217 currency code (USD, EUR, GBP)"
                },
                "availability": {
                    "type": "string",
                    "description": "Stock status: In Stock, Out of Stock, or specific quantity"
                }
            }
        }
    }
}

response = requests.post(
    "https://api.hasdata.com/scrape/web",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json=payload,
    timeout=30
)

def normalize_price(price_str):
    if not price_str:
        return None
    clean = re.sub(r"[^\d.]", "", price_str)
    return str(Decimal(clean)) if clean else None

if response.status_code == 200:
    data = response.json()
    price_info = data.get("aiResponse", {}).get("price_data", [])

    rows = []

    for item in price_info:
        row = {
            "variant": item.get("product_variant"),
            "current_price": normalize_price(item.get("current_price")),
            "original_price": normalize_price(item.get("original_price")),
            "currency": item.get("currency"),
            "availability": item.get("availability"),
        }
        rows.append(row)

    header = f"{'Variant':45} | {'Current':10} | {'Original':10} | {'Cur':3} | Availability"
    print(header)
    print("-" * len(header))

    for r in rows:
        print(
            f"{r['variant'][:45]:45} | "
            f"{r['current_price']:10} | "
            f"{r['original_price']:10} | "
            f"{r['currency']:3} | "
            f"{r['availability']}"
        )

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    with open("prices.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["variant", "current_price", "original_price", "currency", "availability"]
        )
        writer.writeheader()
        writer.writerows(rows)