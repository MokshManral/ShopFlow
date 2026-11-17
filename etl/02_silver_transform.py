
import importlib.util
import os
import pandas as pd

# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SILVER_DIR = os.path.join(ROOT, "data", "silver")

# Automatically create Silver directory and subdirectories
SILVER_FOLDERS = [
    "orders",
    "order_items",
    "payments",
    "customers",
    "products",
    "sellers",
    "reviews",
    "geolocation",
    "category_translation"
]

for folder in SILVER_FOLDERS:
    os.makedirs(os.path.join(SILVER_DIR, folder), exist_ok=True)

print("Silver folder structure created successfully!")


# ==========================================
# 2. COMMON FUNCTIONS
# ==========================================

def check_columns(df, columns):
    missing = [col for col in columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")


def save_silver(df, folder, filename):

    output_dir = os.path.join(SILVER_DIR, folder)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, filename)

    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file} | Shape: {df.shape}")


# ==========================================
# 3. TRANSFORM ORDERS
# ==========================================

def transform_orders(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])

    if df["order_id"].isnull().any():
        raise ValueError("Missing order IDs!")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs!")

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    save_silver(df, "orders", "orders_cleaned.csv")


# ==========================================
# 4. TRANSFORM ORDER ITEMS
# ==========================================

def transform_order_items(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "price",
        "freight_value",
        "shipping_limit_date"
    ])

    keys = ["order_id", "order_item_id", "product_id", "seller_id"]

    if df[keys].isnull().any().any():
        raise ValueError("Missing order item key values!")

    if df.duplicated(["order_id", "order_item_id"]).any():
        raise ValueError("Duplicate order item records!")

    for col in ["price", "freight_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"], errors="coerce"
    )

    print("Negative prices:", (df["price"] < 0).sum())
    print("Negative freight:", (df["freight_value"] < 0).sum())

    save_silver(df, "order_items", "order_items_cleaned.csv")


# ==========================================
# 5. TRANSFORM PAYMENTS
# ==========================================

def transform_payments(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ])

    keys = ["order_id", "payment_sequential"]

    if df[keys].isnull().any().any():
        raise ValueError("Missing payment key values!")

    if df.duplicated(keys).any():
        raise ValueError("Duplicate payment records!")

    for col in [
        "payment_sequential",
        "payment_installments",
        "payment_value"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("Negative payments:", (df["payment_value"] < 0).sum())
    print("Payment types:")
    print(df["payment_type"].value_counts(dropna=False))

    print("Total payment value:", round(df["payment_value"].sum(), 2))

    save_silver(df, "payments", "payments_cleaned.csv")


# ==========================================
# 6. TRANSFORM CUSTOMERS
# ==========================================

def transform_customers(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ])

    keys = ["customer_id", "customer_unique_id"]

    if df[keys].isnull().any().any():
        raise ValueError("Missing customer identifiers!")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs!")

    df["customer_city"] = (
        df["customer_city"].str.strip().str.lower()
    )

    df["customer_state"] = (
        df["customer_state"].str.strip().str.upper()
    )

    df["customer_zip_code_prefix"] = (
        df["customer_zip_code_prefix"].astype("string")
    )

    print("Unique customers:", df["customer_unique_id"].nunique())
    print("Customer states:", df["customer_state"].nunique())

    save_silver(df, "customers", "customers_cleaned.csv")


# ==========================================
# 7. TRANSFORM PRODUCTS
# ==========================================

def transform_products(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ])

    if df["product_id"].isnull().any():
        raise ValueError("Missing product IDs!")

    if df["product_id"].duplicated().any():
        raise ValueError("Duplicate product IDs!")

    df["product_category_name"] = (
        df["product_category_name"].str.strip().str.lower()
    )

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]:
        print(f"Negative {col}:", (df[col] < 0).sum())

    save_silver(df, "products", "products_cleaned.csv")


# ==========================================
# 8. TRANSFORM SELLERS
# ==========================================

