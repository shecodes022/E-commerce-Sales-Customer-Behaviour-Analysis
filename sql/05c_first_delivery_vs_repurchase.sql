WITH ranked AS (
    SELECT customer_unique_id, is_late,
           ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY purchase_ts) AS order_seq,
           COUNT(*)     OVER (PARTITION BY customer_unique_id)                      AS total_orders
    FROM v_delivered_orders
)
SELECT CASE WHEN is_late = 1 THEN 'Late first delivery' ELSE 'On-time first delivery' END AS first_experience,
       COUNT(*)                                                 AS customers,
       ROUND(100.0 * SUM(total_orders > 1) / COUNT(*), 2)       AS repeat_rate_pct
FROM ranked
WHERE order_seq = 1
GROUP BY first_experience;
