
import os
import pandas as pd


# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOLD_DIR = os.path.join(ROOT, "data", "gold")


# ==========================================
# 2. DATASET CONFIGURATION
# ==========================================

DATASETS = {
    "orders": {
        "file": "orders/gold_order_analytics.csv",
        "keys": ["order_id"]
    },

    "products": {
        "file": "products/gold_product_analytics.csv",
        "keys": ["product_id"]
    },

    "customers": {
        "file": "customers/gold_customer_analytics.csv",
        "keys": ["customer_unique_id"]
    },

    "sellers": {
        "file": "sellers/gold_seller_analytics.csv",
        "keys": ["seller_id"]
    },

    "payments": {
        "file": "payments/gold_payment_analytics.csv",
        "keys": ["payment_type"]
    },

    "cities": {
        "file": "cities/gold_city_analytics.csv",
        "keys": ["customer_city", "customer_state"]
    },

    "daily_sales": {
        "file": "daily_sales/gold_daily_sales.csv",
        "keys": ["order_date"]
    },

    "monthly_sales": {
        "file": "monthly_sales/gold_monthly_sales.csv",
        "keys": ["month"]
    },

    "reviews": {
        "file": "reviews/gold_review_analytics.csv",
        "keys": ["review_score"]
    }
}


# ==========================================
# 3. VALIDATION FUNCTION
# ==========================================

def validate_dataset(name, config):

    path = os.path.join(
        GOLD_DIR, config["file"]
    )

    print(f"\nChecking: {name}")

    # Check file existence
    if not os.path.exists(path):

        print("STATUS: FAILED")
        print(" - File missing")

        return False

    df = pd.read_csv(path)

    errors = []

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # Check empty dataset
    if df.empty:
        errors.append("Dataset is empty")

    # Check required columns
    keys = config["keys"]

    missing_columns = [
        col for col in keys
        if col not in df.columns
    ]

    if missing_columns:

        errors.append(
            f"Missing columns: {missing_columns}"
        )

        print("STATUS: FAILED")

        for error in errors:
            print(" -", error)

        return False

    # Check missing key values
    missing_keys = df[keys].isnull().any(axis=1).sum()

    if missing_keys:
        errors.append(
            f"{missing_keys} rows have missing keys"
        )

    # Check duplicate key combinations
    duplicates = df.duplicated(
        subset=keys
    ).sum()

    if duplicates:
        errors.append(
            f"{duplicates} duplicate key records"
        )

    print("Missing key rows:", missing_keys)
    print("Duplicate key records:", duplicates)

    # Final dataset result
    if errors:

        print("STATUS: FAILED")

        for error in errors:
            print(" -", error)

        return False

    print("STATUS: PASSED")

    return True


# ==========================================
# 4. RUN COMPLETE GOLD AUDIT
# ==========================================

def validate_gold():

    print("\n========== GOLD LAYER VALIDATION ==========")

    passed = 0
    failed = 0

    # Validate all Gold datasets
    for name, config in DATASETS.items():

        try:

            if validate_dataset(name, config):
                passed += 1

            else:
                failed += 1

        except Exception as error:

            print(f"FAILED: {name} | {error}")

            failed += 1

    # Final audit summary
    print("\n========== FINAL GOLD AUDIT ==========")

    print("Passed:", passed)
    print("Failed:", failed)
    print("Total checks:", passed + failed)

    if failed:

        raise ValueError(
            "Gold validation failed! "
            "Fix data quality issues before analysis."
        )

    print("\nALL GOLD DATASETS PASSED!")
    print("Gold layer is ready for analysis.")


# ==========================================
# 5. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    validate_gold()
