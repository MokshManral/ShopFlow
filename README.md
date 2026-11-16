# ShopFlow Analytics
### E-commerce Data Engineering Platform

ShopFlow Analytics is an end-to-end data engineering project built using the **Olist Brazilian E-Commerce Public Dataset**. It transforms raw e-commerce data into clean, structured datasets and business-ready analytics using Python and Pandas.

The project follows a **Bronze → Silver → Gold architecture**, with a focus on data ingestion, transformation, validation, and analytical data modelling.

> **Project Status:** Local ETL pipeline and Gold-layer validation completed. AWS cloud integration is planned as the next phase.

---

## Project Objectives

- Build a structured end-to-end ETL pipeline.
- Process multiple related e-commerce datasets.
- Implement data cleaning and validation.
- Design Bronze, Silver, and Gold data layers.
- Generate analytical datasets for business reporting.
- Develop practical data engineering skills using real-world data.

## Dataset

**Olist Brazilian E-Commerce Public Dataset**

The dataset contains information about orders, customers, products, payments, sellers, reviews, and other e-commerce operations.

- Approximately 100,000 orders.
- 9 original CSV datasets.
- Historical data primarily from 2016–2018.
- Brazilian e-commerce transactions.

Dataset source: [Olist Brazilian E-Commerce Dataset – Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Architecture

```text
        Olist CSV Datasets
                |
                v
          Data Ingestion
                |
                v
         BRONZE LAYER
          Raw Datasets
                |
                v
        SILVER LAYER
     Cleaned & Validated Data
                |
                v
          GOLD LAYER
      Business-Ready Analytics
                |
                v
       SQL / Dashboard
          (Planned)
```

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Data Exploration | Jupyter Notebook |
| Data Storage | CSV |
| Data Validation | Python, Pandas |
| Version Control | Git, GitHub |
| Future Cloud Platform | AWS |
| Future ETL Processing | AWS Glue, PySpark |
| Future Analytics | Amazon Athena |

*Future technologies are planned, not yet implemented.*

## Project Structure

```text
ShopFlow/
│
├── data/
│   ├── raw/
│   ├── silver/
│   └── gold/
│
├── ingestion/
│
├── etl/
│   ├── 01_extract.py
│   ├── 02_transform_orders.py
│   ├── ...
│   ├── 20_build_gold_monthly_sales.py
│   ├── 21_build_gold_reviews.py
│   └── 22_validate_gold.py
│
├── notebooks/
│
├── sql/
│
├── dashboard/
│
├── tests/
│
├── explore_data.py
├── profile_data.py
├── requirements.txt
└── README.md
```

## ETL Pipeline

### 1. Data Ingestion and Exploration

- Loaded the original Olist datasets.
- Explored dataset structures and relationships.
- Examined missing values, duplicates, data types, and distributions.
- Identified primary keys and relationships between datasets.

### 2. Silver Layer — Data Cleaning

Implemented transformation and validation scripts for:

- Orders
- Order Items
- Payments
- Customers
- Products
- Sellers
- Reviews
- Geolocation
- Product Category Translation

The Silver layer focuses on data consistency, cleaning, validation, and preparing datasets for further analysis.

### 3. Gold Layer — Business Analytics

Created analytical datasets for:

| Gold Dataset | Purpose |
|---|---|
| Orders | Order-level analytics |
| Products | Product performance |
| Customers | Customer behaviour |
| Sellers | Seller performance |
| Payments | Payment analytics |
| Cities | Location-based analytics |
| Daily Sales | Daily revenue trends |
| Monthly Sales | Monthly revenue trends |
| Reviews | Customer review analytics |

### 4. Data Quality Validation

Implemented validation scripts to check:

- Duplicate records
- Missing identifiers
- Invalid values
- Dataset structure
- Data consistency
- Gold output availability and non-empty datasets

## Current Pipeline Results

| Metric | Result |
|---|---:|
| Total Orders | 99,441 |
| Delivered Orders | 96,478 |
| Cancelled Orders | 625 |
| Payment Records | 103,886 |
| Unique Customers | 96,096 |
| Sellers with Sales | 3,095 |
| City-State Combinations | 4,310 |
| Review Records | 99,224 |
| Daily Sales Records | 634 |
| Monthly Sales Records | 25 |
| Gold Analytical Datasets | 9 |

*These figures describe the historical dataset, not live e-commerce activity.*

## Setup and Execution

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ShopFlow
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the dataset

Download the Olist dataset from Kaggle and place the original CSV files inside:

```text
data/raw/
```

### 5. Run the ETL pipeline

Execute the scripts in sequence:

```bash
python etl/01_extract.py
```

Then run the Silver transformation and validation scripts, followed by the Gold transformation scripts and final audit:

```bash
python etl/22_validate_gold.py
```

Make sure the preceding ETL scripts have completed successfully before running the final audit.

## Planned Improvements

- [ ] Push and maintain the project on GitHub.
- [ ] Build an AWS S3-based Bronze, Silver, and Gold data lake.
- [ ] Implement cloud ETL using AWS Glue and PySpark.
- [ ] Store processed data in Parquet format.
- [ ] Create an AWS Glue Data Catalog.
- [ ] Query analytical datasets using Amazon Athena.
- [ ] Implement pipeline orchestration.
- [ ] Add logging, monitoring, and failure handling.
- [ ] Expand automated data quality tests.
- [ ] Build an analytics dashboard.
- [ ] Document architecture and deployment.

## Learning Outcomes

This project is being developed to gain practical experience with:

- ETL pipeline development
- Data cleaning and transformation
- Data modelling and aggregation
- Data quality checks
- Python-based data engineering
- Cloud data lake architecture
- SQL-based analytics

---

**ShopFlow Analytics** — Building a practical e-commerce data engineering platform, one pipeline at a time.