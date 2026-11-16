
import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "reviews"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load review data
input_file = RAW_DIR / "olist_order_reviews_dataset.csv"
df = pd.read_csv(input_file)

print("Raw reviews:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "review_id",
    "order_id",
    "review_score",
    "review_creation_date",
    "review_answer_timestamp"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Validate review IDs
if df["review_id"].isnull().any():
    raise ValueError("Missing review IDs found!")

# 7. Validate review and order combination
duplicate_pairs = df[
    df.duplicated(
        subset=["review_id", "order_id"],
        keep=False
    )
]

print(
    "\nDuplicate review_id + order_id pairs:",
    len(duplicate_pairs)
)

if not duplicate_pairs.empty:
    raise ValueError(
        "Duplicate review and order combinations found!"
    )

print("Review key validation passed!")

# 8. Convert review score to numeric
df["review_score"] = pd.to_numeric(
    df["review_score"],
    errors="coerce"
)

# 9. Check review score range
invalid_scores = df[
    ~df["review_score"].between(1, 5)
]

print("\nInvalid review scores:", len(invalid_scores))

# 10. Convert date columns
date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )

# 11. Clean review text without changing missing values
text_columns = [
    "review_comment_title",
    "review_comment_message"
]

for column in text_columns:
    df[column] = df[column].str.strip()

# 12. Display review statistics
print("\nReview score distribution:")
print(df["review_score"].value_counts().sort_index())

print("\nMissing values:")
print(df.isnull().sum())

print("\nUnique review IDs:", df["review_id"].nunique())
print("Unique orders reviewed:", df["order_id"].nunique())

# 13. Save cleaned data
output_file = SILVER_DIR / "reviews_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nReview transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)