WITH first_order AS (
    SELECT customer_unique_id, MIN(order_month) AS cohort_month
    FROM v_sales GROUP BY customer_unique_id
),
activity AS (
    SELECT DISTINCT s.customer_unique_id, f.cohort_month, s.order_month
    FROM v_sales s
    JOIN first_order f ON f.customer_unique_id = s.customer_unique_id
),
indexed AS (
    SELECT cohort_month, customer_unique_id,
           (CAST(substr(order_month, 1, 4) AS INT) - CAST(substr(cohort_month, 1, 4) AS INT)) * 12
         + (CAST(substr(order_month, 6, 2) AS INT) - CAST(substr(cohort_month, 6, 2) AS INT)) AS months_since
    FROM activity
)
SELECT cohort_month, months_since,
       COUNT(DISTINCT customer_unique_id) AS active_customers,
       FIRST_VALUE(COUNT(DISTINCT customer_unique_id))
            OVER (PARTITION BY cohort_month ORDER BY months_since) AS cohort_size
FROM indexed
GROUP BY cohort_month, months_since
ORDER BY cohort_month, months_since;
