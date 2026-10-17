-- 1) Latest review per order. Some orders have several reviews -> keep the most recent
CREATE VIEW v_reviews_dedup AS
SELECT order_id, review_score
FROM (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id
                              ORDER BY review_answer_timestamp DESC, review_id) AS rn
    FROM reviews
)
WHERE rn = 1;

-- 2) Sales fact view: one row per order item (5 joins)
CREATE VIEW v_sales AS
SELECT
    oi.order_id,
    oi.order_item_id,
    o.order_status,
    o.order_purchase_timestamp                          AS purchase_ts,
    substr(o.order_purchase_timestamp, 1, 10)           AS purchase_date,
    substr(o.order_purchase_timestamp, 1, 7)            AS order_month,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    oi.seller_id,
    s.seller_state,
    oi.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value                         AS gmv,
    r.review_score
FROM order_items oi
JOIN orders o               ON o.order_id = oi.order_id
JOIN customers c            ON c.customer_id = o.customer_id
LEFT JOIN products p        ON p.product_id = oi.product_id
LEFT JOIN translation t     ON t.product_category_name = p.product_category_name
LEFT JOIN sellers s         ON s.seller_id = oi.seller_id
LEFT JOIN v_reviews_dedup r ON r.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01';

-- 3) Delivered-orders view: one row per order (CTE inside a view)
CREATE VIEW v_delivered_orders AS
WITH order_value AS (
    SELECT order_id, SUM(price) AS revenue, SUM(freight_value) AS freight, COUNT(*) AS items
    FROM order_items
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_purchase_timestamp                                                        AS purchase_ts,
    substr(o.order_purchase_timestamp, 1, 10)                                         AS purchase_date,
    ROUND(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp), 2) AS delivery_days,
    ROUND(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date), 2) AS days_vs_estimate,
    CASE WHEN julianday(o.order_delivered_customer_date) > julianday(o.order_estimated_delivery_date)
         THEN 1 ELSE 0 END                                                            AS is_late,
    ov.revenue, ov.freight, ov.items,
    r.review_score
FROM orders o
JOIN customers c            ON c.customer_id = o.customer_id
JOIN order_value ov         ON ov.order_id = o.order_id
LEFT JOIN v_reviews_dedup r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01';
