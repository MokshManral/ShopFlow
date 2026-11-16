import pandas as pd
from pathlib import Path

# 1. Define directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "customers"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load customer dataset
input_file = RAW_DIR / "olist_customers_dataset.csv"
df = pd.read_csv(input_file)

print("Raw customers:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check missing customer identifiers
key_columns = [
    "customer_id",
    "customer_unique_id"
]

if df[key_columns].isnull().any().any():
    raise ValueError("Missing customer identifiers found!")

# 7. Check customer ID uniqueness
if df["customer_id"].duplicated().any():
    raise ValueError("Duplicate customer IDs found!")

# 8. Standardize text columns
df["customer_city"] = (
    df["customer_city"]
    .str.strip()
    .str.lower()
)

df["customer_state"] = (
    df["customer_state"]
    .str.strip()
    .str.upper()
)

# 9. Keep ZIP prefix as text
df["customer_zip_code_prefix"] = (
    df["customer_zip_code_prefix"].astype("string")
)

# 10. Display customer statistics
print("\nUnique customer records:", df["customer_id"].nunique())

print(
    "Actual unique customers:",
    df["customer_unique_id"].nunique()
)

print(
    "\nCustomer states:",
    df["customer_state"].nunique()
)

print("\nMissing values:")
print(df.isnull().sum())

# 11. Save cleaned customer data
output_file = SILVER_DIR / "customers_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nCustomer transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)