# Business Requirements Document (BRD)
## E-Commerce Customer & Sales Analytics Platform — Microsoft Fabric

---

## 1. Executive Summary

This project delivers an end-to-end analytics solution on Microsoft Fabric for an Indian e-commerce marketplace operating between January 2022 and December 2024. The solution ingests raw order, customer, and product data into a Fabric Lakehouse, transforms it through a medallion architecture (Bronze → Silver → Gold), and surfaces business-ready insights through Power BI dashboards running on Direct Lake mode.

**Business context:** The marketplace sells across 8 product categories (Electronics, Fashion, Grocery, Home & Kitchen, Beauty & Personal Care, Mobiles & Accessories, Sports & Fitness, Books & Stationery) to customers spread across Tier 1, Tier 2, and Tier 3 Indian cities, accepting Cash on Delivery (COD), UPI, Card, and Wallet payments.

**Purpose:** Give business stakeholders visibility into order cancellation/return drivers, delivery performance, discount effectiveness, and customer value — enabling data-driven decisions on payment mix strategy, logistics investment, and retention marketing.

**Expected business value:** Reduced cancellation/return rate through payment-method-targeted interventions, improved on-time delivery in Tier 2/3 cities, optimized festival-season discounting, and higher customer retention through segmentation-driven marketing.

---

## 2. Project Overview

| Field | Detail |
|---|---|
| Project Name | E-Commerce Customer & Sales Analytics Platform |
| Project Description | Build a Fabric-based medallion pipeline and Power BI semantic layer over 3 years of marketplace order data |
| Business Domain | E-Commerce / Retail (B2C) |
| Project Objectives | Improve order fulfillment quality, reduce cancellations, improve customer retention, enable data-driven discounting |
| Expected Outcomes | Automated, refreshable dashboards replacing manual spreadsheet reporting |
| Scope | Orders, Customers, and Products data (Jan 2022–Dec 2024); Bronze/Silver/Gold pipeline; Power BI reporting layer |
| Out of Scope | Real-time streaming, marketing campaign attribution, inventory replenishment planning, external ad-spend data |
| Success Criteria | Pipeline runs end-to-end without manual intervention; report answers all defined business questions; refresh completes within acceptable SLA |

---

## 3. Dataset Overview

**Time period:** January 1, 2022 – December 31, 2024 (3 years)
**Granularity:** One row per order line item (Orders table); one row per customer (Customers table); one row per product (Products table)
**Volume:** ~56,700 order records, 5,000 customers, 400 products

### 3.1 Orders Table — Column Summary

| Column Name | Description | Data Type | Business Meaning | Example Value |
|---|---|---|---|---|
| Order_ID | Unique order identifier | Text | Primary key for each order | ORD0000001 |
| Customer_ID | Links order to customer | Text | Foreign key to Customers | CUST00001 |
| Product_ID | Links order to product | Text | Foreign key to Products | PROD0144 |
| Category | Product category at time of order | Text | Denormalized for quick filtering | Grocery |
| Order_Date | Date order was placed | Date | Drives all time-series analysis | 2024-08-27 |
| Quantity | Units ordered | Integer | Volume metric | 1 |
| Gross_Amount | Price × quantity before discount | Decimal | Revenue before deductions | 885.52 |
| Discount_Percent | Discount applied | Decimal (0–0.5) | Promotional intensity | 0.06 |
| Discount_Amount | Discount value in currency | Decimal | Cost of promotion | 53.13 |
| Final_Amount | Amount actually charged | Decimal | Net revenue | 832.39 |
| Coupon_Used | Whether a coupon/code was applied | Text (Yes/No) | Marketing effectiveness signal | No |
| Payment_Method | COD / UPI / Card / Wallet | Text | Key driver of cancellation risk | Credit/Debit Card |
| Shipping_Mode | Standard / Express | Text | Logistics choice | Standard |
| Shipping_Cost | Shipping fee charged | Decimal | Cost recovery | 90.30 |
| Delivery_Date | Date order was delivered | Date | Delivery performance tracking | 2024-09-04 |
| Delivery_Days | Days taken to deliver | Integer | SLA measurement | 8 |
| Delivery_On_Time | Whether delivery met promised SLA | Text (Yes/No) | Logistics KPI | No |
| Order_Status | Delivered / Cancelled / Returned | Text | Core fulfillment outcome | Delivered |
| Return_Reason | Reason if returned | Text | Root-cause analysis | (blank if not returned) |
| Product_Rating_Given | Customer rating post-delivery | Integer (1–5) | Customer satisfaction proxy | 3 |

