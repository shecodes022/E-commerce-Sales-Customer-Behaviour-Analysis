SELECT p.payment_type,
       COUNT(DISTINCT p.order_id)                              AS orders,
       ROUND(SUM(p.payment_value), 0)                          AS total_value,
       ROUND(100.0 * SUM(p.payment_value) / SUM(SUM(p.payment_value)) OVER (), 1) AS pct_of_value,
       ROUND(AVG(p.payment_value), 2)                          AS avg_payment,
       ROUND(AVG(p.payment_installments), 1)                   AS avg_installments
FROM order_payments p
JOIN orders o ON o.order_id = p.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY p.payment_type
ORDER BY total_value DESC;
