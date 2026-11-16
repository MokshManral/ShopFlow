import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
SILVER_DIR = PROJECT_DIR / "data" / "silver" / "payments"

# 2. Create output directory
SILVER_DIR.mkdir(parents=True, exist_ok=True)

# 3. Load raw payment data
input_file = RAW_DIR / "olist_order_payments_dataset.csv"
df = pd.read_csv(input_file)

print("Raw payments:", df.shape)

# 4. Remove exact duplicate rows
df = df.drop_duplicates()

# 5. Check required columns
required_columns = [
    "order_id",
    "payment_sequential",
    "payment_type",
    "payment_installments",
    "payment_value"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# 6. Check missing key values
key_columns = ["order_id", "payment_sequential"]

if df[key_columns].isnull().any().any():
    raise ValueError("Missing payment key values found!")

# 7. Check payment record uniqueness
if df.duplicated(
    subset=["order_id", "payment_sequential"]
).any():
    raise ValueError("Duplicate payment records found!")

# 8. Convert numeric columns
df["payment_sequential"] = pd.to_numeric(
    df["payment_sequential"], errors="coerce"
)

df["payment_installments"] = pd.to_numeric(
    df["payment_installments"], errors="coerce"
)

df["payment_value"] = pd.to_numeric(
    df["payment_value"], errors="coerce"
)

# 9. Check suspicious values
print("\nMissing values:")
print(df.isnull().sum())

print(
    "\nNegative payment values:",
    (df["payment_value"] < 0).sum()
)

print(
    "\nPayment types:",
    df["payment_type"].value_counts(dropna=False)
)

# 10. Save cleaned payment data
output_file = SILVER_DIR / "payments_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nPayment transformation completed!")
print("Final shape:", df.shape)
print("Saved to:", output_file)

# 11. Calculate total payment value
print(
    "\nTotal payment value:",
    round(df["payment_value"].sum(), 2)
)
