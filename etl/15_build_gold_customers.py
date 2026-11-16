
import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold" / "customers"

GOLD_DIR.mkdir(parents=True, exist_ok=True)

# 2. Load cleaned datasets
orders = pd.read_csv(
    SILVER_DIR / "orders" / "orders_cleaned.csv"
)

customers = pd.read_csv(
    SILVER_DIR / "customers" / "customers_cleaned.csv"
)

payments = pd.read_csv(
    SILVER_DIR / "payments" / "payments_cleaned.csv"
)

print("All datasets loaded successfully!")

# 3. Aggregate payments by order
payments_agg = (
    payments.groupby("order_id")
    .agg(
        order_payment=("payment_value", "sum")
    )
    .reset_index()
)

# 4. Join orders with customer information
customer_orders = orders.merge(
    customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state"
        ]
    ],
    on="customer_id",
    how="left",
    validate="one_to_one"
)

# 5. Join aggregated payment information
customer_orders = customer_orders.merge(
    payments_agg,
    on="order_id",
    how="left",
    validate="one_to_one"
)

# 6. Handle orders without payment records
customer_orders["order_payment"] = (
    customer_orders["order_payment"].fillna(0)
)

# 7. Convert purchase timestamp
customer_orders["order_purchase_timestamp"] = pd.to_datetime(
    customer_orders["order_purchase_timestamp"],
    errors="coerce"
)

# 8. Build customer-level analytics
gold = (
    customer_orders.groupby("customer_unique_id")
    .agg(
        customer_city=("customer_city", "first"),
        customer_state=("customer_state", "first"),
        total_orders=("order_id", "nunique"),
        delivered_orders=(
            "order_status",
            lambda x: (x == "delivered").sum()
        ),
        total_payment=("order_payment", "sum"),
        average_order_payment=("order_payment", "mean"),
        first_order_date=("order_purchase_timestamp", "min"),
        latest_order_date=("order_purchase_timestamp", "max")
    )
    .reset_index()
)

# 9. Identify repeat customers
gold["customer_type"] = gold["total_orders"].apply(
    lambda count: "Repeat Customer"
    if count > 1
    else "One-time Customer"
)

# 10. Validate customer table
print("\n========== CUSTOMER TABLE VALIDATION ==========")

print("Total customers:", len(gold))
print(
    "Unique customer IDs:",
    gold["customer_unique_id"].nunique()
)

duplicate_customers = gold["customer_unique_id"].duplicated().sum()

print("Duplicate customer IDs:", duplicate_customers)

if duplicate_customers > 0:
    raise ValueError("Duplicate customer IDs found!")

# 11. Display customer analytics
print("\n========== CUSTOMER ANALYTICS ==========")

print(
    "Total unique customers:",
    len(gold)
)

print(
    "Repeat customers:",
    (gold["total_orders"] > 1).sum()
)

print(
    "One-time customers:",
    (gold["total_orders"] == 1).sum()
)

print(
    "Total recorded customer payments:",
    round(gold["total_payment"].sum(), 2)
)

print("\nCustomer type distribution:")
print(gold["customer_type"].value_counts())

print("\nTop 10 customers by payment:")
print(
    gold.sort_values(
        "total_payment",
        ascending=False
    )[
        [
            "customer_unique_id",
            "total_orders",
            "total_payment",
            "customer_city",
            "customer_state"
        ]
    ].head(10).to_string(index=False)
)

# 12. Save Gold table
output_file = GOLD_DIR / "gold_customer_analytics.csv"

gold.to_csv(output_file, index=False)

print("\nCustomer analytics table created successfully!")
print("Final shape:", gold.shape)
print("Saved to:", output_file)