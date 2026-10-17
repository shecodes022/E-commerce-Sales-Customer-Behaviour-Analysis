WITH ref AS (
    SELECT MAX(purchase_ts) AS max_ts FROM v_sales
),
base AS (
    SELECT s.customer_unique_id,
           CAST(julianday(r.max_ts) - julianday(MAX(s.purchase_ts)) AS INT) AS recency_days,
           COUNT(DISTINCT s.order_id)                                       AS frequency,
           ROUND(SUM(s.price), 2)                                           AS monetary
    FROM v_sales s
    CROSS JOIN ref r
    GROUP BY s.customer_unique_id, r.max_ts
),
scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,     -- 5 = bought most recently
           CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 3 ELSE 5 END AS f_score,
           NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score      -- 5 = biggest spenders
    FROM base
)
SELECT *,
       CASE WHEN r_score >= 4 AND f_score >= 3 THEN 'Champions'
            WHEN f_score >= 3                  THEN 'Loyal'
            WHEN r_score >= 4 AND m_score >= 4 THEN 'New Big Spenders'
            WHEN r_score >= 4                  THEN 'Recent Customers'
            WHEN r_score <= 2 AND m_score >= 4 THEN 'At-Risk High Value'
            WHEN r_score <= 2                  THEN 'Hibernating'
            ELSE                                    'Needs Attention' END AS segment
FROM scored;
