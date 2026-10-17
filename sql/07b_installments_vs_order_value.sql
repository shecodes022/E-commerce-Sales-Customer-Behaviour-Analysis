SELECT CASE WHEN p.payment_installments = 1 THEN '1x'
            WHEN p.payment_installments <= 3 THEN '2-3x'
            WHEN p.payment_installments <= 6 THEN '4-6x'
            ELSE '7-10x' END                  AS installment_plan,
       COUNT(*)                               AS payments,
       ROUND(AVG(p.payment_value), 2)         AS avg_order_value
FROM order_payments p
JOIN orders o ON o.order_id = p.order_id
WHERE p.payment_type = 'credit_card'
  AND o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY installment_plan
ORDER BY MIN(p.payment_installments);
