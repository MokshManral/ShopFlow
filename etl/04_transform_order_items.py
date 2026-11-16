import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "order_items"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load raw order items
input_file = RAW_DIR / "olist_order_items_dataset.csv"
df = pd.read_csv(input_file)

print("Raw order items:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "price",
    "freight_value"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check missing key values
key_columns = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id"
]

if df[key_columns].isnull().any().any():
    raise ValueError("Missing values found in key columns")

# 7. Check item-level uniqueness
if df.duplicated(
    subset=["order_id", "order_item_id"]
).any():
    raise ValueError("Duplicate order item records found")

# 8. Convert numeric columns
df["price"] = pd.to_numeric(
    df["price"], errors="coerce"
)

df["freight_value"] = pd.to_numeric(
    df["freight_value"], errors="coerce"
)

# 9. Convert shipping date
df["shipping_limit_date"] = pd.to_datetime(
    df["shipping_limit_date"],
    errors="coerce"
)

# 10. Display data quality checks
print("\nMissing values:")
print(df.isnull().sum())

print("\nNegative price records:", (df["price"] < 0).sum())
print("Negative freight records:", (df["freight_value"] < 0).sum())

# 11. Save cleaned dataset
output_file = SILVER_DIR / "order_items_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nTransformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)
