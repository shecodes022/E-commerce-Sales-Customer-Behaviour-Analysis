WITH seller_perf AS (
    SELECT seller_id,
           MAX(seller_state)           AS seller_state,
           SUM(price)                  AS revenue,
           COUNT(DISTINCT order_id)    AS orders,
           ROUND(AVG(review_score), 2) AS avg_review
    FROM v_sales
    GROUP BY seller_id
)
SELECT *,
       RANK()    OVER (ORDER BY revenue DESC) AS revenue_rank,
       NTILE(10) OVER (ORDER BY revenue DESC) AS revenue_decile
FROM seller_perf
ORDER BY revenue_rank;
