
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold" / "daily_sales"

GOLD.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

orders = pd.read_csv(
    SILVER / "orders" / "orders_cleaned.csv",
    parse_dates=["order_purchase_timestamp"]
)

items = pd.read_csv(
    SILVER / "order_items" / "order_items_cleaned.csv"
)

print("Datasets loaded successfully!")


# --------------------------------------------------
# 3. VALIDATE REQUIRED DATA
# --------------------------------------------------

if orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order IDs found!")

if orders["order_purchase_timestamp"].isna().any():
    raise ValueError("Missing purchase timestamps found!")


# --------------------------------------------------
# 4. AGGREGATE ITEMS BY ORDER
# --------------------------------------------------

items["price"] = pd.to_numeric(items["price"], errors="coerce")
items["freight_value"] = pd.to_numeric(
    items["freight_value"], errors="coerce"
)

order_items = (
    items.groupby("order_id")
    .agg(
        item_revenue=("price", "sum"),
        freight_value=("freight_value", "sum"),
        total_items=("order_item_id", "count")
    )
    .reset_index()
)


# --------------------------------------------------
# 5. JOIN ITEMS WITH ORDERS
# --------------------------------------------------

sales = orders.merge(
    order_items,
    on="order_id",
    how="left",
    validate="one_to_one"
)

sales["item_revenue"] = sales["item_revenue"].fillna(0)
sales["freight_value"] = sales["freight_value"].fillna(0)
sales["total_items"] = sales["total_items"].fillna(0)

sales["order_date"] = (
    sales["order_purchase_timestamp"].dt.date
)


# --------------------------------------------------
# 6. CREATE REVENUE METRICS
# --------------------------------------------------

sales["delivered_revenue"] = sales["item_revenue"].where(
    sales["order_status"] == "delivered",
    0
)


# --------------------------------------------------
# 7. BUILD DAILY ANALYTICS
# --------------------------------------------------

daily_sales = (
    sales.groupby("order_date")
    .agg(
        total_orders=("order_id", "nunique"),
        delivered_orders=(
            "order_status",
            lambda x: (x == "delivered").sum()
        ),
        canceled_orders=(
            "order_status",
            lambda x: (x == "canceled").sum()
        ),
        total_items=("total_items", "sum"),
        total_item_value=("item_revenue", "sum"),
        delivered_revenue=("delivered_revenue", "sum"),
        total_freight=("freight_value", "sum")
    )
    .reset_index()
)


# --------------------------------------------------
# 8. CALCULATE DAILY METRICS
# --------------------------------------------------

daily_sales["average_order_value"] = (
    daily_sales["delivered_revenue"]
    / daily_sales["delivered_orders"].replace(0, pd.NA)
).fillna(0).infer_objects(copy=False)

daily_sales["delivery_rate"] = (
    daily_sales["delivered_orders"]
    / daily_sales["total_orders"]
) * 100

daily_sales["cancellation_rate"] = (
    daily_sales["canceled_orders"]
    / daily_sales["total_orders"]
) * 100

daily_sales = daily_sales.sort_values("order_date")


# --------------------------------------------------
# 9. FINAL VALIDATION
# --------------------------------------------------

print("\n========== DAILY SALES VALIDATION ==========")

print("Total days:", len(daily_sales))

print(
    "Total orders:",
    daily_sales["total_orders"].sum()
)

print(
    "Total delivered revenue:",
    round(daily_sales["delivered_revenue"].sum(), 2)
)

print(
    "Total item value:",
    round(daily_sales["total_item_value"].sum(), 2)
)

print("\nFirst 5 days:")
print(daily_sales.head().to_string(index=False))

print("\nLast 5 days:")
print(daily_sales.tail().to_string(index=False))


# --------------------------------------------------
# 10. SAVE GOLD TABLE
# --------------------------------------------------

output_path = GOLD / "gold_daily_sales.csv"

daily_sales.to_csv(output_path, index=False)

print("\nDaily sales analytics created successfully!")
print("Final shape:", daily_sales.shape)
print("Saved to:", output_path)
