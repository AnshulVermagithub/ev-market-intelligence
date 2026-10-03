import pandas as pd


REQUIRED_COLUMNS = [
    "brand",
    "model",
    "variant",
    "battery_kwh",
    "range_km",
    "charging_time_hr",
    "price_inr",
    "price_type",
    "currency",
    "source_name",
    "source_url",
    "collected_at",
]


def validate_schema(df):
    """
    Validate the structural schema of the EV dataset.

    Raises:
        ValueError: If required columns are missing.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


def validate_required_values(df):
    """
    Validate mandatory identifying and provenance fields.
    """

    required_value_columns = [
        "brand",
        "model",
        "variant",
        "currency",
        "source_name",
        "source_url",
        "collected_at",
    ]

    errors = []

    for column in required_value_columns:
        missing_count = df[column].isna().sum()

        if missing_count > 0:
            errors.append(
                f"{column}: {missing_count} missing values"
            )

    if errors:
        raise ValueError(
            "Required-value validation failed:\n"
            + "\n".join(errors)
        )

    return True


def validate_numeric_ranges(df):
    """
    Validate reasonable ranges for core EV specifications.
    """

    checks = {
        "battery_kwh": (10, 200),
        "range_km": (50, 1000),
        "charging_time_hr": (0.1, 48),
        "price_inr": (100000, 100000000),
    }

    errors = []

    for column, (minimum, maximum) in checks.items():

        # Allow missing values for fields that manufacturers
        # do not publish consistently.
        if column not in df.columns:
            continue

        invalid = df[column].notna() & (
            (df[column] < minimum)
            | (df[column] > maximum)
        )

        invalid_count = invalid.sum()

        if invalid_count > 0:
            errors.append(
                f"{column}: {invalid_count} values outside "
                f"valid range {minimum}-{maximum}"
            )

    if errors:
        raise ValueError(
            "Numeric-range validation failed:\n"
            + "\n".join(errors)
        )

    return True


def validate_duplicates(df):
    """
    Detect duplicate EV variants.

    At this stage duplicate variants should already have
    been resolved by the ingestion layer.
    """

    duplicate_columns = [
        "brand",
        "model",
        "variant",
    ]

    duplicates = df.duplicated(
        subset=duplicate_columns,
        keep=False
    )

    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Duplicate EV variants detected: "
            f"{duplicate_count} rows"
        )

    return True


def validate_ev_dataset(df):
    """
    Run all EV dataset validation checks.
    """

    validate_schema(df)
    validate_required_values(df)
    validate_numeric_ranges(df)
    validate_duplicates(df)

    return True