### 3.2 Customers Table — Column Summary

| Column Name | Description | Data Type | Business Meaning | Example Value |
|---|---|---|---|---|
| Customer_ID | Unique customer identifier | Text | Primary key | CUST00001 |
| Customer_Name | Full name | Text | Identification | Rahul Kumar |
| Gender | Male / Female | Text | Demographic segmentation | Male |
| Age | Customer age | Integer | Demographic segmentation | 36 |
| Email | Contact email | Text | Marketing channel | rahul.kumar1@example.com |
| City | City of residence | Text | Geographic analysis | Pune |
| State | State of residence | Text | Regional rollups | Maharashtra |
| City_Tier | Tier 1 / 2 / 3 classification | Text | Key driver of payment behavior & delivery time | Tier 1 |
| Signup_Date | Date customer registered | Date | Cohort/retention analysis | 2024-05-10 |

### 3.3 Products Table — Column Summary

| Column Name | Description | Data Type | Business Meaning | Example Value |
|---|---|---|---|---|
| Product_ID | Unique product identifier | Text | Primary key | PROD0001 |
| Category | Top-level category | Text | Merchandising rollup | Electronics |
| Sub_Category | Second-level category | Text | Granular merchandising | Television |
| Brand | Product brand | Text | Brand performance analysis | Samsung |
| Price | Selling price | Decimal | Revenue driver | 30360.06 |
| Cost_Price | Company's cost | Decimal | Profit margin calculation | 21598.79 |
| Product_Rating | Average product rating | Decimal (1–5) | Quality signal | 3.9 |
| Stock_Quantity | Units in stock | Integer | Inventory risk signal | 392 |

**Entity relationships:** Orders → Customers (many-to-one via Customer_ID); Orders → Products (many-to-one via Product_ID).

**Data quality observations:** No nulls by design except Return_Reason (blank unless status = Returned) and Product_Rating_Given (blank unless delivered and customer rated). No duplicate Order_IDs.

**Assumption (critical):** This dataset is **synthetically generated** to model realistic Indian e-commerce patterns (COD-driven cancellation risk, festival-season demand and discounting, Tier 2/3 delivery delays, customer repeat-purchase behavior). It is not sourced from a live production system. All business logic embedded (e.g., COD cancellation rates, Tier-based delivery SLAs) was deliberately designed to reflect patterns documented in real Indian e-commerce market research, so that the analytics built on top remain representative of real-world conditions.

---

## 4. Business Problem Statement

**Current challenges:**
- No consolidated view of why orders are cancelled or returned
- Delivery performance is not tracked against SLA by geography
- Discounting is applied without visibility into its impact on margin
- Customer value is not segmented — all customers are marketed to uniformly
- Reporting today would rely on manual spreadsheet exports, which do not scale and are error-prone

**Pain points:** High COD dependency increases cancellation exposure; Tier 2/3 markets have unclear delivery reliability; festival-season discounting erodes margin without measured ROI.

**Business inefficiencies:** No automated, single source of truth; insights are reactive rather than proactive.

**Missed opportunities:** Inability to identify and retain high-value customers; inability to shift payment mix toward lower-risk methods; inability to right-size discounts by category/season.

---

## 5. Business Objectives

- Reduce order cancellation/return rate, particularly for COD orders
- Improve on-time delivery percentage in Tier 2 and Tier 3 cities
- Increase revenue from repeat/high-value customers through targeted retention
- Optimize discount spend during festival season without sacrificing margin
- Establish a single, automated, refreshable source of truth for sales and operations reporting
- Improve leadership visibility into category- and brand-level profitability

---

## 6. Stakeholders

| Stakeholder | Responsibility |
|---|---|
| Business Owner / Founder | Defines strategic priorities, reviews high-level KPIs |
| Sales & Marketing Team | Uses customer segmentation and discount-impact insights |
| Logistics/Operations Team | Uses delivery performance and Tier-wise SLA insights |
| Category/Merchandising Team | Uses category and brand performance insights |
| Finance Team | Uses margin and profitability reporting |
| Data Engineering Team | Builds and maintains the Fabric pipeline |
| BI Developer / Analyst | Builds the semantic model and Power BI reports |

