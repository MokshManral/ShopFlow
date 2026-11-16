import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "products"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load raw product data
input_file = RAW_DIR / "olist_products_dataset.csv"
df = pd.read_csv(input_file)

print("Raw products:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "product_id",
    "product_category_name",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check product identifiers
if df["product_id"].isnull().any():
    raise ValueError("Missing product IDs found!")

if df["product_id"].duplicated().any():
    raise ValueError("Duplicate product IDs found!")

# 7. Standardize category names
df["product_category_name"] = (
    df["product_category_name"]
    .str.strip()
    .str.lower()
)

# 8. Convert numeric columns
numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# 9. Report missing values
print("\nMissing values:")
print(df.isnull().sum())

# 10. Check suspicious measurements
measurement_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in measurement_columns:
    print(
        f"Negative values in {column}:",
        (df[column] < 0).sum()
    )

# 11. Save cleaned product data
output_file = SILVER_DIR / "products_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nProduct transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)