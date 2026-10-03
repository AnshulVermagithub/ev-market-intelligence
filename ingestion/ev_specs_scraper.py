import csv
import os

from sources.manual_source import collect_ev_data


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

OUTPUT_PATH = "data/raw/ev_specs_raw.csv"


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
# INGESTION PIPELINE
# ---------------------------------------

def main():

    print("EV ingestion started")

    # Collect standardized records from source adapter
    rows = collect_ev_data()

    print(f"Records collected: {len(rows)}")

    # Save raw records
    save_raw_data(
        rows,
        OUTPUT_PATH
    )

    print(
        f"Raw data saved at {OUTPUT_PATH}"
    )

    print("EV ingestion finished")


if __name__ == "__main__":
    main()