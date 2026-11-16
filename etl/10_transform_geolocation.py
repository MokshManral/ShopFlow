import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "geolocation"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load geolocation data
input_file = RAW_DIR / "olist_geolocation_dataset.csv"

# Read ZIP prefix as text to preserve leading zeros
df = pd.read_csv(
    input_file,
    dtype={"geolocation_zip_code_prefix": "string"}
)

print("Raw geolocation data:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

print("After removing exact duplicates:", df.shape)

# 5. Check required columns
required_columns = [
    "geolocation_zip_code_prefix",
    "geolocation_lat",
    "geolocation_lng",
    "geolocation_city",
    "geolocation_state"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check missing ZIP-code prefixes
missing_zip = df["geolocation_zip_code_prefix"].isna().sum()

print("\nMissing ZIP-code prefixes:", missing_zip)

# 7. Convert latitude and longitude to numeric
coordinate_columns = [
    "geolocation_lat",
    "geolocation_lng"
]

for column in coordinate_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# 8. Standardize city and state names
df["geolocation_city"] = (
    df["geolocation_city"]
    .str.strip()
    .str.lower()
)

df["geolocation_state"] = (
    df["geolocation_state"]
    .str.strip()
    .str.upper()
)

# 9. Validate coordinate ranges
invalid_latitude = df[
    ~df["geolocation_lat"].between(-90, 90)
]

invalid_longitude = df[
    ~df["geolocation_lng"].between(-180, 180)
]

print("\nInvalid latitude records:", len(invalid_latitude))
print("Invalid longitude records:", len(invalid_longitude))

# 10. Display missing values
print("\nMissing values:")
print(df.isnull().sum())

# 11. Analyze ZIP-code prefixes
print("\nTotal geolocation records:", len(df))

print(
    "Unique ZIP-code prefixes:",
    df["geolocation_zip_code_prefix"].nunique()
)

print(
    "Repeated ZIP-code prefix records:",
    df.duplicated(
        subset=["geolocation_zip_code_prefix"],
        keep=False
    ).sum()
)

# 12. Display coordinate ranges
print("\nLatitude range:")
print(df["geolocation_lat"].min(), "to", df["geolocation_lat"].max())

print("\nLongitude range:")
print(df["geolocation_lng"].min(), "to", df["geolocation_lng"].max())

# 13. Save cleaned data
output_file = SILVER_DIR / "geolocation_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nGeolocation transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)