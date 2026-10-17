WITH cat AS (
    SELECT category,
           SUM(price)                    AS revenue,
           COUNT(DISTINCT order_id)      AS orders,
           ROUND(AVG(review_score), 2)   AS avg_review
    FROM v_sales
    GROUP BY category
)
SELECT category, ROUND(revenue, 0) AS revenue, orders, avg_review,
       ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS pct_of_total,
       ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                   / SUM(revenue) OVER (), 2)           AS cumulative_pct
FROM cat
ORDER BY revenue DESC;
