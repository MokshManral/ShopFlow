import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "sellers"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load seller data
input_file = RAW_DIR / "olist_sellers_dataset.csv"
df = pd.read_csv(input_file)

print("Raw sellers:", df.shape)

# 4. Remove exact duplicates
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check seller IDs
if df["seller_id"].isnull().any():
    raise ValueError("Missing seller IDs found!")

if df["seller_id"].duplicated().any():
    raise ValueError("Duplicate seller IDs found!")

# 7. Standardize text fields
df["seller_city"] = (
    df["seller_city"].str.strip().str.lower()
)

df["seller_state"] = (
    df["seller_state"].str.strip().str.upper()
)

# 8. Keep ZIP prefix as text
df["seller_zip_code_prefix"] = (
    df["seller_zip_code_prefix"].astype("string")
)

# 9. Print seller statistics
print("\nUnique sellers:", df["seller_id"].nunique())

print("Seller cities:", df["seller_city"].nunique())

print("Seller states:", df["seller_state"].nunique())

print("\nMissing values:")
print(df.isnull().sum())

# 10. Save cleaned data
output_file = SILVER_DIR / "sellers_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nSeller transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)