
import os
import pandas as pd

# Project paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")

# Required datasets
FILES = [
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

    print("\n========== DATA EXTRACTION ==========\n")

    for file in FILES:

        path = os.path.join(RAW_DIR, file)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing dataset: {file}")

        # Preserve ZIP codes as text
        dtype = {}

        if "customers" in file:
            dtype["customer_zip_code_prefix"] = "string"

        elif "sellers" in file:
            dtype["seller_zip_code_prefix"] = "string"

        elif "geolocation" in file:
            dtype["geolocation_zip_code_prefix"] = "string"

        df = pd.read_csv(path, dtype=dtype)

        # Match the concise keys expected by the Silver transformations.
        name = file.removesuffix(".csv").removeprefix("olist_")
        name = name.removesuffix("_dataset")

        datasets[name] = df

        print(f"{name}: {len(df)} rows, {len(df.columns)} columns")

    print("\nExtraction completed successfully!")

    return datasets


if __name__ == "__main__":
    data = extract_data()