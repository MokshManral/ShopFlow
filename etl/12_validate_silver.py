import pandas as pd
from pathlib import Path

# 1. Define project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
SILVER_DIR = PROJECT_DIR / "data" / "silver"

# 2. Define datasets and their expected keys
datasets = {
    "orders": {
        "file": "orders/orders_cleaned.csv",
        "keys": ["order_id"]
    },
    "order_items": {
        "file": "order_items/order_items_cleaned.csv",
        "keys": ["order_id", "order_item_id"]
    },
    "payments": {
        "file": "payments/payments_cleaned.csv",
        "keys": ["order_id", "payment_sequential"]
    },
    "customers": {
        "file": "customers/customers_cleaned.csv",
        "keys": ["customer_id"]
    },
    "products": {
        "file": "products/products_cleaned.csv",
        "keys": ["product_id"]
    },
    "sellers": {
        "file": "sellers/sellers_cleaned.csv",
        "keys": ["seller_id"]
    },
    "reviews": {
        "file": "reviews/reviews_cleaned.csv",
        "keys": ["review_id", "order_id"]
    },
    "geolocation": {
        "file": "geolocation/geolocation_cleaned.csv",
        "keys": []
    },
    "category_translation": {
        "file": "category_translation/category_translation_cleaned.csv",
        "keys": ["product_category_name"]
    }
}

# 3. Track validation results
total_errors = 0

print("\n========== SILVER LAYER QUALITY AUDIT ==========\n")

# 4. Validate each dataset
for name, config in datasets.items():

    file_path = SILVER_DIR / config["file"]

    print(f"\nChecking: {name}")

    # Check whether file exists
    if not file_path.exists():
        print("ERROR: File not found:", file_path)
        total_errors += 1
        continue

    # Load dataset
    df = pd.read_csv(file_path)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    keys = config["keys"]

    if not keys:
        print("No unique key validation required.")
        print("STATUS: PASSED")
        continue

    # Check required key columns
    missing_columns = [
        column for column in keys
        if column not in df.columns
    ]

    if missing_columns:
        print("ERROR: Missing key columns:", missing_columns)
        total_errors += 1
        continue

    # Check missing key values
    missing_keys = df[keys].isnull().any(axis=1).sum()

    print("Rows with missing key values:", missing_keys)

    # Check duplicate key combinations
    duplicate_keys = df.duplicated(
        subset=keys,
        keep=False
    ).sum()

    print("Rows with duplicate keys:", duplicate_keys)

    if missing_keys > 0 or duplicate_keys > 0:
        print("STATUS: FAILED")
        total_errors += 1
    else:
        print("STATUS: PASSED")

# 5. Final audit summary
print("\n========== FINAL AUDIT SUMMARY ==========")

if total_errors == 0:
    print("ALL DATASETS PASSED!")
    print("Silver layer quality audit completed successfully.")
else:
    print("AUDIT FAILED!")
    print("Number of datasets with errors:", total_errors)
    print("Please investigate the errors before proceeding.")
