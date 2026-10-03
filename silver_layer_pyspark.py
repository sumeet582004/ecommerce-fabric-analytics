# ================================================================
# CELL 1: Load Bronze tables
# ================================================================
df_orders = spark.read.table("Orders")
df_customers = spark.read.table("Customers")
df_products = spark.read.table("Products")

print("Orders:", df_orders.count())
print("Customers:", df_customers.count())
print("Products:", df_products.count())


# ================================================================
# CELL 2: Import functions
# ================================================================
from pyspark.sql.functions import (
    col, when, to_date, month, year, coalesce, lit, round as spark_round,
    countDistinct, current_date, datediff
)


# ================================================================
# CELL 3: Clean Orders table
# ================================================================
df_orders_clean = (
    df_orders
    # cast date columns properly
    .withColumn("Order_Date", to_date(col("Order_Date")))
    .withColumn("Delivery_Date", to_date(col("Delivery_Date")))
    # handle conditional blanks -> replace empty string with "Not Applicable"
    .withColumn(
        "Return_Reason",
        when((col("Return_Reason") == "") | col("Return_Reason").isNull(), "Not Applicable")
        .otherwise(col("Return_Reason"))
    )
    .withColumn(
        "Product_Rating_Given",
        when(col("Product_Rating_Given") == "", None)
        .otherwise(col("Product_Rating_Given"))
        .cast("int")
    )
    # derived flags
    .withColumn("Is_Cancelled", when(col("Order_Status") == "Cancelled", 1).otherwise(0))
    .withColumn("Is_Returned", when(col("Order_Status") == "Returned", 1).otherwise(0))
    .withColumn("Is_Delivered", when(col("Order_Status") == "Delivered", 1).otherwise(0))
    .withColumn("Order_Month", month(col("Order_Date")))
    .withColumn("Order_Year", year(col("Order_Date")))
    .withColumn(
        "Is_Festival_Month",
        when(col("Order_Month").isin(10, 11), 1).otherwise(0)
    )
)

# drop exact duplicate rows if any
df_orders_clean = df_orders_clean.dropDuplicates(["Order_ID"])

print("Orders after cleaning:", df_orders_clean.count())
df_orders_clean.select("Order_ID", "Return_Reason", "Product_Rating_Given", "Is_Festival_Month").show(5)


# ================================================================
# CELL 4: Clean Customers table
# ================================================================
df_customers_clean = (
    df_customers
    .withColumn("Signup_Date", to_date(col("Signup_Date")))
    .withColumn(
        "Age_Group",
        when(col("Age") < 25, "18-24")
        .when(col("Age") < 35, "25-34")
        .when(col("Age") < 45, "35-44")
        .when(col("Age") < 55, "45-54")
        .otherwise("55+")
    )
    .dropDuplicates(["Customer_ID"])
)

print("Customers after cleaning:", df_customers_clean.count())


# ================================================================
# CELL 5: Clean Products table + Profit calculation prep
# ================================================================
df_products_clean = (
    df_products
    .withColumn("Margin_Percent", spark_round(((col("Price") - col("Cost_Price")) / col("Price")) * 100, 2))
    .dropDuplicates(["Product_ID"])
)

print("Products after cleaning:", df_products_clean.count())


# ================================================================
# CELL 6: Referential integrity check (data quality)
# ================================================================
orphan_customers = df_orders_clean.join(
    df_customers_clean, "Customer_ID", "left_anti"
).count()

orphan_products = df_orders_clean.join(
    df_products_clean, "Product_ID", "left_anti"
).count()

print("Orders with no matching Customer:", orphan_customers)
print("Orders with no matching Product:", orphan_products)
# Should both print 0 if data is clean


# ================================================================
# CELL 7: Write Silver tables back to Lakehouse
# ================================================================
df_orders_clean.write.mode("overwrite").format("delta").saveAsTable("Silver_Orders")
df_customers_clean.write.mode("overwrite").format("delta").saveAsTable("Silver_Customers")
df_products_clean.write.mode("overwrite").format("delta").saveAsTable("Silver_Products")

print("Silver layer tables written successfully.")
