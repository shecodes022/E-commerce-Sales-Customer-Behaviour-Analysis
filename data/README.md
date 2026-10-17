# Data

Download the **Brazilian E-Commerce Public Dataset by Olist** from Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Unzip these 8 files into this folder:

- olist_customers_dataset.csv
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_order_payments_dataset.csv
- olist_order_reviews_dataset.csv
- olist_products_dataset.csv
- olist_sellers_dataset.csv
- product_category_name_translation.csv

(`olist_geolocation_dataset.csv` is not used.)

If the files are missing, the notebook tries to download them with `kagglehub`, and if that fails it falls back to
**synthetic demo data** and prints a loud warning. Never publish findings computed from the synthetic data.
