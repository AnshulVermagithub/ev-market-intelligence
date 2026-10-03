import os

import pandas as pd


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

CONFLICT_OUTPUT_PATH = (
    "data/quality/source_conflicts.csv"
)


# Fields where conflicting source values
# are analytically meaningful.
COMPARISON_FIELDS = [
    "battery_kwh",
    "range_km",
    "charging_time_hr",
    "price_inr",
    "price_type",
]


# ---------------------------------------
# CONFLICT DETECTION
# ---------------------------------------

def detect_conflicts(rows):
    """
    Detect conflicting values for the same EV variant
    across multiple sources.

    Returns
    -------
    pandas.DataFrame
        Conflict records.
    """

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    required_columns = [
        "record_id",
        "brand",
        "model",
        "variant",
        "source_name",
        "source_priority",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns for conflict detection: "
            f"{missing_columns}"
        )

    conflicts = []

    grouped = df.groupby(
        "record_id"
    )

    for record_id, group in grouped:

        # A single source cannot create
        # a cross-source conflict.
        if len(group) < 2:
            continue

        for field in COMPARISON_FIELDS:

            if field not in group.columns:
                continue

            values = group[field].dropna()

            if len(values) <= 1:
                continue

            unique_values = values.astype(str).unique()

            if len(unique_values) <= 1:
                continue

            conflicts.append(
                {
                    "record_id": record_id,
                    "brand": group["brand"].iloc[0],
                    "model": group["model"].iloc[0],
                    "variant": group["variant"].iloc[0],
                    "field": field,
                    "source_count": len(group),
                    "values": " | ".join(
                        unique_values
                    ),
                    "sources": " | ".join(
                        group["source_name"]
                        .astype(str)
                    ),
                    "priorities": " | ".join(
                        group["source_priority"]
                        .astype(str)
                    ),
                }
            )

    return pd.DataFrame(conflicts)


# ---------------------------------------
# SAVE CONFLICT LOG
# ---------------------------------------

def save_conflicts(conflicts):
    """
    Save detected source conflicts.
    """

    if conflicts.empty:
        print(
            "No source conflicts detected."
        )
        return

    output_directory = os.path.dirname(
        CONFLICT_OUTPUT_PATH
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    conflicts.to_csv(
        CONFLICT_OUTPUT_PATH,
        index=False
    )

    print(
        f"Source conflict log saved at "
        f"{CONFLICT_OUTPUT_PATH}"
    )