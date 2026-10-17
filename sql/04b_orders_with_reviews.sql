SELECT order_id, is_late, review_score, days_vs_estimate FROM v_delivered_orders WHERE review_score IS NOT NULL;
