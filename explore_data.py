import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

for file in sorted(DATA_DIR.glob("*.csv")):
    print("\n" + "=" * 60)
    print(f"FILE: {file.name}")
    print("=" * 60)

    # Read only 5 rows initially
    df = pd.read_csv(file, nrows=5)

    print("Columns:")
    print(df.columns.tolist())

    print("\nSample records:")
    print(df.head())

    print("\nColumn data types:")
    print(df.dtypes)
