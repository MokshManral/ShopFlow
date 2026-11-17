
import os
import pandas as pd


# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SILVER_DIR = os.path.join(ROOT, "data", "silver")
GOLD_DIR = os.path.join(ROOT, "data", "gold")


# ==========================================
# 2. LOAD FUNCTION
# ==========================================

def load(name):

    path = os.path.join(
        SILVER_DIR, name, f"{name}_cleaned.csv"
    )

    return pd.read_csv(path)


# ==========================================
# 3. SAVE FUNCTION
# ==========================================

def save(df, folder, filename):

    path = os.path.join(GOLD_DIR, folder)

    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, filename)

    df.to_csv(file_path, index=False)

    print(f"Saved: {filename} | Rows: {len(df)}")


# ==========================================
# 4. BUILD GOLD LAYER
# ==========================================

def build_gold():

    print("\n========== BUILDING GOLD LAYER ==========")

    # Load Silver datasets
    orders = load("orders")
    items = load("order_items")
    payments = load("payments")
    customers = load("customers")
    products = load("products")
    sellers = load("sellers")
    reviews = load("reviews")

    # Convert numeric columns
    for col in ["price", "freight_value"]:

        items[col] = pd.to_numeric(
            items[col], errors="coerce"
        )

    payments["payment_value"] = pd.to_numeric(
        payments["payment_value"], errors="coerce"
    )

    reviews["review_score"] = pd.to_numeric(
        reviews["review_score"], errors="coerce"
    )

    # Aggregate items by order
    item_agg = items.groupby("order_id").agg(
        total_items=("order_item_id", "count"),
        revenue=("price", "sum"),
        freight=("freight_value", "sum")
    ).reset_index()

    # Aggregate payments by order
    payment_agg = payments.groupby("order_id").agg(
        total_payment=("payment_value", "sum")
    ).reset_index()

    # Aggregate reviews by order
    review_agg = reviews.groupby("order_id").agg(
        average_review=("review_score", "mean"),
        review_count=("review_id", "count")
    ).reset_index()


    # ==========================================
    # 5. GOLD ORDERS
    # ==========================================

    gold_orders = orders.merge(
        item_agg, on="order_id", how="left"
    ).merge(
        payment_agg, on="order_id", how="left"
    ).merge(
        review_agg, on="order_id", how="left"
    )

    gold_orders = gold_orders.merge(
        customers[
            ["customer_id", "customer_city", "customer_state"]
        ],
        on="customer_id",
        how="left"
    )

    gold_orders[
        [
            "total_items",
            "revenue",
            "freight",
            "total_payment",
            "review_count"
        ]
    ] = gold_orders[
        [
            "total_items",
            "revenue",
            "freight",
            "total_payment",
            "review_count"
        ]
    ].fillna(0)

    save(
        gold_orders,
        "orders",
        "gold_order_analytics.csv"
    )


    # ==========================================
    # 6. GOLD PRODUCTS
    # ==========================================

    product_data = items.merge(
        products,
        on="product_id",
        how="left"
    )

    gold_products = product_data.groupby(
        ["product_id", "product_category_name"],
        dropna=False
    ).agg(
        total_items=("order_item_id", "count"),
        unique_orders=("order_id", "nunique"),
        revenue=("price", "sum")
    ).reset_index()

    save(
        gold_products,
        "products",
        "gold_product_analytics.csv"
    )


    # ==========================================
    # 7. GOLD CUSTOMERS
    # ==========================================

    customer_orders = orders.merge(
        customers,
        on="customer_id",
        how="left"
    )

    customer_orders = customer_orders.merge(
        payment_agg,
        on="order_id",
        how="left"
    )

    gold_customers = customer_orders.groupby(
        "customer_unique_id"
    ).agg(
        total_orders=("order_id", "nunique"),
        total_payment=("total_payment", "sum"),
        customer_city=("customer_city", "first"),
        customer_state=("customer_state", "first")
    ).reset_index()

    gold_customers["customer_type"] = (
        gold_customers["total_orders"]
        .map(lambda x: "Repeat" if x > 1 else "One-time")
    )

    save(
        gold_customers,
        "customers",
        "gold_customer_analytics.csv"
    )


    # ==========================================
    # 8. GOLD SELLERS
    # ==========================================

    seller_data = items.merge(
        sellers,
        on="seller_id",
        how="left"
    )

    gold_sellers = seller_data.groupby(
        "seller_id"
    ).agg(
        total_items=("order_item_id", "count"),
        unique_orders=("order_id", "nunique"),
        revenue=("price", "sum"),
        seller_city=("seller_city", "first"),
        seller_state=("seller_state", "first")
    ).reset_index()

    save(
        gold_sellers,
        "sellers",
        "gold_seller_analytics.csv"
    )


    # ==========================================
    # 9. GOLD PAYMENTS
    # ==========================================

    gold_payments = payments.groupby(
        "payment_type"
    ).agg(
        total_transactions=("payment_value", "count"),
        total_payment=("payment_value", "sum"),
        average_payment=("payment_value", "mean")
    ).reset_index()

    save(
        gold_payments,
        "payments",
        "gold_payment_analytics.csv"
    )


    # ==========================================
    # 10. GOLD CITIES
    # ==========================================

    city_orders = orders.merge(
        customers,
        on="customer_id",
        how="left"
    ).merge(
        item_agg,
        on="order_id",
        how="left"
    )

    gold_cities = city_orders.groupby(
        ["customer_city", "customer_state"]
    ).agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("revenue", "sum"),
        unique_customers=("customer_unique_id", "nunique")
    ).reset_index()

    save(
        gold_cities,
        "cities",
        "gold_city_analytics.csv"
    )


    # ==========================================
    # 11. GOLD DAILY SALES
    # ==========================================

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

    daily_data = orders.merge(
        item_agg,
        on="order_id",
        how="left"
    )

    daily_data["order_date"] = (
        daily_data["order_purchase_timestamp"].dt.date
    )

    gold_daily = daily_data.groupby(
        "order_date"
    ).agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("revenue", "sum"),
        total_items=("total_items", "sum")
    ).reset_index()

    save(
        gold_daily,
        "daily_sales",
        "gold_daily_sales.csv"
    )


    # ==========================================
    # 12. GOLD MONTHLY SALES
    # ==========================================

    daily_data["month"] = (
        daily_data["order_purchase_timestamp"]
        .dt.to_period("M").astype(str)
    )

    gold_monthly = daily_data.groupby(
        "month"
    ).agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("revenue", "sum"),
        total_items=("total_items", "sum")
    ).reset_index()

    save(
        gold_monthly,
        "monthly_sales",
        "gold_monthly_sales.csv"
    )


    # ==========================================
    # 13. GOLD REVIEWS
    # ==========================================

    gold_reviews = reviews.groupby(
        "review_score"
    ).agg(
        total_reviews=("review_id", "count"),
        unique_orders=("order_id", "nunique")
    ).reset_index()

    save(
        gold_reviews,
        "reviews",
        "gold_review_analytics.csv"
    )


    # ==========================================
    # 14. COMPLETION
    # ==========================================

    print("\n========== GOLD LAYER COMPLETED ==========")

    print("Total Gold datasets created: 9")

    print("Gold layer creation completed successfully!")


# ==========================================
# 15. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    build_gold()
