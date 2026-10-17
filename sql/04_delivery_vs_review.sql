WITH bucketed AS (
    SELECT order_id, review_score,
           CASE WHEN days_vs_estimate <= -7 THEN '1. Early (7+ days)'
                WHEN days_vs_estimate <=  0 THEN '2. On time'
                WHEN days_vs_estimate <=  3 THEN '3. Late 1-3 days'
                WHEN days_vs_estimate <=  7 THEN '4. Late 4-7 days'
                ELSE                             '5. Late 7+ days' END AS delivery_bucket
    FROM v_delivered_orders
    WHERE review_score IS NOT NULL
)
SELECT delivery_bucket,
       COUNT(*)                                          AS orders,
       ROUND(AVG(review_score), 2)                       AS avg_review,
       ROUND(100.0 * SUM(review_score <= 2) / COUNT(*), 1) AS pct_bad_reviews_1_2_stars
FROM bucketed
GROUP BY delivery_bucket
ORDER BY delivery_bucket;
