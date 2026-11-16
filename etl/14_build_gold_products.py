
import pandas as pd
from pathlib import Path

# 1. Define project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold" / "products"

GOLD_DIR.mkdir(parents=True, exist_ok=True)

# 2. Load cleaned datasets
items = pd.read_csv(
    SILVER_DIR / "order_items" / "order_items_cleaned.csv"
)

products = pd.read_csv(
    SILVER_DIR / "products" / "products_cleaned.csv"
)

translations = pd.read_csv(
    SILVER_DIR / "category_translation" /
    "category_translation_cleaned.csv"
)

print("All datasets loaded successfully!")

# 3. Join order items with product details
product_data = items.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one"
)

# 4. Join English category translations
product_data = product_data.merge(
    translations,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)

# 5. Preserve categories without translations
product_data["product_category_name_english"] = (
    product_data["product_category_name_english"]
    .fillna("unknown")
)

# 6. Aggregate data at product level
gold = (
    product_data.groupby(
        [
            "product_id",
            "product_category_name",
            "product_category_name_english"
        ],
        dropna=False
    )
    .agg(
        total_order_items=("order_item_id", "count"),
        unique_orders=("order_id", "nunique"),
        product_revenue=("price", "sum"),
        total_freight=("freight_value", "sum"),
        average_item_price=("price", "mean")
    )
    .reset_index()
)

# 7. Sort products by revenue
gold = gold.sort_values(
    by="product_revenue",
    ascending=False
)

# 8. Validate Gold table
print("\n========== PRODUCT TABLE VALIDATION ==========")

print("Total products:", len(gold))
print("Unique product IDs:", gold["product_id"].nunique())

duplicate_products = gold["product_id"].duplicated().sum()

print("Duplicate product IDs:", duplicate_products)

if duplicate_products > 0:
    raise ValueError("Duplicate product IDs found!")

# 9. Display business analytics
print("\n========== PRODUCT ANALYTICS ==========")

print(
    "Total product revenue:",
    round(gold["product_revenue"].sum(), 2)
)

print(
    "Total freight:",
    round(gold["total_freight"].sum(), 2)
)

print("\nTop 10 products by revenue:")
print(
    gold[
        [
            "product_id",
            "product_category_name_english",
            "product_revenue",
            "unique_orders"
        ]
    ].head(10).to_string(index=False)
)

print("\nTop 10 categories by revenue:")

category_summary = (
    gold.groupby("product_category_name_english")
    ["product_revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print(category_summary)

# 10. Save Gold table
output_file = GOLD_DIR / "gold_product_analytics.csv"

gold.to_csv(output_file, index=False)

print("\nProduct analytics table created successfully!")
print("Final shape:", gold.shape)
print("Saved to:", output_file)