---

## 7. Business Questions

1. What is the overall order cancellation and return rate, and how does it vary by payment method?
2. Which payment method carries the highest fulfillment risk (COD vs. digital)?
3. How does cancellation/return rate trend month-over-month across the 3-year period?
4. Which product categories generate the highest revenue and highest profit margin?
5. Which categories have the highest return rate, and what are the top return reasons?
6. How does average discount percentage vary by month, and does it spike during festival season (Oct–Nov)?
7. What is the relationship between discount depth and order cancellation?
8. What percentage of deliveries meet the promised SLA, overall and by City_Tier?
9. How does average delivery time differ between Tier 1, Tier 2, and Tier 3 cities?
10. Does Express shipping meaningfully reduce delivery time and improve on-time performance?
11. Who are the top 10% of customers by lifetime revenue (CLV)?
12. What proportion of customers are one-time buyers vs. repeat buyers?
13. What is the average order frequency and average order value per customer segment?
14. How does customer age or gender correlate with category preference?
15. Which cities/states contribute the most revenue, and which are underpenetrated?
16. What is the customer retention rate by signup cohort (month/quarter)?
17. Which brands have the highest and lowest average product ratings?
18. Is there a correlation between product rating and return rate?
19. What is the average shipping cost recovered vs. actual shipping cost incurred?
20. How does order volume vary seasonally, and which months require additional logistics capacity?
21. What is the coupon usage rate, and does it correlate with higher order value?
22. Which customer segments (by Tier, age, gender) are most price-sensitive (highest discount usage)?
23. What is the profit contribution by category after accounting for discounts and shipping cost?
24. How many customers have gone inactive after their first purchase, and when did they last order?
25. What is the stock-out risk for high-selling, low-stock products?

---

## 8. Analytical Goals

- **Descriptive:** Total revenue, orders, average order value, cancellation rate by period
- **Diagnostic:** Root cause of cancellations/returns (payment method, category, return reason)
- **Trend:** Monthly/quarterly revenue and cancellation trends across 3 years
- **Comparative:** Tier 1 vs. Tier 2 vs. Tier 3 performance; COD vs. digital payment performance
- **Segmentation:** RFM-based customer segmentation (Recency, Frequency, Monetary)
- **Root Cause:** Decomposition of cancellation/return drivers
- **Time Series:** Seasonal demand and discount pattern across festival vs. non-festival months
- **Outlier Detection:** Products with abnormally high return rates or low stock against high demand

---

## 9. Key Performance Indicators (KPIs)

| KPI Name | Formula | Business Importance | Target |
|---|---|---|---|
| Order Cancellation Rate | Cancelled Orders / Total Orders | Measures fulfillment risk | < 6% |
| Return Rate | Returned Orders / Delivered Orders | Measures product/quality risk | < 4% |
| On-Time Delivery % | On-Time Deliveries / Total Deliveries | Measures logistics reliability | > 90% |
| Average Order Value (AOV) | Sum(Final_Amount) / Count(Orders) | Revenue efficiency | Track trend |
| Gross Margin % | (Final_Amount − Cost_Price×Qty) / Final_Amount | Profitability | > 25% |
| Customer Retention Rate | Repeat Customers / Total Customers | Loyalty measurement | > 60% |
| Customer Lifetime Value (CLV) | Sum(Final_Amount) per Customer | Prioritization of high-value customers | Track distribution |
| Discount-to-Revenue Ratio | Sum(Discount_Amount) / Sum(Gross_Amount) | Promotion cost control | < 15% |
| COD Share of Orders | COD Orders / Total Orders | Payment risk exposure | Decreasing trend |

---

## 10. Functional Requirements

- Ingest raw CSV files (Orders, Customers, Products) into a Fabric Lakehouse (Bronze layer)
- Clean and standardize data in Silver layer using PySpark notebooks: handle blanks in Return_Reason/Product_Rating_Given, validate date ranges, deduplicate
- Build a star schema in Gold layer via a Fabric Warehouse using T-SQL
- Create calculated columns/measures for margin, discount ratio, delivery SLA flags
- Build a Power BI semantic model on top of the Gold layer using Direct Lake mode
- Enable drill-through from category-level to product-level and customer-level to order-level
- Support scheduled refresh of the pipeline (daily or on-demand)
- Maintain data lineage from Bronze to Gold for auditability

