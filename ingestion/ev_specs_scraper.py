import csv
import os
import sys

import pandas as pd


# ---------------------------------------
# PROJECT ROOT
# ---------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------
# PROJECT IMPORTS
# ---------------------------------------

from sources.source_registry import collect_from_sources
from processing.validation.ev_schema_validator import validate_ev_dataset
from processing.validation.conflict_detector import detect_conflicts, save_conflicts


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "ev_specs_raw.csv"
)


# ---------------------------------------
# RAW DATA STORAGE
# ---------------------------------------

def save_raw_data(rows, output_path):
    """Save standardized EV records to CSV."""

    if not rows:
        raise ValueError("No EV records collected.")

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    fieldnames = rows[0].keys()

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------
# DEDUPLICATION
# ---------------------------------------

def deduplicate_records(rows):
    """
    Resolve duplicate EV variants using source priority.

    Lower source_priority = higher authority.

    The highest-authority record is retained.
    """

    if not rows:
        return rows

    df = pd.DataFrame(rows)

    # Highest-authority source first
    df = df.sort_values(
        by="source_priority"
    )

    duplicate_count = df.duplicated(
        subset=["record_id"],
        keep=False
    ).sum()

    if duplicate_count > 0:
        print(
            f"Duplicate records detected: "
            f"{duplicate_count}"
        )

    # Keep highest-authority record
    df = df.drop_duplicates(
        subset=["record_id"],
        keep="first"
    )

    return df.to_dict(
        orient="records"
    )


# ---------------------------------------
# INGESTION PIPELINE
# ---------------------------------------

def main():

    print("EV ingestion started")

    # Collect records from all registered sources
    rows = collect_from_sources()

    print(
        f"Records collected before deduplication: "
        f"{len(rows)}"
    )
    # Detect conflicts before deduplication
    conflicts = detect_conflicts(rows)

    save_conflicts(conflicts)
    # Resolve cross-source duplicates
    rows = deduplicate_records(rows)

    print(
        f"Records remaining after deduplication: "
        f"{len(rows)}"
    )

    # Convert records into DataFrame
    df = pd.DataFrame(rows)

    # Validate final dataset
    print("Validating EV dataset...")

    validate_ev_dataset(df)

    print("Dataset validation passed.")

    # Save validated raw records
    save_raw_data(
        rows,
        OUTPUT_PATH
    )

    print(
        f"Raw data saved at "
        f"{os.path.relpath(OUTPUT_PATH, PROJECT_ROOT)}"
    )

    print("EV ingestion finished")


# ---------------------------------------
# ENTRY POINT
# ---------------------------------------

if __name__ == "__main__":
    main()