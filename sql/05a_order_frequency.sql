WITH cust AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS n_orders, SUM(price) AS spend
    FROM v_sales GROUP BY customer_unique_id
)
SELECT CASE WHEN n_orders = 1 THEN '1 order' WHEN n_orders = 2 THEN '2 orders' ELSE '3+ orders' END AS segment,
       COUNT(*)                                             AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)   AS pct_customers,
       ROUND(SUM(spend), 0)                                 AS revenue,
       ROUND(100.0 * SUM(spend) / SUM(SUM(spend)) OVER (), 1) AS pct_revenue
FROM cust GROUP BY segment ORDER BY segment;
