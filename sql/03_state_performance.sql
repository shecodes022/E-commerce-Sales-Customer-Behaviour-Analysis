WITH sales AS (
    SELECT customer_state AS state,
           SUM(price)                         AS revenue,
           SUM(freight_value)                 AS freight,
           COUNT(DISTINCT customer_unique_id) AS customers
    FROM v_sales
    GROUP BY customer_state
),
logistics AS (
    SELECT customer_state AS state,
           AVG(delivery_days)   AS avg_delivery_days,
           100.0 * AVG(is_late) AS late_pct,
           AVG(review_score)    AS avg_review
    FROM v_delivered_orders
    GROUP BY customer_state
)
SELECT s.state,
       ROUND(s.revenue, 0)                              AS revenue,
       ROUND(100.0 * s.revenue / SUM(s.revenue) OVER (), 1) AS revenue_share_pct,
       s.customers,
       ROUND(100.0 * s.freight / s.revenue, 1)          AS freight_pct,
       ROUND(l.avg_delivery_days, 1)                    AS avg_delivery_days,
       ROUND(l.late_pct, 1)                             AS late_pct,
       ROUND(l.avg_review, 2)                           AS avg_review
FROM sales s
JOIN logistics l ON l.state = s.state
ORDER BY s.revenue DESC;
