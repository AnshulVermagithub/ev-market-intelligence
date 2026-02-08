import pandas as pd
import os

print("Processing script started")

# File paths
input_path = "data/raw/ev_specs_raw.csv"
output_path = "data/processed/ev_specs_clean.csv"

# Ensure output folder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load raw data
df = pd.read_csv(input_path)

print(f"Raw records: {len(df)}")

# -----------------------------
# VALIDATION RULES
# -----------------------------

# Drop null brand/model
df = df.dropna(subset=["brand", "model"])

# Battery validation
df = df[(df["battery_kwh"] >= 10) & (df["battery_kwh"] <= 200)]

# Range validation
df = df[(df["range_km"] >= 50) & (df["range_km"] <= 1000)]

# Charging time validation
df = df[(df["charging_time_hr"] >= 0.5) & (df["charging_time_hr"] <= 48)]

# Price validation
df = df[df["price_inr"] >= 100000]

# Remove duplicates
df = df.drop_duplicates(subset=["brand", "model"])

print(f"Clean records: {len(df)}")


import numpy as np

# -----------------------------
# Efficiency Metrics
# -----------------------------
df["km_per_kwh"] = df["range_km"] / df["battery_kwh"]

# -----------------------------
# Pricing Efficiency
# -----------------------------
df["price_per_km"] = df["price_inr"] / df["range_km"]
df["price_per_kwh"] = df["price_inr"] / df["battery_kwh"]

# -----------------------------
# Charging Productivity
# -----------------------------
df["km_per_hr_charge"] = df["range_km"] / df["charging_time_hr"]

# -----------------------------
# Running Economics
# -----------------------------
ELECTRICITY_COST_PER_KWH = 8  # ₹ assumption

df["cost_per_km"] = ELECTRICITY_COST_PER_KWH / df["km_per_kwh"]
df["full_charge_cost"] = df["battery_kwh"] * ELECTRICITY_COST_PER_KWH

# -----------------------------
# Price Segmentation
# -----------------------------
def price_segment(price):
    if price < 1000000:
        return "Budget"
    elif price < 2000000:
        return "Mid"
    elif price < 4000000:
        return "Premium"
    else:
        return "Luxury"

df["price_segment"] = df["price_inr"].apply(price_segment)

# -----------------------------
# Range Segmentation
# -----------------------------
def range_segment(r):
    if r < 200:
        return "Short"
    elif r < 350:
        return "Medium"
    elif r < 500:
        return "Long"
    else:
        return "Ultra"

df["range_segment"] = df["range_km"].apply(range_segment)

# -----------------------------
# Data Validation
# -----------------------------
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)
# -----------------------------
# NORMALIZATION FUNCTION
# -----------------------------
def normalize(series):
    if series.max() == series.min():
        return 0.5  # neutral score
    return (series - series.min()) / (series.max() - series.min())

def normalize_inverse(series):
    if series.max() == series.min():
        return 0.5
    return (series.max() - series) / (series.max() - series.min())

# -----------------------------
# NORMALIZED SCORES
# -----------------------------
df["range_score"] = normalize(df["range_km"])
df["efficiency_score"] = normalize(df["km_per_kwh"])
df["affordability_score"] = normalize_inverse(df["price_per_km"])

# -----------------------------
# COMPOSITE VALUE INDEX
# -----------------------------
df["ev_value_index"] = (
    0.4 * df["range_score"] +
    0.3 * df["efficiency_score"] +
    0.3 * df["affordability_score"]
)

# Scale to 100 for executive readability
df["ev_value_index"] = df["ev_value_index"] * 100

# Save clean dataset
df.to_csv(output_path, index=False)

print(f"Clean data saved at {output_path}")
print("Processing script finished")


