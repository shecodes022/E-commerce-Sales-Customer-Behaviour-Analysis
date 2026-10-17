# Power BI dashboard guide (about 45 minutes)

Running the notebook creates ready-to-load CSVs in `powerbi/exports/`. The steps below are enough to build the
dashboard and screenshot it for your README. (Tableau users: same files, same logic; use the measures as calculated fields.)

## 1. Load the data
1. **Get Data → Text/CSV** and load these from `powerbi/exports/`: `fact_sales`, `fact_orders`, `rfm_customers`,
   `category_summary`, `state_summary`, `cohort_retention`, `seller_summary`.
2. In **Power Query**, set `purchase_date` (in `fact_sales` and `fact_orders`) to type **Date**.
3. Create a date table: **Modeling → New table**

```DAX
dim_date =
ADDCOLUMNS(
    CALENDAR(DATE(2017,1,1), DATE(2018,8,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "YYYY-MM"),
    "MonthNo", MONTH([Date]),
    "Weekday", FORMAT([Date], "ddd"),
    "WeekdayNo", WEEKDAY([Date], 2)
)
```
Select it → **Mark as date table**.

## 2. Model (Model view)
| From | To | Type |
|---|---|---|
| `dim_date[Date]` | `fact_sales[purchase_date]` | one-to-many |
| `dim_date[Date]` | `fact_orders[purchase_date]` | one-to-many |

Leave `rfm_customers`, `category_summary`, `state_summary`, `cohort_retention` and `seller_summary` as standalone
tables; they are already aggregated by the SQL in the notebook.

## 3. DAX measures (create a table called `_Measures`)
```DAX
Revenue           = SUM(fact_sales[price])
Orders            = DISTINCTCOUNT(fact_sales[order_id])
Customers         = DISTINCTCOUNT(fact_sales[customer_unique_id])
AOV               = DIVIDE([Revenue], [Orders])
Freight %         = DIVIDE(SUM(fact_sales[freight_value]), [Revenue])

Revenue LM        = CALCULATE([Revenue], DATEADD(dim_date[Date], -1, MONTH))
Revenue MoM %     = DIVIDE([Revenue] - [Revenue LM], [Revenue LM])
Revenue LY        = CALCULATE([Revenue], SAMEPERIODLASTYEAR(dim_date[Date]))
Revenue YoY %     = DIVIDE([Revenue] - [Revenue LY], [Revenue LY])

Avg Review        = AVERAGE(fact_orders[review_score])
Late Delivery %   = AVERAGE(fact_orders[is_late])
Avg Delivery Days = AVERAGE(fact_orders[delivery_days])
Bad Review %      =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_orders), fact_orders[review_score] <= 2),
        COUNTROWS(FILTER(fact_orders, NOT ISBLANK(fact_orders[review_score])))
    )

Repeat Rate       =
    DIVIDE(
        CALCULATE(COUNTROWS(rfm_customers), rfm_customers[frequency] > 1),
        COUNTROWS(rfm_customers)
    )
```

## 4. Page layout
**Page 1: Executive Overview**
- Top row: 6 **Card** visuals → Revenue, Orders, Customers, AOV, Avg Review, Late Delivery %
- Left: **Line and clustered column chart** (x = `dim_date[Month]`, columns = Revenue, line = Revenue MoM %)
- Right: **Bar chart** of the top 10 `fact_sales[category]` by Revenue
- Slicers: Year, `customer_state`

**Page 2: Delivery & Customer Experience**
- **Column chart**: Avg Review for Late vs On-time (`fact_orders[is_late]`), or bin `days_vs_estimate`
- **Scatter**: `state_summary`, x = avg_delivery_days, y = avg_review, size = revenue, details = state
- **Filled map**: `customer_state` shaded by Late Delivery %

**Page 3: Customers & Retention**
- **Bar chart**: customers by `rfm_customers[segment]`
- **Table**: segment, customers, revenue, avg spend (add conditional formatting)
- **Matrix**: `cohort_retention`, rows = cohort_month, columns = months_since, values = retention_pct (heat-map conditional formatting)
- **Card**: Repeat Rate

**Page 4: Sellers & Categories**
- **Scatter**: `seller_summary`, orders vs avg_review, colour by revenue_decile
- **Table**: top 10 sellers by revenue

## 5. Make it look professional
- Use one consistent theme. Suggested colours: blue `#2563eb`, orange `#f59e0b`, red `#dc2626`.
- Give every page a **title that states the insight** ("Late deliveries drive a disproportionate share of bad reviews") rather than a label ("Delivery analysis").
- Align everything to the grid, keep fonts consistent, and add a one-line takeaway text box per page.
- Add **bookmarks + buttons** for navigation if you want to go a step further.

## 6. Add it to your portfolio
1. Take one screenshot per page into `images/powerbi_page1.png`, `powerbi_page2.png`, and so on.
2. Embed them near the top of your README, right under the title.
3. Save the `.pbix` into the `powerbi/` folder and export **File → Export → PDF** as a backup.
4. Optional: **Publish → Publish to web** and add the link. Only do this with public data like Olist.
