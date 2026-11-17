
import importlib.util
from pathlib import Path


# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parent


# ==========================================
# 2. PIPELINE CONFIGURATION
# ==========================================

STAGES = [
    ("03_silver_validate.py", "validate_silver"),
    ("04_gold_build.py", "build_gold"),
    ("05_gold_validate.py", "validate_gold"),
]


def load_stage(filename):
    """Load a numbered pipeline script as a Python module."""
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load pipeline stage: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ==========================================
# 3. RUN PIPELINE
# ==========================================

def run_pipeline():

    print("\n========== SHOPFLOW ETL PIPELINE ==========\n")

    print("\nRunning: 01_extract.py + 02_silver_transform.py")
    extracted = load_stage("01_extract.py").extract_data()
    load_stage("02_silver_transform.py").transform_data(extracted)
    print("Completed: extraction and Silver transformation")

    for filename, function_name in STAGES:
        print(f"\nRunning: {filename}")
        stage = load_stage(filename)
        getattr(stage, function_name)()
        print(f"Completed: {filename}")

    # Final pipeline status
    print("\n===================================")
    print("SHOPFLOW PIPELINE COMPLETED!")
    print("===================================")


# ==========================================
# 4. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    run_pipeline()
