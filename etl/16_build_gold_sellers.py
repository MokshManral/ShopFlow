
import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold" / "sellers"

GOLD_DIR.mkdir(parents=True, exist_ok=True)

# 2. Load cleaned datasets
items = pd.read_csv(
    SILVER_DIR / "order_items" / "order_items_cleaned.csv"
)

sellers = pd.read_csv(
    SILVER_DIR / "sellers" / "sellers_cleaned.csv"
)

orders = pd.read_csv(
    SILVER_DIR / "orders" / "orders_cleaned.csv"
)

print("All datasets loaded successfully!")

# 3. Join order items with seller information
seller_items = items.merge(
    sellers[
        ["seller_id", "seller_city", "seller_state"]
    ],
    on="seller_id",
    how="left",
    validate="many_to_one"
)

# 4. Join order status information
seller_items = seller_items.merge(
    orders[
        ["order_id", "order_status"]
    ],
    on="order_id",
    how="left",
    validate="many_to_one"
)

# 5. Check missing seller information
if seller_items["seller_city"].isna().any():
    raise ValueError("Some seller records could not be mapped!")

# 6. Identify delivered orders
seller_items["delivered_order_id"] = (
    seller_items["order_id"]
    .where(seller_items["order_status"] == "delivered")
)

# 7. Aggregate data by seller
gold = (
    seller_items.groupby("seller_id")
    .agg(
        seller_city=("seller_city", "first"),
        seller_state=("seller_state", "first"),
        total_order_items=("order_item_id", "count"),
        unique_orders=("order_id", "nunique"),
        unique_products=("product_id", "nunique"),
        product_revenue=("price", "sum"),
        total_freight=("freight_value", "sum"),
        average_item_price=("price", "mean"),
        delivered_orders=("delivered_order_id", "nunique")
    )
    .reset_index()
)

# 8. Calculate delivery percentage
gold["delivered_order_percentage"] = (
    gold["delivered_orders"] /
    gold["unique_orders"] * 100
)

# 9. Sort sellers by revenue
gold = gold.sort_values(
    by="product_revenue",
    ascending=False
)

# 10. Validate seller analytics
print("\n========== SELLER TABLE VALIDATION ==========")

print("Total sellers with sales:", len(gold))
print("Unique seller IDs:", gold["seller_id"].nunique())

duplicate_sellers = gold["seller_id"].duplicated().sum()

print("Duplicate seller IDs:", duplicate_sellers)

if duplicate_sellers > 0:
    raise ValueError("Duplicate seller IDs found!")

# 11. Display seller analytics
print("\n========== SELLER ANALYTICS ==========")

print(
    "Total product revenue:",
    round(gold["product_revenue"].sum(), 2)
)

print(
    "Total freight:",
    round(gold["total_freight"].sum(), 2)
)

print(
    "Total seller orders:",
    gold["unique_orders"].sum()
)

print("\nTop 10 sellers by revenue:")

print(
    gold[
        [
            "seller_id",
            "seller_city",
            "seller_state",
            "product_revenue",
            "unique_orders",
            "delivered_order_percentage"
        ]
    ].head(10).to_string(index=False)
)

# 12. Save Gold table
output_file = GOLD_DIR / "gold_seller_analytics.csv"

gold.to_csv(output_file, index=False)

print("\nSeller analytics table created successfully!")
print("Final shape:", gold.shape)
print("Saved to:", output_file)