import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "orders"

# 2. Create the Silver output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load the raw orders dataset
input_file = RAW_DIR / "olist_orders_dataset.csv"
df = pd.read_csv(input_file)

print("Raw data loaded:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check for missing order IDs
if df["order_id"].isnull().any():
    raise ValueError("Missing order IDs found!")

# 6. Check order ID uniqueness
if df["order_id"].duplicated().any():
    raise ValueError("Duplicate order IDs found!")

# 7. Convert date columns to datetime
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )

# 8. Save the cleaned dataset
output_file = SILVER_DIR / "orders_cleaned.csv"
df.to_csv(output_file, index=False)

print("\nTransformation completed!")
print("Cleaned data shape:", df.shape)
print("Saved to:", output_file)
print("\nFinal data types:")
print(df.dtypes)
