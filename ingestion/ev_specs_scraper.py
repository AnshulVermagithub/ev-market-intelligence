import requests
import csv
import os

print("Script started")

URLS = [
    {
        "brand": "Tata",
        "model": "Nexon EV",
        "url": "https://example.com"
    }
]

rows = []

for item in URLS:
    response = requests.get(item["url"])
    print(f"Status code: {response.status_code}")

    rows.append({
        "brand": item["brand"],
        "model": item["model"],
        "battery_kwh": 40,
        "range_km": 465,
        "charging_time_hr": 8,
        "price_inr": 1500000,
        "source_url": item["url"]
    })

output_path = "data/raw/ev_specs_raw.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV successfully saved at {output_path}")
print("Script finished")
