-- ================================================================
-- ================================================================
-- NOTEBOOK 1: Build_Gold_Layer
-- Purpose: Build the Gold Layer using SQL
-- Setup: Attach the Ecommerce_Bronze_Lakehouse to the notebook.
-- Each CELL should be executed separately.
-- Each SQL cell must begin with %%sql.
-- Execute the cells sequentially from top to bottom.
-- ================================================================
-- ================================================================


-- ===================== CELL 1: Dim_Date =====================
%%sql
CREATE OR REPLACE TABLE Dim_Date AS
SELECT
    CAST(date_format(d, 'yyyyMMdd') AS INT)         AS Date_Key,
    d                                               AS `Date`,
    YEAR(d)                                         AS `Year`,
    QUARTER(d)                                      AS `Quarter`,
    MONTH(d)                                        AS `Month`,
    date_format(d, 'MMMM')                          AS Month_Name,
    DAY(d)                                          AS `Day`,
    date_format(d, 'EEEE')                          AS Day_Name,
    WEEKOFYEAR(d)                                   AS Week_Of_Year,
    CASE WHEN MONTH(d) IN (10, 11) THEN 1 ELSE 0 END AS Is_Festival_Month
FROM (
    SELECT explode(sequence(to_date('2022-01-01'), to_date('2024-12-31'), interval 1 day)) AS d
)


-- ===================== CELL 2: Dim_Customer =====================
%%sql
CREATE OR REPLACE TABLE Dim_Customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY Customer_ID) AS Customer_Key,
    Customer_ID, Customer_Name, Gender, Age, Age_Group,
    Email, City, `State`, City_Tier, Signup_Date
FROM Silver_Customers


-- ===================== CELL 3: Dim_Product =====================
%%sql
CREATE OR REPLACE TABLE Dim_Product AS
SELECT
    ROW_NUMBER() OVER (ORDER BY Product_ID) AS Product_Key,
    Product_ID, Category, Sub_Category, Brand,
    Price, Cost_Price, Margin_Percent, Product_Rating, Stock_Quantity
FROM Silver_Products


-- ===================== CELL 4: Dim_Payment_Method =====================
%%sql
CREATE OR REPLACE TABLE Dim_Payment_Method AS
SELECT
    ROW_NUMBER() OVER (ORDER BY Payment_Method) AS Payment_Method_Key,
    Payment_Method
FROM (
    SELECT explode(array('COD', 'UPI', 'Credit/Debit Card', 'Wallet')) AS Payment_Method
)


-- ===================== CELL 5: Fact_Orders =====================
-- Execute this cell after Cells 2, 3, and 4 because
-- Fact_Orders joins the customer, product, and payment dimensions.
%%sql
CREATE OR REPLACE TABLE Fact_Orders AS
SELECT
    o.Order_ID,
    c.Customer_Key,
    p.Product_Key,
    CAST(date_format(o.Order_Date, 'yyyyMMdd') AS INT) AS Date_Key,
    pm.Payment_Method_Key,
    o.Quantity,
    o.Gross_Amount,
    o.Discount_Percent,
    o.Discount_Amount,
    o.Final_Amount,
    o.Coupon_Used,
    o.Shipping_Mode,
    o.Shipping_Cost,
    o.Delivery_Days,
    o.Delivery_On_Time,
    o.Order_Status,
    o.Is_Cancelled,
    o.Is_Returned,
    o.Is_Delivered,
    o.Return_Reason,
    o.Product_Rating_Given,
    o.Final_Amount - (p.Cost_Price * o.Quantity) AS Profit_Amount
FROM Silver_Orders o
JOIN Dim_Customer       c  ON o.Customer_ID    = c.Customer_ID
JOIN Dim_Product        p  ON o.Product_ID     = p.Product_ID
JOIN Dim_Payment_Method pm ON o.Payment_Method = pm.Payment_Method


-- ===================== CELL 6: GOLD Aggregation Table — Category + Month performance =====================
%%sql
CREATE OR REPLACE TABLE Gold_Monthly_Category_Summary AS
SELECT
    d.`Year`,
    d.`Month`,
    d.Month_Name,
    p.Category,
    COUNT(f.Order_ID)                               AS Total_Orders,
    ROUND(SUM(f.Final_Amount), 2)                   AS Total_Revenue,
    ROUND(SUM(f.Profit_Amount), 2)                  AS Total_Profit,
    ROUND(SUM(f.Is_Cancelled) * 100.0 / COUNT(*), 2) AS Cancellation_Rate,
    ROUND(SUM(f.Is_Returned)  * 100.0 / COUNT(*), 2) AS Return_Rate,
    ROUND(AVG(f.Final_Amount), 2)                   AS Avg_Order_Value
FROM Fact_Orders f
JOIN Dim_Date    d ON f.Date_Key    = d.Date_Key
JOIN Dim_Product p ON f.Product_Key = p.Product_Key
GROUP BY d.`Year`, d.`Month`, d.Month_Name, p.Category


-- ===================== CELL 7: GOLD 2 — Payment Method + City Tier risk =====================
%%sql
CREATE OR REPLACE TABLE Gold_Payment_Risk_Summary AS
SELECT
    pm.Payment_Method,
    c.City_Tier,
    COUNT(f.Order_ID)                               AS Total_Orders,
    ROUND(SUM(f.Final_Amount), 2)                   AS Total_Revenue,
    ROUND(SUM(f.Is_Cancelled) * 100.0 / COUNT(*), 2) AS Cancellation_Rate,
    ROUND(SUM(f.Is_Returned)  * 100.0 / COUNT(*), 2) AS Return_Rate
FROM Fact_Orders f
JOIN Dim_Payment_Method pm ON f.Payment_Method_Key = pm.Payment_Method_Key
JOIN Dim_Customer       c  ON f.Customer_Key       = c.Customer_Key
GROUP BY pm.Payment_Method, c.City_Tier


-- ===================== CELL 8: Verify (all tables row count) =====================
%%sql
SELECT 'Dim_Date' AS Table_Name, COUNT(*) AS Row_Count FROM Dim_Date
UNION ALL SELECT 'Dim_Customer', COUNT(*) FROM Dim_Customer
UNION ALL SELECT 'Dim_Product', COUNT(*) FROM Dim_Product
UNION ALL SELECT 'Dim_Payment_Method', COUNT(*) FROM Dim_Payment_Method
UNION ALL SELECT 'Fact_Orders', COUNT(*) FROM Fact_Orders
UNION ALL SELECT 'Gold_Monthly_Category_Summary', COUNT(*) FROM Gold_Monthly_Category_Summary
UNION ALL SELECT 'Gold_Payment_Risk_Summary', COUNT(*) FROM Gold_Payment_Risk_Summary
