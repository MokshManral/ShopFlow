
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold" / "cities"

GOLD.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD SILVER DATA
# --------------------------------------------------

orders = pd.read_csv(
    SILVER / "orders" / "orders_cleaned.csv",
    parse_dates=["order_purchase_timestamp"]
)

customers = pd.read_csv(
    SILVER / "customers" / "customers_cleaned.csv"
)

items = pd.read_csv(
    SILVER / "order_items" / "order_items_cleaned.csv"
)

print("All datasets loaded successfully!")


# --------------------------------------------------
# 3. AGGREGATE ITEMS AT ORDER LEVEL
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
# 4. JOIN ORDERS WITH CUSTOMERS
# --------------------------------------------------

city_orders = orders.merge(
    customers[
        ["customer_id", "customer_city", "customer_state",
         "customer_unique_id"]
    ],
    on="customer_id",
    how="left",
    validate="many_to_one"
)

city_orders = city_orders.merge(
    order_items,
    on="order_id",
    how="left",
    validate="one_to_one"
)

city_orders["item_revenue"] = city_orders["item_revenue"].fillna(0)
city_orders["freight_value"] = city_orders["freight_value"].fillna(0)
city_orders["total_items"] = city_orders["total_items"].fillna(0)


# --------------------------------------------------
# 5. VALIDATE CITY DATA
# --------------------------------------------------

if city_orders["customer_city"].isna().any():
    raise ValueError("Some orders have missing customer cities!")

if city_orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order IDs found after joining!")


# --------------------------------------------------
# 6. BUILD CITY ANALYTICS
# --------------------------------------------------

city_analytics = (
    city_orders.groupby(
        ["customer_city", "customer_state"]
    )
    .agg(
        total_orders=("order_id", "nunique"),
        unique_customers=("customer_unique_id", "nunique"),
        delivered_orders=(
            "order_status",
            lambda x: (x == "delivered").sum()
        ),
        canceled_orders=(
            "order_status",
            lambda x: (x == "canceled").sum()
        ),
        total_items=("total_items", "sum"),
        total_revenue=("item_revenue", "sum"),
        total_freight=("freight_value", "sum")
    )
    .reset_index()
)


# --------------------------------------------------
# 7. CALCULATE BUSINESS METRICS
# --------------------------------------------------

city_analytics["average_order_value"] = (
    city_analytics["total_revenue"]
    / city_analytics["total_orders"]
)

city_analytics["delivery_rate"] = (
    city_analytics["delivered_orders"]
    / city_analytics["total_orders"]
) * 100

city_analytics["cancellation_rate"] = (
    city_analytics["canceled_orders"]
    / city_analytics["total_orders"]
) * 100

city_analytics = city_analytics.sort_values(
    by="total_revenue",
    ascending=False
)


# --------------------------------------------------
# 8. FINAL VALIDATION
# --------------------------------------------------

print("\n========== CITY ANALYTICS VALIDATION ==========")

print("Total cities:", len(city_analytics))

print(
    "Duplicate city-state combinations:",
    city_analytics.duplicated(
        ["customer_city", "customer_state"]
    ).sum()
)

print(
    "Total orders across cities:",
    city_analytics["total_orders"].sum()
)

print(
    "Total city revenue:",
    round(city_analytics["total_revenue"].sum(), 2)
)

print("\nTop 10 cities by revenue:")

print(
    city_analytics[
        [
            "customer_city",
            "customer_state",
            "total_orders",
            "unique_customers",
            "total_revenue",
            "delivery_rate"
        ]
    ].head(10).to_string(index=False)
)


# --------------------------------------------------
# 9. SAVE GOLD DATA
# --------------------------------------------------

output_path = GOLD / "gold_city_analytics.csv"

city_analytics.to_csv(output_path, index=False)

print("\nCity analytics created successfully!")
print("Final shape:", city_analytics.shape)
print("Saved to:", output_path)
