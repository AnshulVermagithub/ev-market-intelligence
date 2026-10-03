import os

import numpy as np
import pandas as pd


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

INPUT_PATH = "data/raw/ev_specs_raw.csv"
OUTPUT_PATH = "data/processed/ev_specs_clean.csv"

ELECTRICITY_COST_PER_KWH = 8


# ---------------------------------------
# DATA LOADING
# ---------------------------------------

def load_data(input_path):
    """Load raw EV data from CSV."""
    return pd.read_csv(input_path)


# ---------------------------------------
# DATA VALIDATION
# ---------------------------------------

def validate_data(df):
    """Apply data-quality rules and remove invalid records."""

    # Required fields
    df = df.dropna(subset=["brand", "model"])

    # Battery validation
    df = df[
        (df["battery_kwh"] >= 10) &
        (df["battery_kwh"] <= 200)
    ]

    # Range validation
    df = df[
        (df["range_km"] >= 50) &
        (df["range_km"] <= 1000)
    ]

    # Charging time validation
    df = df[
        (df["charging_time_hr"] >= 0.5) &
        (df["charging_time_hr"] <= 48)
    ]

    # Price validation
    df = df[df["price_inr"] >= 100000]

    # Remove duplicate vehicles
    df = df.drop_duplicates(subset=["brand", "model"])

    return df


# ---------------------------------------
# KPI CALCULATIONS
# ---------------------------------------

def calculate_metrics(df):
    """Calculate EV performance, pricing and running-cost metrics."""

    # Efficiency
    df["km_per_kwh"] = (
        df["range_km"] / df["battery_kwh"]
    )

    # Pricing efficiency
    df["price_per_km"] = (
        df["price_inr"] / df["range_km"]
    )

    df["price_per_kwh"] = (
        df["price_inr"] / df["battery_kwh"]
    )

    # Charging productivity
    df["km_per_hr_charge"] = (
        df["range_km"] / df["charging_time_hr"]
    )

    # Running economics
    df["cost_per_km"] = (
        ELECTRICITY_COST_PER_KWH / df["km_per_kwh"]
    )

    df["full_charge_cost"] = (
        df["battery_kwh"] * ELECTRICITY_COST_PER_KWH
    )

    return df


# ---------------------------------------
# SEGMENTATION
# ---------------------------------------

def price_segment(price):
    """Classify vehicles based on purchase price."""

    if price < 1_000_000:
        return "Budget"
    elif price < 2_000_000:
        return "Mid"
    elif price < 4_000_000:
        return "Premium"
    else:
        return "Luxury"


def range_segment(range_km):
    """Classify vehicles based on driving range."""

    if range_km < 200:
        return "Short"
    elif range_km < 350:
        return "Medium"
    elif range_km < 500:
        return "Long"
    else:
        return "Ultra"


def add_segments(df):
    """Add business segments to the dataset."""

    df["price_segment"] = df["price_inr"].apply(price_segment)
    df["range_segment"] = df["range_km"].apply(range_segment)

    return df


# ---------------------------------------
# NORMALIZATION
# ---------------------------------------

def normalize(series):
    """Normalize values between 0 and 1."""

    if series.max() == series.min():
        return pd.Series(0.5, index=series.index)

    return (
        (series - series.min()) /
        (series.max() - series.min())
    )


def normalize_inverse(series):
    """Normalize values between 0 and 1 where lower is better."""

    if series.max() == series.min():
        return pd.Series(0.5, index=series.index)

    return (
        (series.max() - series) /
        (series.max() - series.min())
    )


# ---------------------------------------
# EV VALUE INDEX
# ---------------------------------------

def calculate_value_index(df):
    """Calculate the composite EV Value Index."""

    df["range_score"] = normalize(df["range_km"])

    df["efficiency_score"] = normalize(
        df["km_per_kwh"]
    )

    df["affordability_score"] = normalize_inverse(
        df["price_per_km"]
    )

    df["ev_value_index"] = (
        0.4 * df["range_score"] +
        0.3 * df["efficiency_score"] +
        0.3 * df["affordability_score"]
    )

    df["ev_value_index"] = (
        df["ev_value_index"] * 100
    )

    return df


# ---------------------------------------
# FINAL DATA QUALITY CHECK
# ---------------------------------------

def final_validation(df):
    """Remove infinite and missing calculated values."""

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    df.dropna(inplace=True)

    return df


# ---------------------------------------
# MAIN PIPELINE
# ---------------------------------------

def main():

    print("Processing script started")

    # Ensure output directory exists
    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    # Load
    df = load_data(INPUT_PATH)

    print(f"Raw records: {len(df)}")

    # Validate
    df = validate_data(df)

    print(f"Clean records: {len(df)}")

    # Calculate metrics
    df = calculate_metrics(df)

    # Add segments
    df = add_segments(df)

    # Calculate Value Index
    df = calculate_value_index(df)

    # Final validation
    df = final_validation(df)

    # Save
    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"Clean data saved at {OUTPUT_PATH}"
    )

    print("Processing script finished")


if __name__ == "__main__":
    main()