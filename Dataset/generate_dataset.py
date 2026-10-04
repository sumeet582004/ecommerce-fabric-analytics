"""
Synthetic Indian E-Commerce Dataset Generator
Jan 2022 - Dec 2024 (3 years)

Realistic business logic baked in:
- COD orders have higher cancellation rate than digital payments
- Festival months (Oct-Nov: Diwali season) have sales spikes
- Tier 2/3 cities skew more towards COD; Tier 1 skews digital
- Repeat customers vs one-time customers (retention pattern)
- Category-wise price ranges and seasonality (Fashion spikes in festival season,
  Electronics spikes in Jan/Republic Day sale and Oct/Diwali)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ---------------------------------------------------------------
# 1. CUSTOMERS TABLE
# ---------------------------------------------------------------
N_CUSTOMERS = 5000

cities_tier1 = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata"]
cities_tier2 = ["Nagpur", "Indore", "Bhopal", "Coimbatore", "Vadodara", "Nashik",
                "Aurangabad", "Rajkot", "Ranchi", "Jodhpur", "Amritsar", "Raipur"]
cities_tier3 = ["Latur", "Akola", "Bhavnagar", "Sagar", "Rewa", "Ratlam",
                "Karimnagar", "Hisar", "Rohtak", "Bilaspur", "Ambala", "Shillong"]

states_map = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra",
    "Nashik": "Maharashtra", "Aurangabad": "Maharashtra", "Akola": "Maharashtra",
    "Delhi": "Delhi", "Bangalore": "Karnataka", "Hyderabad": "Telangana",
    "Karimnagar": "Telangana", "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu",
    "Kolkata": "West Bengal", "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
    "Sagar": "Madhya Pradesh", "Rewa": "Madhya Pradesh", "Vadodara": "Gujarat",
    "Rajkot": "Gujarat", "Bhavnagar": "Gujarat", "Ranchi": "Jharkhand",
    "Jodhpur": "Rajasthan", "Ratlam": "Madhya Pradesh", "Amritsar": "Punjab",
    "Raipur": "Chhattisgarh", "Bilaspur": "Chhattisgarh", "Hisar": "Haryana",
    "Rohtak": "Haryana", "Ambala": "Haryana", "Shillong": "Meghalaya",
    "Latur": "Maharashtra",
}

def pick_city_tier():
    r = np.random.rand()
    if r < 0.45:
        return random.choice(cities_tier1), "Tier 1"
    elif r < 0.75:
        return random.choice(cities_tier2), "Tier 2"
    else:
        return random.choice(cities_tier3), "Tier 3"

start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
total_days = (end_date - start_date).days

first_names_m = ["Rahul", "Amit", "Vikram", "Rohan", "Suresh", "Arjun", "Karan", "Sanjay", "Deepak", "Manoj"]
first_names_f = ["Priya", "Anjali", "Neha", "Pooja", "Sneha", "Kavita", "Ritu", "Divya", "Meera", "Shreya"]
last_names = ["Sharma", "Verma", "Patel", "Gupta", "Kumar", "Singh", "Reddy", "Iyer", "Nair", "Joshi"]

customers = []
for i in range(1, N_CUSTOMERS + 1):
    city, tier = pick_city_tier()
    state = states_map[city]
    signup_offset = np.random.randint(0, total_days - 30)  # leave room for at least one order after signup
    signup_date = start_date + timedelta(days=int(signup_offset))
    gender = random.choice(["Male", "Female"])
    first_name = random.choice(first_names_m if gender == "Male" else first_names_f)
    last_name = random.choice(last_names)
    age = int(np.clip(np.random.normal(32, 9), 18, 65))
    email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
    customers.append({
        "Customer_ID": f"CUST{i:05d}",
        "Customer_Name": f"{first_name} {last_name}",
        "Gender": gender,
        "Age": age,
        "Email": email,
        "City": city,
        "State": state,
        "City_Tier": tier,
        "Signup_Date": signup_date.date().isoformat(),
    })

df_customers = pd.DataFrame(customers)

# ---------------------------------------------------------------
# 2. PRODUCTS TABLE
# ---------------------------------------------------------------
categories = {
    "Electronics": (500, 45000),
    "Fashion": (299, 4999),
    "Grocery": (49, 1499),
    "Home & Kitchen": (199, 12000),
    "Beauty & Personal Care": (99, 2999),
    "Mobiles & Accessories": (299, 60000),
    "Sports & Fitness": (199, 8999),
    "Books & Stationery": (49, 1999),
}

N_PRODUCTS = 400

sub_categories = {
    "Electronics": ["Television", "Laptop", "Camera", "Speaker", "Headphones"],
    "Fashion": ["Men's Wear", "Women's Wear", "Footwear", "Watches", "Bags"],
    "Grocery": ["Staples", "Snacks", "Beverages", "Dairy", "Personal Hygiene"],
    "Home & Kitchen": ["Cookware", "Furniture", "Decor", "Storage", "Appliances"],
    "Beauty & Personal Care": ["Skincare", "Haircare", "Makeup", "Fragrance", "Grooming"],
    "Mobiles & Accessories": ["Smartphones", "Chargers", "Cases", "Earphones", "Power Banks"],
    "Sports & Fitness": ["Fitness Equipment", "Sportswear", "Outdoor Gear", "Cycling", "Yoga"],
    "Books & Stationery": ["Fiction", "Academic", "Notebooks", "Pens & Pencils", "Art Supplies"],
}

brands_by_cat = {
    "Electronics": ["Sony", "LG", "Samsung", "Philips", "Boat"],
    "Fashion": ["Levis", "H&M", "Allen Solly", "Puma", "Van Heusen"],
    "Grocery": ["Tata", "Amul", "ITC", "Patanjali", "Nestle"],
    "Home & Kitchen": ["Prestige", "Milton", "IKEA", "Cello", "Wonderchef"],
    "Beauty & Personal Care": ["Lakme", "Nivea", "Mamaearth", "L'Oreal", "Himalaya"],
    "Mobiles & Accessories": ["Samsung", "Xiaomi", "Boat", "Realme", "OnePlus"],
    "Sports & Fitness": ["Nike", "Adidas", "Decathlon", "Reebok", "Cosco"],
    "Books & Stationery": ["Penguin", "Classmate", "Camlin", "Faber-Castell", "HarperCollins"],
}

products = []
prod_id = 1
for cat, (lo, hi) in categories.items():
    n_this_cat = N_PRODUCTS // len(categories)
    for _ in range(n_this_cat):
        price = round(np.random.uniform(lo, hi), 2)
        cost_price = round(price * np.random.uniform(0.55, 0.80), 2)  # margin 20-45%
        sub_cat = random.choice(sub_categories[cat])
        brand = random.choice(brands_by_cat[cat])
        rating = round(np.random.uniform(2.5, 5.0), 1)
        stock_qty = np.random.randint(0, 500)
        products.append({
            "Product_ID": f"PROD{prod_id:04d}",
            "Category": cat,
            "Sub_Category": sub_cat,
            "Brand": brand,
            "Price": price,
            "Cost_Price": cost_price,
            "Product_Rating": rating,
            "Stock_Quantity": stock_qty,
        })
        prod_id += 1

df_products = pd.DataFrame(products)

# ---------------------------------------------------------------
# 3. ORDERS TABLE
# ---------------------------------------------------------------
N_ORDERS = 60000

payment_methods = ["COD", "UPI", "Credit/Debit Card", "Wallet"]

def payment_method_for_tier(tier):
    # Tier 1: mostly digital. Tier 2/3: more COD.
    if tier == "Tier 1":
        return np.random.choice(payment_methods, p=[0.25, 0.40, 0.25, 0.10])
    elif tier == "Tier 2":
        return np.random.choice(payment_methods, p=[0.50, 0.30, 0.12, 0.08])
    else:
        return np.random.choice(payment_methods, p=[0.68, 0.20, 0.07, 0.05])

def month_weight(month):
    # Festival season boost: Oct-Nov (Diwali), smaller boost Jan (Republic Day/New Year sales)
    weights = {1: 1.2, 2: 0.9, 3: 0.9, 4: 0.85, 5: 0.85, 6: 0.85,
               7: 0.9, 8: 0.9, 9: 1.0, 10: 1.6, 11: 1.5, 12: 1.1}
    return weights[month]

# Precompute daily weights across the whole span for sampling order dates
all_days = [start_date + timedelta(days=d) for d in range(total_days + 1)]
day_weights = np.array([month_weight(d.month) for d in all_days], dtype=float)
day_weights /= day_weights.sum()

# Give ~70% of customers repeat-purchase behaviour (2-15 orders), 30% one-time buyers
customer_ids = df_customers["Customer_ID"].tolist()
customer_tier_map = dict(zip(df_customers["Customer_ID"], df_customers["City_Tier"]))
customer_signup_map = dict(zip(df_customers["Customer_ID"], pd.to_datetime(df_customers["Signup_Date"])))

repeat_customers = set(np.random.choice(customer_ids, size=int(0.7 * N_CUSTOMERS), replace=False))

orders = []
order_id = 1
product_ids = df_products["Product_ID"].tolist()
product_price_map = dict(zip(df_products["Product_ID"], df_products["Price"]))
product_cat_map = dict(zip(df_products["Product_ID"], df_products["Category"]))

# Build an order-count target per customer so total ~= N_ORDERS
targets = []
for cid in customer_ids:
    if cid in repeat_customers:
        targets.append(np.random.randint(2, 16))
    else:
        targets.append(1)
targets = np.array(targets)
# scale so sum matches N_ORDERS roughly
scale = N_ORDERS / targets.sum()
targets = np.maximum(1, (targets * scale).astype(int))

return_reasons = ["Defective Product", "Wrong Item Delivered", "Size/Fit Issue",
                   "Not as Described", "Changed Mind", "Better Price Found Elsewhere"]

shipping_modes = ["Standard", "Express"]

for cid, n_orders_for_cust in zip(customer_ids, targets):
    signup = customer_signup_map[cid]
    tier = customer_tier_map[cid]
    days_since_signup = (end_date - signup).days
    if days_since_signup <= 0:
        continue
    for _ in range(n_orders_for_cust):
        offset = np.random.randint(0, days_since_signup)
        order_date = signup + timedelta(days=int(offset))

        pid = random.choice(product_ids)
        category = product_cat_map[pid]
        base_price = product_price_map[pid]
        qty = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.5, 0.2, 0.1, 0.1, 0.07, 0.03])
        gross_amount = round(base_price * qty, 2)

        # Discount: festival months get bigger discounts
        month_discount_boost = 0.15 if order_date.month in (10, 11) else 0.0
        discount_pct = round(np.clip(np.random.uniform(0, 0.25) + month_discount_boost, 0, 0.5), 2)
        discount_amount = round(gross_amount * discount_pct, 2)
        final_amount = round(gross_amount - discount_amount, 2)
        coupon_used = "Yes" if discount_pct > 0.10 else "No"

        payment = payment_method_for_tier(tier)

        # Cancellation logic: COD has higher cancel/return probability
        base_cancel_prob = {"COD": 0.18, "UPI": 0.05, "Credit/Debit Card": 0.06, "Wallet": 0.07}[payment]
        r = np.random.rand()
        if r < base_cancel_prob * 0.6:
            status = "Cancelled"
        elif r < base_cancel_prob:
            status = "Returned"
        else:
            status = "Delivered"

        shipping_mode = np.random.choice(shipping_modes, p=[0.75, 0.25])
        shipping_cost = 0.0 if final_amount > 999 else round(np.random.uniform(29, 99), 2)

        # Delivery days: express faster, tier 3 cities take longer
        base_days = 2 if shipping_mode == "Express" else 5
        tier_delay = {"Tier 1": 0, "Tier 2": 1, "Tier 3": 3}[tier]
        delivery_days = max(1, int(np.random.poisson(base_days + tier_delay)))
        delivery_date = order_date + timedelta(days=delivery_days)
        promised_days = base_days + tier_delay
        delivery_on_time = "Yes" if delivery_days <= promised_days + 1 else "No"

        return_reason = ""
        if status == "Returned":
            return_reason = random.choice(return_reasons)

        product_rating_given = ""
        if status == "Delivered" and np.random.rand() < 0.4:
            product_rating_given = int(np.clip(np.random.normal(4, 1), 1, 5))

        orders.append({
            "Order_ID": f"ORD{order_id:07d}",
            "Customer_ID": cid,
            "Product_ID": pid,
            "Category": category,
            "Order_Date": order_date.date().isoformat(),
            "Quantity": int(qty),
            "Gross_Amount": gross_amount,
            "Discount_Percent": discount_pct,
            "Discount_Amount": discount_amount,
            "Final_Amount": final_amount,
            "Coupon_Used": coupon_used,
            "Payment_Method": payment,
            "Shipping_Mode": shipping_mode,
            "Shipping_Cost": shipping_cost,
            "Delivery_Date": delivery_date.date().isoformat(),
            "Delivery_Days": delivery_days,
            "Delivery_On_Time": delivery_on_time,
            "Order_Status": status,
            "Return_Reason": return_reason,
            "Product_Rating_Given": product_rating_given,
        })
        order_id += 1

df_orders = pd.DataFrame(orders)

# ---------------------------------------------------------------
# SAVE FILES
# ---------------------------------------------------------------
out_dir = "/mnt/user-data/outputs"
df_customers.to_csv(f"{out_dir}/Customers.csv", index=False)
df_products.to_csv(f"{out_dir}/Products.csv", index=False)
df_orders.to_csv(f"{out_dir}/Orders.csv", index=False)

print("Customers:", df_customers.shape)
print("Products:", df_products.shape)
print("Orders:", df_orders.shape)
print(df_orders["Order_Status"].value_counts(normalize=True))
print(df_orders.groupby("Payment_Method")["Order_Status"].value_counts(normalize=True))
