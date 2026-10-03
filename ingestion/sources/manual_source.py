from datetime import datetime, timezone


def collect_ev_data():
    """
    Return standardized EV records.

    This adapter currently uses a manually curated
    prototype dataset. It will later be replaced
    or supplemented with an authorized data source.
    """

    collected_at = datetime.now(timezone.utc).isoformat()

    return [
        {
            "brand": "Tata",
            "model": "Nexon EV",
            "battery_kwh": 40,
            "range_km": 465,
            "charging_time_hr": 8,
            "price_inr": 1500000,
            "currency": "INR",
            "source_name": "Prototype Dataset",
            "source_url": "https://example.com",
            "collected_at": collected_at,
        },
        {
            "brand": "MG",
            "model": "ZS EV",
            "battery_kwh": 50.3,
            "range_km": 461,
            "charging_time_hr": 9,
            "price_inr": 2300000,
            "currency": "INR",
            "source_name": "Prototype Dataset",
            "source_url": "https://example.com",
            "collected_at": collected_at,
        },
        {
            "brand": "Hyundai",
            "model": "Kona Electric",
            "battery_kwh": 39.2,
            "range_km": 452,
            "charging_time_hr": 7,
            "price_inr": 2400000,
            "currency": "INR",
            "source_name": "Prototype Dataset",
            "source_url": "https://example.com",
            "collected_at": collected_at,
        },
        {
            "brand": "Mahindra",
            "model": "XUV400",
            "battery_kwh": 39.4,
            "range_km": 456,
            "charging_time_hr": 6.5,
            "price_inr": 1800000,
            "currency": "INR",
            "source_name": "Prototype Dataset",
            "source_url": "https://example.com",
            "collected_at": collected_at,
        },
        {
            "brand": "BYD",
            "model": "Atto 3",
            "battery_kwh": 60.5,
            "range_km": 521,
            "charging_time_hr": 10,
            "price_inr": 3400000,
            "currency": "INR",
            "source_name": "Prototype Dataset",
            "source_url": "https://example.com",
            "collected_at": collected_at,
        },
    ]