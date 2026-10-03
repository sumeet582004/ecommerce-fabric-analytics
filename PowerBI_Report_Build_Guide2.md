# E-Commerce Fabric Project — Power BI Report Build Guide
Beginner-friendly, step-by-step. Follow top to bottom, don't skip steps.

---

## 0. Before you start — report-level settings

1. Open Power BI Desktop, connected live to the `e_commerce_sementic` semantic model (Direct Lake), as already set up.
2. On the **View** tab (top ribbon) → **Themes** → pick a clean theme close to teal/coral (matches your Supply Chain project's teal + pink/coral palette). If none matches, we'll set exact colors per visual later — don't worry about this now.
3. Still on **View** tab → make sure **Page view** is set to **Fit to page** (keeps every page the same size on any screen).
4. Right-click the **Page 1** tab at the bottom → **Rename page** → type `home`.
5. Format pane (paint-roller icon, right side) → with nothing selected, click on empty canvas → **Format your page** → **Canvas settings** → confirm size is **16:9** (this is default — 1280×720). Keep this for all 5 pages.
6. Add 4 more pages now (click **+** at the bottom, 4 times). Rename them in order:
   - `home`
   - `sales_overview`
   - `fulfillment_risk`
   - `customer_segmentation`
   - `discount_effectiveness`

This gives you the 5 tabs at the bottom you'll build one at a time.

---

## 1. All DAX measures — write these first, before any visual

**Why first:** visuals just point at a measure name. If the measure doesn't exist yet, the visual has nothing to show. Build the full measure list now, then every page after this is just drag-and-drop.

**How to create a measure (do this for every one below):**
1. In the **Data** pane (right side), click on the `fact_orders` table name (just select it, don't expand it).
2. Ribbon → **Home** tab → **New measure** (calculator icon).
3. A formula bar opens at the top of the canvas. Delete the placeholder text, paste the DAX given below, press **Enter**.
4. The new measure now appears inside `fact_orders` in the Data pane. Click on it once to select it.
5. In the **Properties** pane (right side, may need to expand it), find the field called **Home table** — leave as `fact_orders`. Find **Display Folder** and type the folder path exactly as given below (with the `\`) — this is what groups measures into folders like your Supply Chain project screenshot.
6. Also set **Format** in Properties: for revenue/currency measures pick `Currency`, for percentages pick `Percentage`, for plain counts pick `Whole Number`.

Do this 24 times, using the tables below. It's repetitive but mechanical — no thinking required, just follow each row.

### Folder: `Page 1 - Sales\Base`

| Measure name | DAX | Format |
|---|---|---|
| Total Revenue | `SUM(fact_orders[Final_Amount])` | Currency |
| Total Orders | `COUNTROWS(fact_orders)` | Whole Number |
| Total Profit | `SUM(fact_orders[Profit_Amount])` | Currency |

### Folder: `Page 1 - Sales\KPIs`

| Measure name | DAX | Format |
|---|---|---|
| Average Order Value | `DIVIDE([Total Revenue], [Total Orders])` | Currency |
| Gross Margin % | `DIVIDE([Total Profit], [Total Revenue])` | Percentage |
| Gross Margin Target % | `0.25` | Percentage |

### Folder: `Page 2 - Fulfillment\Base`

| Measure name | DAX | Format |
|---|---|---|
| Cancelled Orders | `SUM(fact_orders[Is_Cancelled])` | Whole Number |
| Returned Orders | `SUM(fact_orders[Is_Returned])` | Whole Number |
| Delivered Orders | `SUM(fact_orders[Is_Delivered])` | Whole Number |
| On-Time Deliveries | `CALCULATE(COUNTROWS(fact_orders), fact_orders[Delivery_On_Time] = "Yes")` | Whole Number |
| COD Orders | `CALCULATE([Total Orders], dim_payment_method[Payment_Method] = "COD")` | Whole Number |

### Folder: `Page 2 - Fulfillment\KPIs`

| Measure name | DAX | Format |
|---|---|---|
| Cancellation Rate | `DIVIDE([Cancelled Orders], [Total Orders])` | Percentage |
| Return Rate | `DIVIDE([Returned Orders], [Total Orders])` | Percentage |
| On-Time Delivery % | `DIVIDE([On-Time Deliveries], [Delivered Orders])` | Percentage |
| COD Share of Orders | `DIVIDE([COD Orders], [Total Orders])` | Percentage |
| On-Time Delivery Target % | `0.9` | Percentage |

### Folder: `Page 3 - Customer\Base`

| Measure name | DAX | Format |
|---|---|---|
| Total Customers | `DISTINCTCOUNT(fact_orders[Customer_Key])` | Whole Number |
| Repeat Customers | `VAR CustOrders = SUMMARIZE(fact_orders, fact_orders[Customer_Key], "OrderCount", COUNTROWS(fact_orders)) RETURN COUNTROWS(FILTER(CustOrders, [OrderCount] > 1))` | Whole Number |
| One-time Customers | `[Total Customers] - [Repeat Customers]` | Whole Number |

### Folder: `Page 3 - Customer\KPIs`

| Measure name | DAX | Format |
|---|---|---|
| Customer Retention Rate | `DIVIDE([Repeat Customers], [Total Customers])` | Percentage |
| Customer Lifetime Value | `DIVIDE([Total Revenue], [Total Customers])` | Currency |

### Folder: `Page 4 - Discount\Base`

| Measure name | DAX | Format |
|---|---|---|
| Total Discount | `SUM(fact_orders[Discount_Amount])` | Currency |
| Total Gross Amount | `SUM(fact_orders[Gross_Amount])` | Currency |
| Coupon Orders | `CALCULATE([Total Orders], fact_orders[Coupon_Used] = "Yes")` | Whole Number |

### Folder: `Page 4 - Discount\KPIs`

| Measure name | DAX | Format |
|---|---|---|
| Discount to Revenue Ratio | `DIVIDE([Total Discount], [Total Gross Amount])` | Percentage |
| Average Discount % | `AVERAGE(fact_orders[Discount_Percent])` | Percentage |
| Orders with Coupon % | `DIVIDE([Coupon Orders], [Total Orders])` | Percentage |
| Discount Ratio Target % | `0.15` | Percentage |

**Checkpoint:** Data pane → `fact_orders` → you should now see 4 folders (`Page 1 - Sales`, `Page 2 - Fulfillment`, `Page 3 - Customer`, `Page 4 - Discount`), each with `Base` and `KPIs` sub-folders, 28 measures total. If a folder name has a typo, click the measure → fix the **Display Folder** text in Properties, it moves automatically.

**Note on the 3 "Target" measures** (`Gross Margin Target %`, `On-Time Delivery Target %`, `Discount Ratio Target %`): these are plain constants, not calculations off your data — they exist only to draw the target line/band on gauge visuals in Section 2. The numbers (25%, 90%, 15%) come straight from your BRD's KPI table (Section 9).

---

## 2. Page-by-page layout

General rule for every page: **top strip = title/KPI cards, middle = main charts, bottom = supporting charts/filters.** This matches your Supply Chain project's pattern (title + insight cards on top, charts below).

Canvas is 1280×720 on every page. Positions below are approximate zones, not exact pixels — use the **Format pane → General → Properties → Position and Size** fields if you want exact numbers, but eyeballing it with Power BI's snap-to-grid is fine for a fresher project.

---

### PAGE 1 — `home` (cover page)

Reference: your Supply Chain project's cover page (icon + title top-left, illustration top-right, key insight cards row, page navigation cards row, footer banner).

```
┌─────────────────────────────────────────────────────────┐
│ [icon] E-COMMERCE ANALYTICS DASHBOARD      [illustration] │
│ Big Title: "Understanding Every Order."                   │
│ Subtitle: one-line project summary                        │
│ ─────                                                      │
│ KEY INSIGHTS                                               │
│ [card][card][card][card]   <- 4 small insight cards       │
│ ─────                                                      │
│ EXPLORE THE DASHBOARD                                      │
│ [Page 2 card] [Page 3 card] [Page 4 card] [Page 5 card]    │
│ ─────                                                      │
│ [footer banner strip]                                       │
└─────────────────────────────────────────────────────────┘
```

**Steps:**
1. Insert → **Text box** → type your title `Understanding Every Order.` → big bold font (32–40pt), dark teal color. Position: top-left.
2. Insert another text box below it for the one-line subtitle (14–16pt, grey).
3. Insert → **Shapes** → rectangle, top-right, as a placeholder block (you can add a downloaded icon/illustration image here later via Insert → Image; not mandatory for a fresher project, a clean colored rectangle is fine too).
4. For each of the 4 "Key Insight" cards: Insert → **Card visual** (New visual → Card), place in a row. Drag one KPI measure into each: `Total Revenue`, `Cancellation Rate`, `On-Time Delivery %`, `Customer Retention Rate`. These are your 4 headline numbers.
5. For each of the 4 "Explore the Dashboard" navigation cards: Insert a **rectangle shape**, add a text box on top naming the page (e.g. "Page 2 — Sales & Revenue"). Select the rectangle → Format pane → **Action** → turn **On** → Type: **Page navigation** → pick the target page (`sales_overview`, etc.). Now clicking that box in Reading view jumps to that page.
6. Bottom footer: one long thin rectangle shape, dark teal fill, with a text box on top for a closing line like "Data-Driven Decisions. Smarter Fulfillment."

---

Each page below has however many visuals the underlying tables genuinely support a distinct question for — not a fixed count. In practice that lands on 5 per page (plus the 4 KPI cards), because your model has enough dimensions (payment method, city tier, category, age, gender, time) to ask 5 non-overlapping questions per dashboard — but every visual listed earns its place by answering something the others on that page don't. Where an earlier draft of this guide had two visuals showing the same breakdown in different chart shapes, it's been replaced below. The mix (line/bar/donut plus treemap, waterfall, gauge, matrix with conditional formatting, scatter) is what makes this look like more than a basic project — but only where the data actually supports it.

---

### PAGE 2 — `sales_overview` (BRD Dashboard 1)

```
┌─────────────────────────────────────────────────────────┐
│ Title: Sales & Revenue Overview                            │
│ [Total Revenue][Total Orders][AOV][Gross Margin %]  <- cards│
│ ───────────────┬─────────────────┬───────────────────────  │
│ Revenue Trend   │ Revenue by       │ Revenue by City Tier    │
│ (line)          │ Category         │ (column)                │
│                 │ (treemap)        │                         │
│ ───────────────┴─────────────────┴───────────────────────  │
│  Profit by Category (waterfall)   │  Gross Margin % (gauge)  │
└─────────────────────────────────────────────────────────┘
```

**Visuals to build:**

1. **4 Card visuals** (top row): `Total Revenue`, `Total Orders`, `Average Order Value`, `Gross Margin %`.
2. **Revenue Trend — Line chart**: Insert → Line chart.
   - X-axis: `dim_date[Date]` (not `Month_Name` — Month_Name only has 12 values, so Jan 2022/2023/2024 would all merge into one point and destroy your 3-year trend; `Date` keeps every day distinct)
   - Y-axis (Values): `Total Revenue`
   - Shows the real 3-year trend and the festival-month (Oct–Nov) spikes in each year separately.
3. **Revenue by Category — Treemap** (uses the Gold table): Insert → New visual → **Treemap**.
   - Category (Group): `gold_monthly_category_summary[Category]`
   - Values: `gold_monthly_category_summary[Total_Revenue]`
   - Treemap draws each category as a rectangle sized by revenue — a single glance shows which categories dominate, and it looks noticeably more polished than a plain bar chart.
4. **Revenue by City Tier — Column chart**:
   - X-axis: `dim_customer[City_Tier]`
   - Y-axis: `Total Revenue`
5. **Profit by Category — Waterfall chart**: Insert → New visual → **Waterfall**.
   - Category (Breakdown): `dim_product[Category]`
   - Y-axis (Values): `Total Profit`
   - A waterfall shows each category as a step that adds to (or subtracts from) the running total profit — this is the single visual most likely to make an interviewer stop scrolling and ask about it.
6. **Gross Margin % — Gauge**: Insert → New visual → **Gauge**.
   - Value: `Gross Margin %`
   - Target value: `Gross Margin Target %`
   - Minimum: 0, Maximum: 1 (set both in the Fields well — gauge needs an explicit max since it's a fraction 0–1)
   - The needle position vs the target tick mark instantly tells a viewer whether margin is on track.

---

### PAGE 3 — `fulfillment_risk` (BRD Dashboard 2 — this is your core finding)

```
┌─────────────────────────────────────────────────────────┐
│ Title: Order Fulfillment & Risk                            │
│ [Cancellation Rate][Return Rate][On-Time %][COD Share] <-cards│
│ ───────────────┬─────────────────┬───────────────────────  │
│ Cancellation by │ Cancellation     │ Decomposition tree:     │
│ Payment Method  │ Rate Trend       │ what drives              │
│ & City Tier     │ over time (line) │ cancellations             │
│ (clustered bar) │                  │                          │
│ ───────────────┴─────────────────┴───────────────────────  │
│ Return Rate by Category (bar)  │  On-Time Delivery % (gauge)  │
└─────────────────────────────────────────────────────────┘
```

Note on why this changed from an earlier draft: a Matrix breaking Payment Method × City Tier down was considered here, but that's the exact same two fields already in the bar chart above — same data, just a different chart shape. That's decoration, not new information, so it's dropped. In its place is the trend line your BRD's own Dashboard 2 spec asked for (Section 14: "trend line"), which the earlier draft had missed entirely — it tells you whether cancellations are getting better or worse over the 3 years, something the bar chart (a snapshot) can't show.

**Visuals to build:**

1. **4 Card visuals**: `Cancellation Rate`, `Return Rate`, `On-Time Delivery %`, `COD Share of Orders`.
2. **Cancellation Rate by Payment Method — Clustered bar chart** (the single most important chart in your whole project):
   - Insert → Clustered bar chart
   - Y-axis: `gold_payment_risk_summary[Payment_Method]`
   - X-axis (Values): `gold_payment_risk_summary[Cancellation_Rate]`
   - Legend: `gold_payment_risk_summary[City_Tier]`
3. **Cancellation Rate Trend — Line chart** (new — answers "is the problem improving or worsening", which the bar chart above can't):
   - Insert → Line chart
   - X-axis: `dim_date[Date]` (not `Month_Name`, same reason as Page 2 — keeps the 3 years separate instead of merging into 12 points)
   - Y-axis (Values): `Cancellation Rate`
   - This uses `fact_orders` directly (via the `Cancellation Rate` measure), not a Gold table — so it's also proof you can build a trend straight off the fact table, not just off pre-aggregated data.
4. **Return Rate by Category — Bar chart**:
   - Y-axis: `gold_monthly_category_summary[Category]`
   - X-axis (Values): `gold_monthly_category_summary[Return_Rate]`
   - Sort descending, so the worst-returning category is on top.
5. **Decomposition tree**:
   - Insert → New visual → Decomposition tree
   - Analyze field: `Cancelled Orders`
   - Explain by: `dim_payment_method[Payment_Method]`, `dim_customer[City_Tier]`, `dim_product[Category]`
6. **On-Time Delivery % — Gauge**:
   - Value: `On-Time Delivery %`, Target: `On-Time Delivery Target %`, Minimum 0, Maximum 1.

---

### PAGE 4 — `customer_segmentation` (BRD Dashboard 3)

```
┌─────────────────────────────────────────────────────────┐
│ Title: Customer Segmentation & Retention                   │
│ [Total Customers][Repeat Customers][Retention %][CLV] <-cards│
│ ───────────────┬─────────────────┬───────────────────────  │
│ Customers by    │ Customers by     │ Repeat vs One-time      │
│ Age Group (bar) │ Gender (donut)   │ (donut)                  │
│ ───────────────┴─────────────────┴───────────────────────  │
│ Top Cities by Customers (treemap)  │ City Tier summary (matrix)│
└─────────────────────────────────────────────────────────┘
```

**Visuals to build:**

1. **4 Card visuals**: `Total Customers`, `Repeat Customers`, `Customer Retention Rate`, `Customer Lifetime Value`.
2. **Customers by Age Group — Bar chart**:
   - X-axis: `dim_customer[Age_Group]`, Y-axis: `Total Customers`
3. **Customers by Gender — Donut chart**:
   - Legend: `dim_customer[Gender]`, Values: `Total Customers`
4. **Repeat vs One-time — Donut chart** (no extra column needed — Power BI can slice a donut by two different measures instead of one column):
   - Insert → Donut chart
   - Values: drag in **both** `Repeat Customers` and `One-time Customers` — Power BI automatically uses the two measure names as the legend, splitting the donut between them.
5. **Top Cities by Customers — Treemap**:
   - Category (Group): `dim_customer[City]`
   - Values: `Total Customers`
   - This surfaces your top customer cities visually, sized by count, without needing a map visual (which needs geo-recognition and can be unreliable).
6. **City Tier Summary — Matrix with conditional formatting**:
   - Rows: `dim_customer[City_Tier]`
   - Values: `Total Customers`, `Repeat Customers`, `Customer Retention Rate`
   - Format pane → **Cell elements** → turn on for `Customer Retention Rate` → **Data bars**. Same trick as Page 3 — turns a plain grid into something that reads at a glance.

---

### PAGE 5 — `discount_effectiveness` (BRD Dashboard 4)

```
┌─────────────────────────────────────────────────────────┐
│ Title: Discount & Promotion Effectiveness                  │
│ [Total Discount][Discount:Revenue][Avg Discount %][Coupon %]│
│ ───────────────┬─────────────────┬───────────────────────  │
│ Avg Discount %  │ AOV: Coupon vs   │ Avg Discount % by       │
│ by Month (line) │ No Coupon        │ Category (bar)           │
│                 │ (column)         │                          │
│ ───────────────┴─────────────────┴───────────────────────  │
│ Discount % vs Cancellation Rate (scatter) │ Discount:Revenue (gauge)│
└─────────────────────────────────────────────────────────┘
```

**Visuals to build:**

1. **4 Card visuals**: `Total Discount`, `Discount to Revenue Ratio`, `Average Discount %`, `Orders with Coupon %`.
2. **Avg Discount % Trend — Line chart**:
   - X-axis: `dim_date[Date]` (not `Month_Name`, same reason as the other trend charts — keeps 2022/2023/2024 separate)
   - Y-axis: `Average Discount %`
   - Should visibly spike Oct–Nov each year, matching the festival-discount pattern built into your data.
3. **AOV: Coupon vs No Coupon — Clustered column chart**:
   - X-axis: `fact_orders[Coupon_Used]`, Y-axis: `Average Order Value`
4. **Avg Discount % by Category — Bar chart**:
   - Y-axis: `dim_product[Category]`, X-axis (Values): `Average Discount %`
5. **Discount % vs Cancellation Rate — Scatter chart** (the advanced visual for this page — shows a real correlation, not just a ranking):
   - Insert → New visual → **Scatter chart**
   - Values (this becomes the dots): `dim_product[Category]`
   - X-axis: `Average Discount %`
   - Y-axis: `Cancellation Rate`
   - Each dot is one category, positioned by how much it's discounted vs how often it cancels — if there's a pattern (heavier discounts near higher cancellation), it'll be visible immediately.
6. **Discount to Revenue Ratio — Gauge**:
   - Value: `Discount to Revenue Ratio`, Target: `Discount Ratio Target %`, Minimum 0, Maximum 0.5 (discount ratio won't realistically exceed 50%, so this range makes the needle movement readable).

---

## 3. Professional polish (production-grade touches)

Do this **after** Section 2 is fully built (all 5 pages, all visuals in place) and **before** Section 4 (formatting pass). Order matters here — the reset button in 3.5 needs to capture a state where everything else already exists.

### 3.1 Mark `dim_date` as a Date Table (required before 3.2)

Time intelligence functions (`PREVIOUSMONTH`, `SAMEPERIODLASTYEAR`) need Power BI to know which table is your calendar and which column is the actual date.

1. Go to **Model view**.
2. Click the `dim_date` table (select the table itself, not a column).
3. Ribbon → **Table tools** tab → **Mark as date table** → toggle **On**.
4. In the dialog, pick the date column: `Date`.
5. Click **Mark**. Power BI checks that every calendar day is present with no gaps — your `dim_date` covers every day from 2022-01-01 to 2024-12-31 with no gaps, so this will pass cleanly.

### 3.2 Time Intelligence measures

**Folder:** `Page 1 - Sales\Time Intelligence`

| Measure name | DAX | Format |
|---|---|---|
| Previous Month Revenue | `CALCULATE([Total Revenue], PREVIOUSMONTH(dim_date[Date]))` | Currency |
| MoM Revenue Growth % | `DIVIDE([Total Revenue] - [Previous Month Revenue], [Previous Month Revenue])` | Percentage |
| Previous Year Revenue | `CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[Date]))` | Currency |
| YoY Revenue Growth % | `DIVIDE([Total Revenue] - [Previous Year Revenue], [Previous Year Revenue])` | Percentage |
| Cumulative Revenue | `CALCULATE([Total Revenue], FILTER(ALL(dim_date), dim_date[Date] <= MAX(dim_date[Date])))` | Currency |

**Expected blanks, not bugs:** January 2022 is the very first month in your data, so `Previous Month Revenue`, `MoM Revenue Growth %`, `Previous Year Revenue`, and `YoY Revenue Growth %` will all show blank for that month (and the whole of 2022 for the YoY ones) — there's nothing before it to compare against. This is correct behavior, not something to fix.

**Where to use these** — added without creating a redundant new chart:
1. Go back to `sales_overview` → your existing **Revenue Trend** line chart (Section 2, visual #2) → change its visual type to **Line and stacked column chart** (a combo chart).
   - Column values: `Total Revenue`
   - Line values: `Cumulative Revenue`
   - X-axis stays `dim_date[Date]`
   - This turns one existing chart into two insights (period revenue + running total) instead of adding a new box to an already-full page.
2. On the same page, add **2 more small Card visuals** next to your existing 4 KPI cards: `MoM Revenue Growth %` and `YoY Revenue Growth %`. These are genuinely new information (a growth rate, not a repeat of the revenue level already shown), so they earn their place.

### 3.3 Dynamic titles

A dynamic title is just a text measure that changes based on what's filtered, bound to a visual's title through the `fx` button. One flagship measure per dashboard page is enough — don't do this for every single visual, that's effort for no real benefit.

**Folder:** `_Report Controls\Dynamic Titles`

| Measure name | DAX |
|---|---|
| Sales Page Title | `"Sales & Revenue Overview — " & IF(ISFILTERED(dim_date[Year]), SELECTEDVALUE(dim_date[Year]), "All Years")` |
| Fulfillment Page Title | `"Order Fulfillment & Risk — " & IF(ISFILTERED(dim_payment_method[Payment_Method]), SELECTEDVALUE(dim_payment_method[Payment_Method]), "All Payment Methods")` |
| Customer Page Title | `"Customer Segmentation & Retention — " & IF(ISFILTERED(dim_customer[City_Tier]), SELECTEDVALUE(dim_customer[City_Tier]), "All City Tiers")` |
| Discount Page Title | `"Discount & Promotion Effectiveness — " & IF(ISFILTERED(dim_product[Category]), SELECTEDVALUE(dim_product[Category]), "All Categories")` |

**How to bind one to a title (repeat for each page's title text box):**
1. Click the page title text box (from Section 2's title step).
2. Format pane → **Title** (or if it's a plain text box, delete it and use a **Card** visual with **Category label off** instead — text boxes can't bind to measures, only proper visuals can).
   - Simplest fix: use a **Card visual** for each page title instead of a text box, drag in the matching measure above. This is a small change from Section 2, but it's what makes the title dynamic.
3. Format the card's font size large (28–32pt) so it still reads as a title, not a KPI number.

### 3.4 Global Year slicer with Sync Slicers

1. Go to `sales_overview` (build the slicer here first).
2. Insert → **Slicer** → drag `dim_date[Year]` into it. Place it top-right of the page, small.
3. Ribbon → **View** tab → **Sync slicers** → this opens a pane with two columns per page: a sync checkbox and a visibility checkbox.
4. Tick **Sync** for: `sales_overview`, `fulfillment_risk`, `customer_segmentation`, `discount_effectiveness`.
5. **Do not tick `home`** — it has no data visuals (just cards and navigation boxes), so syncing a filter to it does nothing useful.
6. Optionally untick **Visible** on pages where you don't want the slicer box to visually repeat, while keeping it synced (the filter still applies even if hidden) — useful if a page's layout doesn't have room for it.

### 3.5 "Clear All Filters" reset button

Build this **last**, after every other visual, slicer, and filter on every page already exists — the bookmark needs to capture the true default state.

1. Go to `sales_overview`. Make sure nothing is currently filtered or cross-highlighted (click on empty canvas to clear any selection).
2. **View** tab → **Bookmarks** → **Bookmarks pane** → **Add**. A bookmark named "Bookmark 1" appears — rename it to `Reset`.
3. Right-click the `Reset` bookmark → confirm **Data** is checked (this is what captures "no filters applied"), leave **Display** and **Current Page** unchecked so it doesn't also force you back to this specific page.
4. Insert → **Buttons** → **Blank button**. Resize it small, place it near the slicer (top-right). Add a text label on top: "Reset filters".
5. With the button selected → Format pane → **Action** → toggle **On** → Type: **Bookmark** → Bookmark: `Reset`.
6. Copy this button (Ctrl+C) and paste it (Ctrl+V) onto the other 3 dashboard pages, in the same position, so it's available everywhere the slicer is.

### 3.6 Keep the filter pane clean — where secondary filters belong

Your BRD (Section 14) lists different secondary filters per dashboard: Payment Method and City Tier for Fulfillment, Gender/Age for Customer, Coupon_Used for Discount. Don't turn every one of these into an on-canvas slicer box — that clutters the 1280×720 canvas fast. Instead:

1. On each page, open the **Filters** pane (right side, may need **View → Filters** to show it).
2. Drag that page's secondary fields (e.g. on `fulfillment_risk`: `dim_payment_method[Payment_Method]`, `dim_customer[City_Tier]`) into the **Filters on this page** section.
3. Click each filter card → set **Filter type: Basic filtering** so a viewer gets a clean checklist dropdown.
4. Leave the **Filters on this visual** section alone unless one specific chart needs its own filter that shouldn't affect the rest of the page.
5. Result: only the synced Year slicer and the Reset button live on the canvas itself; everything else is one click away in the Filters pane, keeping every page visually clean.

---

## 4. Formatting pass (do this after all 5 pages have their visuals)

For every visual on every page:
1. Click the visual → Format pane (paint-roller icon) → **General** → **Title** → turn on, type a short clear title (e.g. "Revenue Trend by Month").
2. **Data labels** → turn On for card visuals and bar charts so numbers are visible without hovering.
3. **Colors**: pick 2–3 consistent colors across the whole report (e.g. dark teal for primary, coral/pink for a highlight or negative metric like cancellation). Set this once on one visual, then use Format pane → **...** → **Copy formatting** (or manually repeat) on the others so every page looks consistent.
4. Align cards in a row: select all card visuals on a page (Ctrl+click each) → ribbon **Format** tab (visual tools) → **Align** → **Align top**, then **Distribute horizontally**.

---

## 5. Final checklist before you save

- [ ] All 5 pages built, named `home`, `sales_overview`, `fulfillment_risk`, `customer_segmentation`, `discount_effectiveness`
- [ ] 28 core measures created, all inside `fact_orders`, grouped into the 4 folders with `Base`/`KPIs` sub-folders
- [ ] Each of the 4 dashboard pages (2–5) has its 4 KPI cards plus a set of main visuals where none of them duplicate what another visual on the same page already shows — across the report this includes at least one treemap, one waterfall or scatter, one gauge, and one matrix with conditional formatting
- [ ] All trend/line charts use `dim_date[Date]` on the axis, not `Month_Name` — otherwise 2022/2023/2024 collapse into the same 12 points
- [ ] Both Gold tables (`gold_monthly_category_summary`, `gold_payment_risk_summary`) are each used in at least one visual (Page 2 and Page 3) — so they aren't sitting unused in the model
- [ ] `dim_date` marked as a Date Table (Section 3.1), done before any time intelligence measure was tested
- [ ] 5 Time Intelligence measures built, `sales_overview` revenue chart converted to a combo chart with Cumulative Revenue, 2 growth-rate cards added
- [ ] 4 dynamic title measures built and bound to a Card-visual title on each dashboard page (not a plain text box)
- [ ] Year slicer built once, synced across the 4 dashboard pages (not `home`)
- [ ] Reset button built last, present on all 4 dashboard pages, tested by filtering something and confirming the button clears it
- [ ] Secondary filters (Payment Method, City Tier, Gender, Coupon_Used) live in the Filters pane per page, not as extra on-canvas slicers
- [ ] Home page navigation cards click through to the correct pages
- [ ] Titles, data labels, and consistent colors applied on every visual
- [ ] Save as `.pbip` (File → Save As → Power BI Project files) — only after everything above is done