---

## 11. Non-Functional Requirements

- **Performance:** Report visuals should render within 3–5 seconds under Direct Lake mode
- **Scalability:** Pipeline should handle growth from ~57K to 500K+ order rows without redesign
- **Reliability:** Pipeline failures should be logged and alertable
- **Security:** Row-level security not required for this synthetic dataset but architecture should support it
- **Data Governance:** Column-level documentation maintained (as in Section 3)
- **Availability:** Reports available during business hours at minimum
- **Backup/Disaster Recovery:** Lakehouse/Warehouse backed by OneLake's built-in redundancy
- **Maintainability:** Notebooks and SQL scripts version-controlled (e.g., in GitHub)

---

## 12. Microsoft Fabric Architecture

- **OneLake:** Central storage layer underlying all Fabric items, used implicitly by Lakehouse/Warehouse
- **Lakehouse:** Stores Bronze (raw) and Silver (cleaned) data as Delta tables
- **Notebooks (PySpark):** Perform Silver-layer transformations — cleaning, type casting, derived columns
- **Data Factory / Pipelines:** Orchestrate the end-to-end flow (ingestion → transformation → load) and manage scheduled refresh
- **Warehouse:** Hosts the Gold-layer star schema, built and queried via T-SQL
- **Semantic Model:** Built over the Warehouse/Lakehouse in Direct Lake mode for near-real-time reporting without import duplication
- **Power BI:** Report and dashboard layer consuming the semantic model
- **Monitoring Hub:** Tracks pipeline and notebook run history/failures
- **Deployment Pipelines:** Promote the solution across Dev → Test → Production workspaces

---

## 13. Data Model Recommendations

**Star schema (Gold layer):**

- **Fact_Orders** — Order_ID, Customer_Key, Product_Key, Date_Key, Payment_Method_Key, Quantity, Gross_Amount, Discount_Amount, Final_Amount, Shipping_Cost, Delivery_Days, Order_Status, Return_Reason
- **Dim_Customer** — Customer_Key, Customer_ID, Name, Gender, Age, City, State, City_Tier, Signup_Date
- **Dim_Product** — Product_Key, Product_ID, Category, Sub_Category, Brand, Price, Cost_Price, Product_Rating
- **Dim_Date** — Date_Key, Date, Month, Quarter, Year, Is_Festival_Month
- **Dim_Payment_Method** — Payment_Method_Key, Payment_Method

**Relationships:** All dimension tables connect to Fact_Orders in a single-direction star schema (no snowflaking needed given the manageable dimension sizes).

**Key measures (DAX):** Total Revenue, Cancellation Rate, Return Rate, On-Time Delivery %, Gross Margin %, CLV, Repeat Customer %, Discount-to-Revenue Ratio.

**Calculated columns:** Age_Group (bucketed), Order_Month_Year, Is_Return, Is_Cancelled, Profit_Amount.

---

## 14. Dashboard Recommendations

**Dashboard 1 — Sales & Revenue Overview**
- *Purpose:* Leadership view of overall business health
- *Audience:* Business Owner, Finance
- *Visualizations:* Revenue trend line, AOV card, category revenue bar chart, YoY comparison
- *KPIs:* Total Revenue, AOV, Gross Margin %
- *Filters:* Year, Category, City_Tier
- *Drill-down:* Category → Sub-Category → Product

**Dashboard 2 — Order Fulfillment & Risk**
- *Purpose:* Identify cancellation/return drivers
- *Audience:* Operations, Logistics
- *Visualizations:* Cancellation rate by Payment_Method (bar), decomposition tree for return drivers, trend line
- *KPIs:* Cancellation Rate, Return Rate, On-Time Delivery %
- *Filters:* Payment_Method, City_Tier, Category
- *Drill-down:* Payment Method → Category → Order detail

**Dashboard 3 — Customer Segmentation & Retention**
- *Purpose:* Identify high-value and at-risk customers
- *Audience:* Marketing
- *Visualizations:* RFM segment matrix, CLV distribution histogram, cohort retention heatmap
- *KPIs:* Customer Retention Rate, CLV, Repeat Purchase Rate
- *Filters:* Signup cohort, City_Tier, Gender/Age group
- *Drill-down:* Segment → Customer list → Order history

