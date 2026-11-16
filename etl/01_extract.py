import pandas as pd
from pathlib import Path

# Find the project directory and raw data folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

# List of datasets required by ShopFlow
REQUIRED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv"
]


def extract_data():
    datasets = {}

    print("Starting data extraction...\n")

    for filename in REQUIRED_FILES:
        file_path = DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing dataset: {filename}"
            )

        df = pd.read_csv(file_path)

        dataset_name = filename.replace(
            ".csv", ""
        ).replace("olist_", "")

        datasets[dataset_name] = df

        print(
            f"Loaded {filename} | "
            f"Rows: {len(df)} | "
            f"Columns: {len(df.columns)}"
        )

    print("\nData extraction completed!")

    return datasets


if __name__ == "__main__":
    data = extract_data()