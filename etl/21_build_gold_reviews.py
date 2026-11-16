from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"

OUTPUT_DIR = ROOT / "data" / "gold" / "reviews"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD REVIEWS
# --------------------------------------------------

reviews = pd.read_csv(
    SILVER / "reviews" / "reviews_cleaned.csv",
    parse_dates=[
        "review_creation_date",
        "review_answer_timestamp"
    ]
)

print("Review data loaded successfully!")


# --------------------------------------------------
# 3. VALIDATE REVIEWS
# --------------------------------------------------

if reviews["review_id"].isna().any():
    raise ValueError("Missing review IDs found!")

if reviews["order_id"].isna().any():
    raise ValueError("Missing order IDs found!")

if not reviews["review_score"].between(1, 5).all():
    raise ValueError("Invalid review scores found!")

if reviews.duplicated(["review_id", "order_id"]).any():
    raise ValueError("Duplicate review-order pairs found!")


# --------------------------------------------------
# 4. CLEAN COMMENT FIELDS
# --------------------------------------------------

reviews["review_comment_title"] = (
    reviews["review_comment_title"].fillna("").astype(str).str.strip()
)

reviews["review_comment_message"] = (
    reviews["review_comment_message"].fillna("").astype(str).str.strip()
)

reviews["has_comment"] = (
    (reviews["review_comment_title"] != "")
    | (reviews["review_comment_message"] != "")
)


# --------------------------------------------------
# 5. CALCULATE RESPONSE TIME
# --------------------------------------------------

reviews["response_hours"] = (
    reviews["review_answer_timestamp"]
    - reviews["review_creation_date"]
).dt.total_seconds() / 3600

# Exclude missing or negative response times
reviews.loc[
    reviews["response_hours"] < 0,
    "response_hours"
] = pd.NA


# --------------------------------------------------
# 6. BUILD REVIEW SCORE ANALYTICS
# --------------------------------------------------

review_analytics = (
    reviews.groupby("review_score")
    .agg(
        total_reviews=("review_id", "count"),
        unique_orders=("order_id", "nunique"),
        reviews_with_comments=("has_comment", "sum"),
        average_response_hours=("response_hours", "mean")
    )
    .reset_index()
)


# --------------------------------------------------
# 7. CALCULATE PERCENTAGES
# --------------------------------------------------

total_reviews = review_analytics["total_reviews"].sum()

review_analytics["review_percentage"] = (
    review_analytics["total_reviews"] / total_reviews
) * 100

review_analytics["comment_percentage"] = (
    review_analytics["reviews_with_comments"]
    / review_analytics["total_reviews"]
) * 100

review_analytics = review_analytics.sort_values("review_score")


# --------------------------------------------------
# 8. FINAL VALIDATION
# --------------------------------------------------

print("\n========== REVIEW ANALYTICS VALIDATION ==========")

print("Total reviews:", total_reviews)

print(
    "Unique reviewed orders:",
    reviews["order_id"].nunique()
)

print(
    "Reviews with comments:",
    int(reviews["has_comment"].sum())
)

print("\nReview score analytics:")

print(review_analytics.to_string(index=False))


# --------------------------------------------------
# 9. SAVE GOLD TABLE
# --------------------------------------------------

output_path = OUTPUT_DIR / "gold_review_analytics.csv"

review_analytics.to_csv(output_path, index=False)

print("\nReview analytics created successfully!")
print("Final shape:", review_analytics.shape)
print("Saved to:", output_path)