**Dashboard 4 — Discount & Promotion Effectiveness**
- *Purpose:* Evaluate discount ROI, especially festival season
- *Audience:* Merchandising, Finance
- *Visualizations:* Discount % trend by month, discount vs. cancellation scatter, coupon usage impact
- *KPIs:* Discount-to-Revenue Ratio, AOV with/without coupon
- *Filters:* Month, Category, Coupon_Used

---

## 15. Data Quality Assessment

- **Duplicate records:** None expected (Order_ID is unique by construction); Silver layer should still include a dedup check
- **Missing values:** Return_Reason and Product_Rating_Given are conditionally blank by design — not a data quality defect, must be handled as "Not Applicable" rather than nulls in the Gold layer
- **Invalid values:** None expected in this synthetic dataset; production data would require range checks on Age, Price, Discount_Percent (0–1)
- **Data consistency:** Category field appears in both Orders and Products — Silver layer should validate consistency and prefer Products as the source of truth
- **Recommendation:** Add automated data quality checks (row count thresholds, null checks, referential integrity between Orders/Customers/Products) as part of the Silver-layer notebook

---

## 16. Risks

| Risk | Mitigation |
|---|---|
| Data is synthetic, not live production data | Clearly disclosed; architecture and logic remain transferable to real data |
| Pipeline failure during scheduled refresh | Add monitoring/alerting via Monitoring Hub |
| Schema drift if source columns change | Implement schema validation step in Bronze-to-Silver transformation |
| Performance degradation as data grows | Partition Delta tables by Order_Date; monitor Direct Lake performance |
| Security/access control not yet implemented | Design for Row-Level Security (RLS) even if not enforced initially |
| Low stakeholder adoption of new dashboards | Involve stakeholders early; align dashboards to their existing decision processes |

---

## 17. Assumptions

- The dataset is synthetically generated but modeled on realistic Indian e-commerce business patterns (COD-driven risk, festival seasonality, Tier-based logistics)
- Currency is assumed to be INR (₹)
- "Festival months" are assumed to be October and November (Diwali season) plus a smaller January spike (New Year/Republic Day sales)
- One Order_ID represents one product line item, not a multi-item cart (simplification for this project)
- Customers are uniquely identified by Customer_ID with no duplicate accounts

---

## 18. Constraints

- **Technical:** Limited to Microsoft Fabric trial/capacity; no real-time streaming ingestion in this phase
- **Business:** Project is a portfolio/learning exercise, not a live production system
- **Resource:** Solo development (no dedicated data engineering or QA team)
- **Data:** No external data sources (weather, competitor pricing, ad spend) integrated in this phase

---

## 19. Deliverables

- Fabric Lakehouse with Bronze and Silver layer tables
- Fabric Data Pipeline for orchestration
- Fabric Warehouse with Gold-layer star schema
- Power BI Semantic Model (Direct Lake)
- 4 Power BI Reports/Dashboards (Sales Overview, Fulfillment & Risk, Customer Segmentation, Discount Effectiveness)
- Project Documentation (this BRD, technical design notes, user guide)
- GitHub repository with pipeline code and documentation

---

## 20. Project Timeline (High-Level)

1. Discovery & Requirements (this BRD)
2. Data Assessment & Bronze Ingestion
3. Silver Layer Transformation (PySpark)
4. Gold Layer Modeling (T-SQL star schema)
5. Power BI Semantic Model & Dashboard Development
6. Testing & Validation
7. User Acceptance Review
8. Go-Live / Publish to GitHub & Resume

---

## 21. Success Metrics

- All 25 business questions (Section 7) are answerable directly from the Power BI reports
- Pipeline runs Bronze → Gold without manual data fixes
- Dashboards load within acceptable performance thresholds in Direct Lake mode
- Project is fully documented and published (GitHub, LinkedIn, resume) as a portfolio piece

---

## 22. Future Enhancements

- Predictive analytics: model to predict cancellation probability at order-placement time
- Real-time streaming: integrate Fabric Eventstream to simulate live order tracking
- AI Insights / Copilot integration: natural-language Q&A over the semantic model
- Automated alerts via Data Activator (e.g., alert when daily cancellation rate exceeds threshold)
- Expand dataset with a marketing/ad-spend table to enable full funnel and ROI analysis
