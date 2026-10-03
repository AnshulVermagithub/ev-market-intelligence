from sources.manual_source import collect_ev_data as collect_manual_data
from sources.manufacturer_source import (
    collect_ev_data as collect_manufacturer_data
)


SOURCE_ADAPTERS = {
    "manual": {
        "collector": collect_manual_data,
        "priority": 2,
    },
    "manufacturer": {
        "collector": collect_manufacturer_data,
        "priority": 1,
    },
}


def create_record_id(record):
    """
    Create a stable identifier for an EV variant.
    """

    brand = str(record["brand"]).strip().lower()
    model = str(record["model"]).strip().lower()
    variant = str(record["variant"]).strip().lower()

    return (
        f"{brand}|"
        f"{model}|"
        f"{variant}"
    )


def collect_from_sources(source_names=None):
    """
    Collect EV records from registered source adapters.

    Lower priority number = higher source authority.
    """

    if source_names is None:
        source_names = list(SOURCE_ADAPTERS.keys())

    records = []

    for source_name in source_names:

        if source_name not in SOURCE_ADAPTERS:
            raise ValueError(
                f"Unknown source adapter: {source_name}"
            )

        source_config = SOURCE_ADAPTERS[source_name]

        collector = source_config["collector"]
        priority = source_config["priority"]

        source_records = collector()

        for record in source_records:

            record["source_priority"] = priority

            record["record_id"] = create_record_id(
                record
            )

            record["source_adapter"] = source_name

            records.append(record)

    return records