def transform_sellers(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ])

    if df["seller_id"].isnull().any():
        raise ValueError("Missing seller IDs!")

    if df["seller_id"].duplicated().any():
        raise ValueError("Duplicate seller IDs!")

    df["seller_city"] = (
        df["seller_city"].str.strip().str.lower()
    )

    df["seller_state"] = (
        df["seller_state"].str.strip().str.upper()
    )

    df["seller_zip_code_prefix"] = (
        df["seller_zip_code_prefix"].astype("string")
    )

    print("Unique sellers:", df["seller_id"].nunique())

    save_silver(df, "sellers", "sellers_cleaned.csv")


# ==========================================
# 9. TRANSFORM REVIEWS
# ==========================================

def transform_reviews(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
        "review_comment_title",
        "review_comment_message"
    ])

    if df["review_id"].isnull().any():
        raise ValueError("Missing review IDs!")

    if df["order_id"].isnull().any():
        raise ValueError("Missing review order IDs!")

    if df.duplicated(["review_id", "order_id"]).any():
        raise ValueError("Duplicate review-order combinations!")

    df["review_score"] = pd.to_numeric(
        df["review_score"], errors="coerce"
    )

    invalid_scores = ~df["review_score"].between(1, 5)

    print("Invalid review scores:", invalid_scores.sum())

    for col in ["review_creation_date", "review_answer_timestamp"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["review_comment_title", "review_comment_message"]:
        df[col] = df[col].str.strip()

    print("Unique reviews:", df["review_id"].nunique())
    print("Orders reviewed:", df["order_id"].nunique())

    save_silver(df, "reviews", "reviews_cleaned.csv")


# ==========================================
# 10. TRANSFORM GEOLOCATION
# ==========================================

def transform_geolocation(df):

    df = df.drop_duplicates().copy()

    check_columns(df, [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ])

    df["geolocation_zip_code_prefix"] = (
        df["geolocation_zip_code_prefix"].astype("string")
    )

    for col in ["geolocation_lat", "geolocation_lng"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["geolocation_city"] = (
        df["geolocation_city"].str.strip().str.lower()
    )

    df["geolocation_state"] = (
        df["geolocation_state"].str.strip().str.upper()
    )

    print(
        "Invalid latitude:",
        (~df["geolocation_lat"].between(-90, 90)).sum()
    )

    print(
        "Invalid longitude:",
        (~df["geolocation_lng"].between(-180, 180)).sum()
    )

    print(
        "Unique ZIP prefixes:",
        df["geolocation_zip_code_prefix"].nunique()
    )

    save_silver(df, "geolocation", "geolocation_cleaned.csv")


# ==========================================
# 11. TRANSFORM CATEGORY TRANSLATION
# ==========================================

def transform_category_translation(df):

    df = df.drop_duplicates().copy()

    columns = [
        "product_category_name",
        "product_category_name_english"
    ]

    check_columns(df, columns)

    if df["product_category_name"].isnull().any():
        raise ValueError("Missing original category names!")

    for col in columns:
        df[col] = df[col].str.strip().str.lower()

    conflicts = (
        df.groupby("product_category_name")[
            "product_category_name_english"
        ].nunique()
    )

    if (conflicts > 1).any():
        raise ValueError("Conflicting category translations!")

    df = df.drop_duplicates(subset=["product_category_name"])

    print("Translated categories:", len(df))

    save_silver(
        df,
        "category_translation",
        "category_translation_cleaned.csv"
    )


# ==========================================
# 12. RUN ALL TRANSFORMATIONS
# ==========================================

def transform_data(datasets):

    print("\n========== SILVER TRANSFORMATION ==========\n")

    transformations = {
        "orders": transform_orders,
        "order_items": transform_order_items,
        "order_payments": transform_payments,
        "customers": transform_customers,
        "products": transform_products,
        "sellers": transform_sellers,
        "order_reviews": transform_reviews,
        "geolocation": transform_geolocation,
        "product_category_name_translation": transform_category_translation
    }

    for name, function in transformations.items():

        print(f"\nTransforming: {name}")

        if name not in datasets:
            raise KeyError(f"Dataset not found: {name}")

        function(datasets[name])

    print("\nAll Silver transformations completed successfully!")


if __name__ == "__main__":
    extract_path = os.path.join(os.path.dirname(__file__), "01_extract.py")
    spec = importlib.util.spec_from_file_location("shopflow_extract", extract_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load extraction script: {extract_path}")

    extract_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extract_module)
    transform_data(extract_module.extract_data())