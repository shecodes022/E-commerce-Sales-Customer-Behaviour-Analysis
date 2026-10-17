SELECT CAST(strftime('%w', purchase_ts) AS INT) AS weekday,
       CAST(strftime('%H', purchase_ts) AS INT) AS hour,
       COUNT(DISTINCT order_id)                 AS orders
FROM v_sales
GROUP BY weekday, hour;
