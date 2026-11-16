
import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "category_translation"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load category translation data
input_file = RAW_DIR / "product_category_name_translation.csv"
df = pd.read_csv(input_file)

print("Raw category translation data:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

print("After removing exact duplicates:", df.shape)

# 5. Check required columns
required_columns = [
    "product_category_name",
    "product_category_name_english"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check missing category names
print("\nMissing values:")
print(df[required_columns].isnull().sum())

if df["product_category_name"].isnull().any():
    raise ValueError("Missing original category names found!")

# 7. Standardize category names
for column in required_columns:
    df[column] = (
        df[column]
        .str.strip()
        .str.lower()
    )

# 8. Check duplicate original category names
duplicate_categories = df[
    df.duplicated(
        subset=["product_category_name"],
        keep=False
    )
]

print(
    "\nDuplicate original category records:",
    len(duplicate_categories)
)

# 9. Check for conflicting translations
conflicting_categories = (
    df.groupby("product_category_name")[
        "product_category_name_english"
    ]
    .nunique()
)

conflicting_categories = conflicting_categories[
    conflicting_categories > 1
]

if not conflicting_categories.empty:
    raise ValueError(
        "Some original categories have multiple English translations!"
    )

# 10. Remove repeated mappings
df = df.drop_duplicates(
    subset=["product_category_name"]
)

# 11. Display translation statistics
print("\nTotal translated categories:", len(df))

print(
    "Unique original categories:",
    df["product_category_name"].nunique()
)

print(
    "Unique English categories:",
    df["product_category_name_english"].nunique()
)

print("\nSample translations:")
print(df.head(10))

# 12. Save cleaned data
output_file = SILVER_DIR / "category_translation_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nCategory translation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)
