from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "data" / "gold"

expected_files = [
    "orders/gold_order_analytics.csv",
    "products/gold_product_analytics.csv",
    "customers/gold_customer_analytics.csv",
    "sellers/gold_seller_analytics.csv",
    "payments/gold_payment_analytics.csv",
    "cities/gold_city_analytics.csv",
    "daily_sales/gold_daily_sales.csv",
    "monthly_sales/gold_monthly_sales.csv",
    "reviews/gold_review_analytics.csv"
]

print("========== GOLD LAYER AUDIT ==========")

passed = 0
failed = 0

for relative_path in expected_files:
    file_path = GOLD / relative_path

    if not file_path.exists():
        print(f"FAILED: {relative_path} - File missing")
        failed += 1
        continue

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            print(f"FAILED: {relative_path} - Empty table")
            failed += 1
            continue

        print(
            f"PASSED: {relative_path} "
            f"| Rows: {len(df)} "
            f"| Columns: {len(df.columns)}"
        )
        passed += 1

    except Exception as error:
        print(f"FAILED: {relative_path} - {error}")
        failed += 1

print("\n========== AUDIT SUMMARY ==========")
print("Passed:", passed)
print("Failed:", failed)
print("Total:", len(expected_files))

if failed:
    raise SystemExit("Gold layer audit failed!")

print("\nGOLD LAYER AUDIT PASSED!")