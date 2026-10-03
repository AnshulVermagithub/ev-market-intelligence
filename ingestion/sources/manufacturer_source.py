from datetime import datetime, timezone


def collect_ev_data():
    """
    Return standardized EV records from a manufacturer source.

    This is currently a prototype adapter. The structure is
    designed so that verified manufacturer data can later be
    collected without changing the downstream pipeline.
    """

    collected_at = datetime.now(timezone.utc).isoformat()

    records = [
        {
            "brand": "Tata",
            "model": "Nexon EV",
            "variant": "45 kWh",
            "battery_kwh": 45,
            "range_km": 489,
            "charging_time_hr": None,
            "price_inr": 1434000,
            "price_type": "ex_showroom",
            "currency": "INR",
            "source_name": "Tata.ev",
            "source_url": (
                "https://prod-ev.tatamotors.com/"
                "nexon/ev/specifications.html"
            ),
            "collected_at": collected_at,
        }
    ]

    return records