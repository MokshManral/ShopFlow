import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold" / "orders"

GOLD_DIR.mkdir(parents=True, exist_ok=True)

# 2. Load cleaned datasets
orders = pd.read_csv(
    SILVER_DIR / "orders" / "orders_cleaned.csv"
)

items = pd.read_csv(
    SILVER_DIR / "order_items" / "order_items_cleaned.csv"
)

payments = pd.read_csv(
    SILVER_DIR / "payments" / "payments_cleaned.csv"
)

customers = pd.read_csv(
    SILVER_DIR / "customers" / "customers_cleaned.csv"
)

reviews = pd.read_csv(
    SILVER_DIR / "reviews" / "reviews_cleaned.csv"
)

print("All Silver datasets loaded successfully!")

# 3. Aggregate order items by order_id
items_agg = (
    items.groupby("order_id")
    .agg(
        total_items=("order_item_id", "count"),
        item_revenue=("price", "sum"),
        freight_value=("freight_value", "sum")
    )
    .reset_index()
)

# 4. Aggregate payments by order_id
payments_agg = (
    payments.groupby("order_id")
    .agg(
        total_payment=("payment_value", "sum"),
        payment_records=("payment_sequential", "count")
    )
    .reset_index()
)

# 5. Aggregate reviews by order_id
reviews_agg = (
    reviews.groupby("order_id")
    .agg(
        average_review_score=("review_score", "mean"),
        review_count=("review_id", "count")
    )
    .reset_index()
)

# 6. Select customer details
customers_selected = customers[
    [
        "customer_id",
        "customer_city",
        "customer_state"
    ]
].copy()

# 7. Start building the Gold table
gold = orders.copy()

# 8. Join customer information
gold = gold.merge(
    customers_selected,
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# 9. Join aggregated item information
gold = gold.merge(
    items_agg,
    on="order_id",
    how="left",
    validate="one_to_one"
)

# 10. Join aggregated payment information
gold = gold.merge(
    payments_agg,
    on="order_id",
    how="left",
    validate="one_to_one"
)

# 11. Join aggregated review information
gold = gold.merge(
    reviews_agg,
    on="order_id",
    how="left",
    validate="one_to_one"
)

# 12. Fill missing count and amount values
numeric_columns = [
    "total_items",
    "item_revenue",
    "freight_value",
    "total_payment",
    "payment_records",
    "review_count"
]

gold[numeric_columns] = gold[numeric_columns].fillna(0)

# 13. Calculate item value including freight
gold["item_value_with_freight"] = (
    gold["item_revenue"] + gold["freight_value"]
)

# 14. Validate the Gold table
print("\n========== GOLD TABLE VALIDATION ==========")

print("Total rows:", len(gold))
print("Unique orders:", gold["order_id"].nunique())

duplicate_orders = gold["order_id"].duplicated().sum()
print("Duplicate order IDs:", duplicate_orders)

if duplicate_orders > 0:
    raise ValueError("Duplicate orders found in Gold table!")

if len(gold) != len(orders):
    raise ValueError("Gold table row count does not match orders!")

# 15. Display summary statistics
print("\n========== ORDER ANALYTICS ==========")

print("Total item revenue:", round(gold["item_revenue"].sum(), 2))
print("Total freight value:", round(gold["freight_value"].sum(), 2))
print("Total recorded payments:", round(gold["total_payment"].sum(), 2))

print("\nOrder status distribution:")
print(gold["order_status"].value_counts())

print("\nAverage review score:")
print(round(gold["average_review_score"].mean(), 2))

# 16. Save Gold table
output_file = GOLD_DIR / "gold_order_analytics.csv"

gold.to_csv(output_file, index=False)

print("\nGold order analytics table created successfully!")
print("Final shape:", gold.shape)
print("Saved to:", output_file)