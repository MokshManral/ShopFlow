
import os
import pandas as pd

# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_DIR = os.path.join(ROOT, "data", "silver")


# ==========================================
# 2. DATASET CONFIGURATION
# ==========================================

DATASETS = {
    "orders": {
        "file": "orders/orders_cleaned.csv",
        "keys": ["order_id"],
        "required": [
            "order_id", "customer_id", "order_status",
            "order_purchase_timestamp"
        ]
    },

    "order_items": {
        "file": "order_items/order_items_cleaned.csv",
        "keys": ["order_id", "order_item_id"],
        "required": [
            "order_id", "order_item_id", "product_id",
            "seller_id", "price", "freight_value"
        ]
    },

    "payments": {
        "file": "payments/payments_cleaned.csv",
        "keys": ["order_id", "payment_sequential"],
        "required": [
            "order_id", "payment_sequential",
            "payment_type", "payment_value"
        ]
    },

    "customers": {
        "file": "customers/customers_cleaned.csv",
        "keys": ["customer_id"],
        "required": [
            "customer_id", "customer_unique_id",
            "customer_city", "customer_state"
        ]
    },

    "products": {
        "file": "products/products_cleaned.csv",
        "keys": ["product_id"],
        "required": ["product_id", "product_category_name"]
    },

    "sellers": {
        "file": "sellers/sellers_cleaned.csv",
        "keys": ["seller_id"],
        "required": [
            "seller_id", "seller_city", "seller_state"
        ]
    },

    "reviews": {
        "file": "reviews/reviews_cleaned.csv",
        "keys": ["review_id", "order_id"],
        "required": [
            "review_id", "order_id", "review_score"
        ]
    },

    "geolocation": {
        "file": "geolocation/geolocation_cleaned.csv",
        "keys": [],
        "required": [
            "geolocation_zip_code_prefix",
            "geolocation_lat", "geolocation_lng"
        ]
    },

    "category_translation": {
        "file": "category_translation/category_translation_cleaned.csv",
        "keys": ["product_category_name"],
        "required": [
            "product_category_name",
            "product_category_name_english"
        ]
    }
}


# ==========================================
# 3. VALIDATION FUNCTION
# ==========================================

def validate_dataset(name, config):

    path = os.path.join(SILVER_DIR, config["file"])

    print(f"\nChecking: {name}")

    # Check file existence
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing Silver file: {path}")

    df = pd.read_csv(path)

    errors = []

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # Check empty dataset
    if df.empty:
        errors.append("Dataset is empty")

    # Check required columns
    missing_columns = [
        col for col in config["required"]
        if col not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        print("FAILED:", errors)
        return False

    # Check missing key values
    keys = config["keys"]

    if keys:
        missing_keys = df[keys].isnull().any(axis=1).sum()

        if missing_keys:
            errors.append(f"{missing_keys} rows have missing keys")

        # Check duplicate key combinations
        duplicates = df.duplicated(subset=keys).sum()

        if duplicates:
            errors.append(f"{duplicates} duplicate key records")

        print("Missing key rows:", missing_keys)
        print("Duplicate key records:", duplicates)

    # Numeric quality checks
    numeric_columns = {
        "order_items": ["price", "freight_value"],
        "payments": [
            "payment_sequential",
            "payment_installments",
            "payment_value"
        ],
        "products": [
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
        ],
        "reviews": ["review_score"],
        "geolocation": [
            "geolocation_lat",
            "geolocation_lng"
        ]
    }

    for col in numeric_columns.get(name, []):

        values = pd.to_numeric(df[col], errors="coerce")

        invalid = (df[col].notna() & values.isna()).sum()

        if invalid:
            errors.append(f"{col}: {invalid} invalid numeric values")

        if col in ["price", "freight_value", "payment_value"]:
            negative = (values < 0).sum()

            if negative:
                errors.append(f"{col}: {negative} negative values")

    # Review score validation
    if name == "reviews":

        invalid_scores = ~df["review_score"].between(1, 5)

        if invalid_scores.any():
            errors.append(
                f"{invalid_scores.sum()} invalid review scores"
            )

    # Geolocation validation
    if name == "geolocation":

        lat = pd.to_numeric(df["geolocation_lat"], errors="coerce")
        lng = pd.to_numeric(df["geolocation_lng"], errors="coerce")

        if ((lat < -90) | (lat > 90)).any():
            errors.append("Invalid latitude values")

        if ((lng < -180) | (lng > 180)).any():
            errors.append("Invalid longitude values")

    # Final dataset result
    if errors:
        print("STATUS: FAILED")

        for error in errors:
            print(" -", error)

        return False

    print("STATUS: PASSED")

    return True


# ==========================================
# 4. REFERENTIAL INTEGRITY
# ==========================================

def validate_relationships():

    print("\n========== RELATIONSHIP VALIDATION ==========")

    def load(folder, filename):
        path = os.path.join(SILVER_DIR, folder, filename)
        return pd.read_csv(path)

    orders = load("orders", "orders_cleaned.csv")
    items = load("order_items", "order_items_cleaned.csv")
    payments = load("payments", "payments_cleaned.csv")
    reviews = load("reviews", "reviews_cleaned.csv")
    customers = load("customers", "customers_cleaned.csv")
    products = load("products", "products_cleaned.csv")
    sellers = load("sellers", "sellers_cleaned.csv")

    relationships = [
        ("Order items → Orders", items, "order_id", orders, "order_id"),
        ("Payments → Orders", payments, "order_id", orders, "order_id"),
        ("Reviews → Orders", reviews, "order_id", orders, "order_id"),
        ("Orders → Customers", orders, "customer_id", customers, "customer_id"),
        ("Order items → Products", items, "product_id", products, "product_id"),
        ("Order items → Sellers", items, "seller_id", sellers, "seller_id")
    ]

    failed = False

    for label, child, child_col, parent, parent_col in relationships:

        missing = (
            ~child[child_col].isin(parent[parent_col])
        ).sum()

        if missing:
            print(f"FAILED: {label} | Unmatched records: {missing}")
            failed = True
        else:
            print(f"PASSED: {label}")

    return not failed


# ==========================================
# 5. RUN COMPLETE SILVER AUDIT
# ==========================================

def validate_silver():

    print("\n========== SILVER LAYER QUALITY AUDIT ==========")

    passed = 0
    failed = 0

    for name, config in DATASETS.items():

        try:
            if validate_dataset(name, config):
                passed += 1
            else:
                failed += 1

        except Exception as error:
            print(f"FAILED: {name} | {error}")
            failed += 1

    # Run relationship checks only if all files exist
    if failed == 0:

        if validate_relationships():
            passed += 1
        else:
            failed += 1

    # Final summary
    print("\n========== FINAL SILVER AUDIT ==========")
    print("Passed:", passed)
    print("Failed:", failed)
    print("Total checks:", passed + failed)

    if failed:
        raise ValueError(
            "Silver validation failed! Fix data quality issues before Gold."
        )

    print("\nALL SILVER DATASETS PASSED!")
    print("Silver layer is ready for Gold creation.")


if __name__ == "__main__":
    validate_silver()
