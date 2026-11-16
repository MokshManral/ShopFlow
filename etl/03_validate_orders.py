
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    PROJECT_DIR
    / "data"
    / "silver"
    / "orders"
    / "orders_cleaned.csv"
)

df = pd.read_csv(FILE_PATH)

print("========== VALIDATION REPORT ==========")

# 1. Total records
print("Total orders:", len(df))

# 2. Check duplicate order IDs
print(
    "Duplicate order IDs:",
    df["order_id"].duplicated().sum()
)

# 3. Check missing order IDs
print(
    "Missing order IDs:",
    df["order_id"].isnull().sum()
)

# 4. Check order status distribution
print("\nOrder status distribution:")
print(df["order_status"].value_counts(dropna=False))

# 5. Check date columns
print("\nMissing date values:")
print(df.isnull().sum())

# 6. Final result
if (
    df["order_id"].isnull().sum() == 0
    and df["order_id"].duplicated().sum() == 0
):
    print("\nVALIDATION PASSED!")
else:
    print("\nVALIDATION FAILED!")