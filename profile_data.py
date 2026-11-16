
import pandas as pd
from pathlib import Path

# 1. Define the location of our raw datasets
DATA_DIR = Path("data/raw")

# 2. Find all CSV files
csv_files = sorted(DATA_DIR.glob("*.csv"))

# 3. Check whether CSV files exist
if not csv_files:
    raise FileNotFoundError("No CSV files found inside data/raw")

print(f"Found {len(csv_files)} CSV files")

# 4. Profile each CSV file individually
for file in csv_files:

    print("\n" + "=" * 70)
    print(f"DATA QUALITY REPORT: {file.name}")
    print("=" * 70)

    # 5. Load the current CSV file
    df = pd.read_csv(file)

    # 6. Basic dataset information
    print("\n--- BASIC INFORMATION ---")
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Total Cells: {df.size}")

    # 7. Column names and data types
    print("\n--- COLUMN DATA TYPES ---")
    print(df.dtypes)

    # 8. Missing values
    print("\n--- MISSING VALUES ---")
    missing = df.isnull().sum()

    missing_report = pd.DataFrame({
        "Missing Values": missing,
        "Missing Percentage": (
            missing / len(df) * 100
        ).round(2)
    })

    print(missing_report)

    # 9. Duplicate records
    print("\n--- DUPLICATE RECORDS ---")
    duplicate_count = df.duplicated().sum()

    print(f"Duplicate Rows: {duplicate_count}")

    # 10. Unique values in each column
    print("\n--- UNIQUE VALUES ---")
    print(df.nunique())

    # 11. Final summary
    print("\n--- PROFILE SUMMARY ---")
    print(
        f"{file.name}: "
        f"{len(df)} rows, "
        f"{len(df.columns)} columns, "
        f"{duplicate_count} duplicate rows"
    )

print("\nDATA PROFILING COMPLETED!")
