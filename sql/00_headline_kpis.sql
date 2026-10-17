SELECT
    COUNT(DISTINCT order_id)                                  AS orders,
    COUNT(DISTINCT customer_unique_id)                        AS customers,
    COUNT(DISTINCT seller_id)                                 AS sellers,
    ROUND(SUM(price), 0)                                      AS revenue,
    ROUND(SUM(price) / COUNT(DISTINCT order_id), 2)           AS avg_order_value,
    ROUND(100.0 * SUM(freight_value) / SUM(price), 1)         AS freight_pct_of_revenue,
    ROUND(AVG(review_score), 2)                               AS avg_review_score
FROM v_sales;
