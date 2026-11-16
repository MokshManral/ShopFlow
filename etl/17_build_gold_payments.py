
import pandas as pd
from pathlib import Path

# 1. Define directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold" / "payments"

GOLD_DIR.mkdir(parents=True, exist_ok=True)

# 2. Load payments
payments = pd.read_csv(
    SILVER_DIR / "payments" / "payments_cleaned.csv"
)

print("Payments dataset loaded!")
print("Raw shape:", payments.shape)

# 3. Create payment method analytics
method_analytics = (
    payments.groupby("payment_type")
    .agg(
        total_transactions=("payment_sequential", "count"),
        unique_orders=("order_id", "nunique"),
        total_payment_value=("payment_value", "sum"),
        average_payment_value=("payment_value", "mean"),
        average_installments=("payment_installments", "mean")
    )
    .reset_index()
)

# 4. Calculate payment method percentage
total_transactions = method_analytics["total_transactions"].sum()

method_analytics["transaction_percentage"] = (
    method_analytics["total_transactions"] /
    total_transactions * 100
)

# 5. Sort by payment value
method_analytics = method_analytics.sort_values(
    by="total_payment_value",
    ascending=False
)

# 6. Validate results
print("\n========== PAYMENT VALIDATION ==========")

print("Total transactions:", len(payments))
print("Payment methods:", payments["payment_type"].nunique())

if payments["payment_value"].isna().any():
    raise ValueError("Missing payment values found!")

if (payments["payment_value"] < 0).any():
    raise ValueError("Negative payment values found!")

# 7. Display analytics
print("\n========== PAYMENT ANALYTICS ==========")

print(
    "Total payment value:",
    round(payments["payment_value"].sum(), 2)
)

print(
    "Average payment value:",
    round(payments["payment_value"].mean(), 2)
)

print("\nPayment method breakdown:")

print(
    method_analytics.to_string(index=False)
)

# 8. Save results
output_file = GOLD_DIR / "gold_payment_analytics.csv"

method_analytics.to_csv(output_file, index=False)

print("\nPayment analytics created successfully!")
print("Final shape:", method_analytics.shape)
print("Saved to:", output_file)
