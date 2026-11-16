from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DAILY_PATH = (
    ROOT / "data" / "gold" / "daily_sales"
    / "gold_daily_sales.csv"
)

OUTPUT_DIR = ROOT / "data" / "gold" / "monthly_sales"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DAILY SALES DATA
# --------------------------------------------------

daily = pd.read_csv(
    DAILY_PATH,
    parse_dates=["order_date"]
)

print("Daily sales data loaded successfully!")


# --------------------------------------------------
# 3. CREATE MONTH COLUMN
# --------------------------------------------------

daily["month"] = (
    daily["order_date"].dt.to_period("M").astype(str)
)


# --------------------------------------------------
# 4. AGGREGATE MONTHLY METRICS
# --------------------------------------------------

monthly = (
    daily.groupby("month")
    .agg(
        total_orders=("total_orders", "sum"),
        delivered_orders=("delivered_orders", "sum"),
        canceled_orders=("canceled_orders", "sum"),
        total_items=("total_items", "sum"),
        total_item_value=("total_item_value", "sum"),
        delivered_revenue=("delivered_revenue", "sum"),
        total_freight=("total_freight", "sum")
    )
    .reset_index()
)


# --------------------------------------------------
# 5. CALCULATE MONTHLY KPIs
# --------------------------------------------------

monthly["average_order_value"] = (
    monthly["delivered_revenue"]
    / monthly["delivered_orders"].replace(0, pd.NA)
).fillna(0)

monthly["delivery_rate"] = (
    monthly["delivered_orders"]
    / monthly["total_orders"]
) * 100

monthly["cancellation_rate"] = (
    monthly["canceled_orders"]
    / monthly["total_orders"]
) * 100


# --------------------------------------------------
# 6. VALIDATE MONTHLY DATA
# --------------------------------------------------

print("\n========== MONTHLY SALES VALIDATION ==========")

print("Total months:", len(monthly))

print("Total orders:", monthly["total_orders"].sum())

print(
    "Total item value:",
    round(monthly["total_item_value"].sum(), 2)
)

print(
    "Total delivered revenue:",
    round(monthly["delivered_revenue"].sum(), 2)
)

if monthly["month"].duplicated().any():
    raise ValueError("Duplicate months found!")

print("\nMonthly sales preview:")
print(monthly.head(10).to_string(index=False))


# --------------------------------------------------
# 7. SAVE MONTHLY ANALYTICS
# --------------------------------------------------

output_path = OUTPUT_DIR / "gold_monthly_sales.csv"

monthly.to_csv(output_path, index=False)

print("\nMonthly sales analytics created successfully!")
print("Final shape:", monthly.shape)
print("Saved to:", output_path)