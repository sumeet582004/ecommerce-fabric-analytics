# E-Commerce Customer & Sales Analytics Platform — Microsoft Fabric

End-to-end data analytics solution built on Microsoft Fabric, covering the full medallion architecture (Bronze → Silver → Gold) and a Power BI report connected live via Direct Lake.

**Dataset note:** This project uses a synthetically generated dataset modeling realistic Indian e-commerce patterns (COD-driven cancellation risk, festival-season demand, Tier 1/2/3 city delivery behavior, customer repeat-purchase patterns). It is not sourced from a live production system — the business logic embedded in the data (COD cancellation rates, tier-based delivery delays, festival discounting) was deliberately designed based on real Indian e-commerce market patterns, so the analytics built on top remain representative of real-world conditions. Full reasoning is documented in the [BRD](./BRD_Ecommerce_Fabric_Project.md).

---

## Business Problem

The marketplace had no consolidated view of why orders were cancelled or returned, no delivery performance tracking by geography, no visibility into discount-vs-margin tradeoffs, and no customer segmentation — reporting relied on manual spreadsheet exports. This project builds a single, automated, refreshable source of truth to answer 25 defined business questions (full list in the BRD).

**Key finding:** COD (Cash on Delivery) orders have a significantly higher cancellation rate than digital payment methods (UPI, Card, Wallet) — this is the core risk driver surfaced on the Order Fulfillment & Risk page.

---

## Architecture

```
Raw CSV (Orders, Customers, Products)
        ↓
Bronze Layer — Fabric Lakehouse (raw Delta tables)
        ↓
Silver Layer — PySpark notebook (cleaning, type casting, derived flags)
        ↓
Gold Layer — Spark SQL notebook (star schema: Dim_Date, Dim_Customer,
             Dim_Product, Dim_Payment_Method, Fact_Orders) +
             2 aggregate tables (Gold_Monthly_Category_Summary,
             Gold_Payment_Risk_Summary)
        ↓
Fabric Warehouse — Gold tables copied in via pipeline; 1 SQL view
        ↓
Power BI (Direct Lake) — 5-page report, 28+ DAX measures, time
             intelligence, dynamic visuals
```

**Tech stack:** Microsoft Fabric (Lakehouse, Warehouse, Notebooks, Data Pipelines), PySpark, Spark SQL, T-SQL, Power BI (Direct Lake), DAX.

---

## Dataset

- **Time period:** January 2022 – December 2024 (3 years)
- **Orders:** ~56,700 rows, 20 columns (payment method, discount, shipping, delivery SLA, return reason, rating)
- **Customers:** 5,000 rows, 9 columns (demographics, city tier, signup date)
- **Products:** 400 rows, 8 columns (category, brand, price, cost, margin, stock)

Full column-level documentation is in the [BRD](./BRD_Ecommerce_Fabric_Project.md), Section 3.

---

## Report Pages

| Page | What it answers |
|---|---|
| **Home** | Executive summary — headline KPIs and navigation |
| **Sales & Revenue Overview** | Revenue trend, category/city performance, profit contribution, YoY/MoM growth |
| **Order Fulfillment & Risk** | Cancellation/return rate by payment method & city tier, root-cause decomposition |
| **Customer Segmentation & Retention** | Age/gender/city breakdown, repeat vs one-time customers, retention by state |
| **Discount & Promotion Effectiveness** | Discount trend, coupon impact on order value, discount-vs-cancellation correlation |

---

## Screenshots

*(Replace these placeholders with your actual exported PNGs before pushing — see the "How to add screenshots" section below.)*

### Home
![Home page](./screenshots/01_home.png)

### Sales & Revenue Overview
![Sales Overview](./screenshots/02_sales_overview.png)

### Order Fulfillment & Risk
![Fulfillment Risk](./screenshots/03_fulfillment_risk.png)

### Customer Segmentation & Retention
![Customer Segmentation](./screenshots/04_customer_segmentation.png)

### Discount & Promotion Effectiveness
![Discount Effectiveness](./screenshots/05_discount_effectiveness.png)

---

## Repository Structure

```
├── README.md
├── BRD_Ecommerce_Fabric_Project.md        # Full business requirements document
├── PowerBI_Report_Build_Guide.md          # Step-by-step build log (measures, visuals, DAX)
├── screenshots/                           # Exported report page images
├── powerbi/
│   └── e_commerce_report.pbip             # Power BI Project (Direct Lake)
├── sql/
│   ├── silver_layer_pyspark.py            # Bronze -> Silver cleaning (PySpark)
│   ├── build_gold_layer_sql_notebook.sql  # Silver -> Gold star schema (Spark SQL)
│   └── warehouse_queries/                 # Warehouse view + verification queries
└── data_generation/
    └── generate_dataset.py                # Synthetic dataset generator
```

---

## Key Insights

- COD orders cancel/return at a materially higher rate than digital payments across every city tier
- Revenue grew year-over-year through 2022–2024 as the customer base expanded
- Festival months (October–November) show a clear discount and sales spike, consistent with Diwali-season shopping patterns
- Customer retention rate sits around 70%, with Maharashtra contributing the highest state-level customer count
- Discount depth shows no strong correlation with cancellation rate — heavier discounting does not appear to drive more cancellations

---

## How to Explore

The `.pbip` file is connected live to a Microsoft Fabric Direct Lake semantic model. Opening it requires:
1. Power BI Desktop
2. Access to the underlying Fabric workspace (private — the live data connection will not work outside the author's Fabric trial/capacity)

If the Fabric trial capacity has expired, the file will not load live data — refer to the screenshots above for the full report, or contact me for a recorded walkthrough.

---

## Author

Sumit Kale — [LinkedIn] · [Portfolio/Resume link]
