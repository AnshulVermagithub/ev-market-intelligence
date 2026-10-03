from datetime import datetime, timezone


def collect_ev_data():
    """
    Return standardized EV variant records.

    This adapter currently contains a small curated dataset
    using manufacturer-level source information. It is designed
    to be replaced or supplemented by automated source adapters.
    """

    collected_at = datetime.now(timezone.utc).isoformat()

    return [
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
            "source_url": "https://prod-ev.tatamotors.com/nexon/ev/specifications.html",
            "collected_at": collected_at,
        },
        {
            "brand": "Hyundai",
            "model": "Creta Electric",
            "variant": "42 kWh",
            "battery_kwh": 42,
            "range_km": 420,
            "charging_time_hr": 6,
            "price_inr": 1802800,
            "price_type": "ex_showroom",
            "currency": "INR",
            "source_name": "Hyundai India",
            "source_url": "https://www.hyundai.com/in/en/find-a-car/creta-electric/specification",
            "collected_at": collected_at,
        },
        {
            "brand": "Hyundai",
            "model": "Creta Electric",
            "variant": "51.4 kWh Long Range",
            "battery_kwh": 51.4,
            "range_km": 510,
            "charging_time_hr": 7.25,
            "price_inr": 1802800,
            "price_type": "ex_showroom",
            "currency": "INR",
            "source_name": "Hyundai India",
            "source_url": "https://www.hyundai.com/in/en/find-a-car/creta-electric/specification",
            "collected_at": collected_at,
        },
        {
            "brand": "MG",
            "model": "ZS EV",
            "variant": "50.3 kWh",
            "battery_kwh": 50.3,
            "range_km": 461,
            "charging_time_hr": None,
            "price_inr": 1300000,
            "price_type": "ex_showroom",
            "currency": "INR",
            "source_name": "MG Motor India",
            "source_url": "https://www.mgmotor.co.in/",
            "collected_at": collected_at,
        },
    ]