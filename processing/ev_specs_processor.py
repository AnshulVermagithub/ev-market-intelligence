import os

import numpy as np
import pandas as pd


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

INPUT_PATH = "data/raw/ev_specs_raw.csv"
OUTPUT_PATH = "data/processed/ev_specs_clean.csv"

ELECTRICITY_COST_PER_KWH = 8

RANGE_WEIGHT = 0.40
EFFICIENCY_WEIGHT = 0.30
AFFORDABILITY_WEIGHT = 0.30


# ---------------------------------------
# DATA LOADING
# ---------------------------------------

def load_data():
    """Load raw EV data from CSV."""

    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    if df.empty:
        raise ValueError("Input dataset is empty.")

    return df


# ---------------------------------------
# BASIC VALIDATION
# ---------------------------------------

def validate_data(df):
    """Validate core EV data before calculations."""

    required_columns = [
        "brand",
        "model",
        "variant",
        "battery_kwh",
        "range_km",
        "price_inr",
        "price_type",
        "currency",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Required text fields
    for column in [
        "brand",
        "model",
        "variant",
        "price_type",
        "currency",
    ]:
        if df[column].isna().any():
            raise ValueError(
                f"Missing values found in {column}."
            )

    # Numeric validation
    numeric_ranges = {
        "battery_kwh": (10, 200),
        "range_km": (50, 1000),
        "price_inr": (100000, 100000000),
    }

    for column, (minimum, maximum) in numeric_ranges.items():

        invalid = (
            df[column].notna()
            & (
                (df[column] < minimum)
                | (df[column] > maximum)
            )
        )

        if invalid.any():
            raise ValueError(
                f"Invalid values found in {column}."
            )

    # Charging time is optional
    if "charging_time_hr" in df.columns:

        invalid = (
            df["charging_time_hr"].notna()
            & (
                (df["charging_time_hr"] <= 0)
                | (df["charging_time_hr"] > 48)
            )
        )

        if invalid.any():
            raise ValueError(
                "Invalid charging_time_hr values found."
            )

    # Duplicate variant detection
    duplicates = df.duplicated(
        subset=["brand", "model", "variant"],
        keep=False,
    )

    if duplicates.any():
        raise ValueError(
            "Duplicate EV variants detected."
        )

    return df


# ---------------------------------------
# TECHNICAL METRICS
# ---------------------------------------

def calculate_metrics(df):
    """Calculate derived EV performance metrics."""

    # Range efficiency
    df["km_per_kwh"] = (
        df["range_km"]
        / df["battery_kwh"]
    )

    # Purchase-price efficiency
    df["price_per_km"] = (
        df["price_inr"]
        / df["range_km"]
    )

    # Price per battery capacity
    df["price_per_kwh"] = (
        df["price_inr"]
        / df["battery_kwh"]
    )

    # Charging speed
    # Missing charging times remain missing.
    df["km_per_hr_charge"] = np.where(
        df["charging_time_hr"].notna(),
        df["range_km"]
        / df["charging_time_hr"],
        np.nan,
    )

    # Estimated electricity operating cost
    df["cost_per_km"] = (
        df["battery_kwh"]
        * ELECTRICITY_COST_PER_KWH
        / df["range_km"]
    )

    # Estimated cost for a full battery charge
    df["full_charge_cost"] = (
        df["battery_kwh"]
        * ELECTRICITY_COST_PER_KWH
    )

    return df


# ---------------------------------------
# SEGMENTATION
# ---------------------------------------

def price_segment(price):
    """Classify EV by purchase price."""

    if price < 1500000:
        return "Budget"

    if price < 2500000:
        return "Mid"

    if price < 4000000:
        return "Premium"

    return "Luxury"


def range_segment(range_km):
    """Classify EV by claimed range."""

    if range_km < 250:
        return "Short"

    if range_km < 400:
        return "Medium"

    if range_km < 500:
        return "Long"

    return "Ultra"


def add_segments(df):
    """Add market segmentation fields."""

    df["price_segment"] = df["price_inr"].apply(
        price_segment
    )

    df["range_segment"] = df["range_km"].apply(
        range_segment
    )

    return df


# ---------------------------------------
# NORMALIZATION
# ---------------------------------------

def normalize(series):
    """Min-max normalization."""

    minimum = series.min()
    maximum = series.max()

    if minimum == maximum:
        return pd.Series(
            0.5,
            index=series.index,
        )

    return (
        (series - minimum)
        / (maximum - minimum)
    )


def normalize_inverse(series):
    """Inverse min-max normalization."""

    minimum = series.min()
    maximum = series.max()

    if minimum == maximum:
        return pd.Series(
            0.5,
            index=series.index,
        )

    return (
        (maximum - series)
        / (maximum - minimum)
    )


# ---------------------------------------
# EV VALUE INDEX
# ---------------------------------------

def calculate_value_index(df):
    """
    Calculate a dataset-relative EV Value Index.

    Higher score = stronger combination of:
    - range
    - efficiency
    - affordability
    """

    df["range_score"] = normalize(
        df["range_km"]
    )

    df["efficiency_score"] = normalize(
        df["km_per_kwh"]
    )

    df["affordability_score"] = normalize_inverse(
        df["price_per_km"]
    )

    df["ev_value_index"] = (
        RANGE_WEIGHT * df["range_score"]
        + EFFICIENCY_WEIGHT * df["efficiency_score"]
        + AFFORDABILITY_WEIGHT * df["affordability_score"]
    )

    df["ev_value_index"] = (
        df["ev_value_index"] * 100
    )

    return df


# ---------------------------------------
# DATA QUALITY FLAGS
# ---------------------------------------

def add_quality_flags(df):
    """Add data-quality indicators."""

    df["charging_time_missing"] = (
        df["charging_time_hr"].isna()
    )

    df["price_comparison_warning"] = (
        df["price_type"] != "ex_showroom"
    )

    return df


# ---------------------------------------
# FINAL VALIDATION
# ---------------------------------------

def final_validation(df):
    """Validate processed output."""

    numeric_columns = [
        "km_per_kwh",
        "price_per_km",
        "price_per_kwh",
        "cost_per_km",
        "full_charge_cost",
        "ev_value_index",
    ]

    for column in numeric_columns:

        if df[column].isna().all():
            raise ValueError(
                f"Processed column contains no usable data: {column}"
            )

    if (
        df["ev_value_index"].min() < 0
        or df["ev_value_index"].max() > 100
    ):
        raise ValueError(
            "EV Value Index must remain between 0 and 100."
        )

    return True


# ---------------------------------------
# SAVE OUTPUT
# ---------------------------------------

def save_processed_data(df):
    """Save cleaned and enriched EV dataset."""

    output_directory = os.path.dirname(
        OUTPUT_PATH
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


# ---------------------------------------
# MAIN PIPELINE
# ---------------------------------------

def main():

    print("EV processing started")

    # 1. Load
    df = load_data()

    print(
        f"Records loaded: {len(df)}"
    )

    # 2. Validate
    print("Validating input data...")

    df = validate_data(df)

    print("Input validation passed.")

    # 3. Calculate metrics
    print("Calculating EV metrics...")

    df = calculate_metrics(df)

    # 4. Add market segments
    print("Adding market segments...")

    df = add_segments(df)

    # 5. Calculate Value Index
    print("Calculating EV Value Index...")

    df = calculate_value_index(df)

    # 6. Add quality flags
    print("Adding data-quality flags...")

    df = add_quality_flags(df)

    # 7. Final validation
    print("Running final validation...")

    final_validation(df)

    # 8. Save
    save_processed_data(df)

    print(
        f"Processed data saved at {OUTPUT_PATH}"
    )

    print("EV processing finished")


# ---------------------------------------
# ENTRY POINT
# ---------------------------------------

if __name__ == "__main__":
    main()