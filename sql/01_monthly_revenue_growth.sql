WITH monthly AS (
    SELECT order_month,
           SUM(price)                  AS revenue,
           COUNT(DISTINCT order_id)    AS orders,
           COUNT(DISTINCT customer_unique_id) AS customers
    FROM v_sales
    GROUP BY order_month
)
SELECT order_month,
       ROUND(revenue, 2)                                  AS revenue,
       orders,
       customers,
       ROUND(revenue / orders, 2)                         AS avg_order_value,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
                   / LAG(revenue) OVER (ORDER BY order_month), 1) AS mom_growth_pct
FROM monthly
ORDER BY order_month;
