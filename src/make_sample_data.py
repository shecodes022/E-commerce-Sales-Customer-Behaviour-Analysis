"""
Synthetic stand-in for the Olist Brazilian E-commerce dataset.

Same table names, column names and data quirks as the real Kaggle files
(duplicate reviews, missing categories, impossible delivery dates, ...), so the
notebook runs end-to-end even before you download the real data.

!! This is FAKE data. Never publish findings computed from it. !!
"""
from pathlib import Path

import numpy as np
import pandas as pd

# (portuguese name, english name, popularity, median price R$, review penalty prob)
CATEGORIES = [
    ("cama_mesa_banho", "bed_bath_table", 10, 90, 0.04),
    ("beleza_saude", "health_beauty", 9.5, 110, 0.00),
    ("esporte_lazer", "sports_leisure", 8.5, 100, 0.00),
    ("informatica_acessorios", "computers_accessories", 8, 120, 0.03),
    ("moveis_decoracao", "furniture_decor", 8, 85, 0.10),
    ("utilidades_domesticas", "housewares", 7, 70, 0.02),
    ("relogios_presentes", "watches_gifts", 5.5, 190, 0.02),
    ("telefonia", "telephony", 4.5, 45, 0.10),
    ("automotivo", "auto", 4.2, 95, 0.02),
    ("brinquedos", "toys", 4, 80, 0.01),
    ("cool_stuff", "cool_stuff", 3.5, 100, 0.00),
    ("perfumaria", "perfumery", 3.4, 85, 0.00),
    ("bebes", "baby", 3.2, 90, 0.03),
    ("eletronicos", "electronics", 2.8, 60, 0.04),
    ("papelaria", "stationery", 2.5, 40, 0.00),
    ("fashion_bolsas_e_acessorios", "fashion_bags_accessories", 2.2, 75, 0.01),
    ("pet_shop", "pet_shop", 2.0, 70, 0.00),
    ("ferramentas_jardim", "garden_tools", 3.6, 80, 0.02),
    ("consoles_games", "consoles_games", 1.5, 130, 0.01),
    ("livros_interesse_geral", "books_general_interest", 1.2, 45, 0.00),
    ("malas_acessorios", "luggage_accessories", 1.1, 110, 0.00),
    ("eletrodomesticos", "small_appliances", 1.3, 150, 0.05),
    ("instrumentos_musicais", "musical_instruments", 0.7, 150, 0.00),
    ("construcao_ferramentas_construcao", "construction_tools_construction", 0.9, 90, 0.03),
    ("alimentos", "food", 0.6, 55, 0.00),
    ("pc_gamer", None, 0.05, 150, 0.00),  # missing from translation table, like the real data
]
STATES = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "ES", "PE", "CE", "PA", "AM"]
STATE_P = np.array([42, 13, 12, 6, 6, 4, 3.5, 2.2, 2.0, 2.0, 1.7, 1.3, 1.0, 0.6])
STATE_P = STATE_P / STATE_P.sum()
STATE_DAYS = dict(zip(STATES, [8, 12, 11, 14, 12, 13, 19, 12, 14, 13, 22, 23, 24, 27]))
STATE_CITIES = {
    "SP": ["sao paulo", "campinas", "santos", "guarulhos"],
    "RJ": ["rio de janeiro", "niteroi"],
    "MG": ["belo horizonte", "uberlandia"],
    "RS": ["porto alegre"], "PR": ["curitiba"], "SC": ["florianopolis"],
    "BA": ["salvador"], "DF": ["brasilia"], "GO": ["goiania"], "ES": ["vitoria"],
    "PE": ["recife"], "CE": ["fortaleza"], "PA": ["belem"], "AM": ["manaus"],
}


def _hex_ids(rng, n):
    return [f"{rng.integers(0, 2**62):016x}{i:016x}" for i in range(n)]


def _sample_ts(rng, n):
    months = pd.period_range("2017-01", "2018-08", freq="M")
    w = np.linspace(1.0, 3.0, len(months))
    w[list(months).index(pd.Period("2017-11"))] *= 1.8  # Black Friday spike
    w = w / w.sum()
    m = rng.choice(len(months), n, p=w)
    starts = pd.to_datetime([months[i].start_time for i in m])
    dim = np.array([months[i].days_in_month for i in m])
    day = (rng.random(n) * dim).astype(int)
    hour_w = np.array([1, .6, .3, .2, .2, .4, 1, 2, 3.5, 4.5, 5, 5, 4.5, 4.5, 5, 5, 4.8, 4.5, 4.3, 4.5, 5, 5, 4, 2.5])
    hour = rng.choice(24, n, p=hour_w / hour_w.sum())
    return (starts + pd.to_timedelta(day, "D") + pd.to_timedelta(hour, "h")
            + pd.to_timedelta(rng.integers(0, 3600, n), "s"))


def _build_orders(rng, ts, states):
    n = len(ts)
    base = np.array([STATE_DAYS[s] for s in states], dtype=float)
    factor = rng.lognormal(0, 0.5, n)
    shock = rng.random(n) < 0.04
    factor[shock] *= rng.uniform(1.8, 3.0, shock.sum())
    actual = np.maximum(2.0, base * factor)
    est = np.ceil(base * 1.7 + 5 + rng.normal(0, 2, n))
    status = rng.choice(["delivered", "shipped", "canceled", "unavailable", "invoiced", "processing"],
                        n, p=[.965, .012, .009, .006, .004, .004])
    delivered = pd.Series(ts + pd.to_timedelta(actual, "D"))
    delivered[status != "delivered"] = pd.NaT
    est_dt = (pd.Series(ts) + pd.to_timedelta(est, "D")).dt.normalize()
    approved = pd.Series(ts) + pd.to_timedelta(rng.integers(5, 600, n), "m")
    carrier = approved + pd.to_timedelta(rng.integers(1, 4, n), "D")
    late = ((delivered > est_dt) & (status == "delivered")).to_numpy()
    days_late = ((delivered - est_dt).dt.total_seconds() / 86400).fillna(0).to_numpy()
    return pd.DataFrame({
        "purchase": pd.Series(ts), "status": status, "approved": approved, "carrier": carrier,
        "delivered": delivered, "estimated": est_dt, "late": late, "days_late": days_late,
    })


def generate(out_dir, n_orders=20000, seed=42):
    rng = np.random.default_rng(seed)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    end = pd.Timestamp("2018-08-31 23:59:59")

    # ---------------- sellers & products ----------------
    n_sellers, n_prod = 320, 1800
    sellers = pd.DataFrame({
        "seller_id": _hex_ids(rng, n_sellers),
        "seller_zip_code_prefix": rng.integers(1000, 99999, n_sellers),
        "seller_state": rng.choice(STATES, n_sellers, p=STATE_P),
    })
    sellers["seller_city"] = [rng.choice(STATE_CITIES[s]) for s in sellers.seller_state]
    seller_w = rng.pareto(1.2, n_sellers) + 0.05
    seller_w /= seller_w.sum()

    cat_pop = np.array([c[2] for c in CATEGORIES], dtype=float)
    prod_cat = rng.choice(len(CATEGORIES), n_prod, p=cat_pop / cat_pop.sum())
    products = pd.DataFrame({
        "product_id": _hex_ids(rng, n_prod),
        "product_category_name": [CATEGORIES[i][0] for i in prod_cat],
        "product_name_lenght": rng.integers(20, 70, n_prod),
        "product_description_lenght": rng.integers(100, 2000, n_prod),
        "product_photos_qty": rng.integers(1, 8, n_prod),
        "product_weight_g": rng.integers(100, 12000, n_prod),
        "product_length_cm": rng.integers(10, 60, n_prod),
        "product_height_cm": rng.integers(2, 40, n_prod),
        "product_width_cm": rng.integers(8, 50, n_prod),
    })
    products.loc[rng.random(n_prod) < 0.02, "product_category_name"] = np.nan  # real data has ~1.5% missing
    prod_w = rng.pareto(1.5, n_prod) + 0.1
    prod_w /= prod_w.sum()
    translation = pd.DataFrame(
        [(c[0], c[1]) for c in CATEGORIES if c[1]],
        columns=["product_category_name", "product_category_name_english"])

    # ---------------- customers & orders ----------------
    n_unique = int(n_orders * 0.965)
    u_state = rng.choice(STATES, n_unique, p=STATE_P)
    first = _build_orders(rng, _sample_ts(rng, n_unique), u_state)
    first["uniq"] = np.arange(n_unique)

    # repeat purchases: customers with a late first delivery come back less often
    p_repeat = np.where(first.late, 0.020, 0.040)
    repeaters = first[rng.random(n_unique) < p_repeat].copy()
    second_ts = repeaters.purchase + pd.to_timedelta(rng.integers(20, 330, len(repeaters)), "D")
    second_ts = second_ts[second_ts < end]
    r2 = _build_orders(rng, second_ts.to_numpy(), u_state[repeaters.loc[second_ts.index, "uniq"]])
    r2["uniq"] = repeaters.loc[second_ts.index, "uniq"].to_numpy()
    third = r2[rng.random(len(r2)) < 0.15]
    third_ts = third.purchase + pd.to_timedelta(rng.integers(20, 200, len(third)), "D")
    third_ts = third_ts[third_ts < end]
    r3 = _build_orders(rng, third_ts.to_numpy(), u_state[third.loc[third_ts.index, "uniq"]])
    r3["uniq"] = third.loc[third_ts.index, "uniq"].to_numpy()

    orders = pd.concat([first, r2, r3], ignore_index=True)
    orders = orders[orders.purchase <= end].reset_index(drop=True)
    n = len(orders)
    orders["order_id"] = _hex_ids(rng, n)
    orders["customer_id"] = _hex_ids(rng, n)  # one customer_id per ORDER, like real Olist
    uniq_ids = _hex_ids(rng, n_unique)
    orders["customer_unique_id"] = [uniq_ids[i] for i in orders.uniq]
    orders["state"] = u_state[orders.uniq.to_numpy()]

    # dirty data on purpose, so the cleaning section has something to find
    deliv_idx = orders.index[orders.status == "delivered"].to_numpy()
    bad = rng.choice(deliv_idx, 6, replace=False)
    orders.loc[bad[:4], "delivered"] = orders.loc[bad[:4], "purchase"] - pd.Timedelta(days=1)
    orders.loc[bad[4:], "delivered"] = pd.NaT

    customers = (orders[["customer_id", "customer_unique_id", "state"]]
                 .rename(columns={"state": "customer_state"}).copy())
    customers["customer_zip_code_prefix"] = rng.integers(1000, 99999, n)
    customers["customer_city"] = [rng.choice(STATE_CITIES[s]) for s in customers.customer_state]
    messy = rng.random(n) < 0.03
    customers.loc[messy, "customer_city"] = customers.loc[messy, "customer_city"].str.upper() + " "
    customers = customers[["customer_id", "customer_unique_id", "customer_zip_code_prefix",
                           "customer_city", "customer_state"]]

    # ---------------- order items ----------------
    n_items = rng.choice([1, 2, 3], n, p=[.88, .09, .03])
    it = pd.DataFrame({"order_id": np.repeat(orders.order_id.to_numpy(), n_items)})
    it["order_item_id"] = it.groupby("order_id").cumcount() + 1
    it["state"] = np.repeat(orders.state.to_numpy(), n_items)
    pidx = rng.choice(n_prod, len(it), p=prod_w)
    it["product_id"] = products.product_id.to_numpy()[pidx]
    it["seller_id"] = sellers.seller_id.to_numpy()[rng.choice(n_sellers, len(it), p=seller_w)]
    cat_median = {c[0]: c[3] for c in CATEGORIES}
    med = products.product_category_name.map(cat_median).fillna(80).to_numpy()[pidx]
    it["price"] = np.round(np.maximum(5, rng.lognormal(np.log(med), 0.6)), 2)
    extra = it.state.map(lambda s: STATE_DAYS[s] * 0.5).to_numpy()
    it["freight_value"] = np.round(6 + 0.05 * it.price + rng.gamma(2, 3, len(it)) + extra, 2)
    ship = orders.set_index("order_id").carrier
    it["shipping_limit_date"] = it.order_id.map(ship)
    order_items = it[["order_id", "order_item_id", "product_id", "seller_id",
                      "shipping_limit_date", "price", "freight_value"]]

    # ---------------- payments ----------------
    totals = it.assign(t=it.price + it.freight_value).groupby("order_id").t.sum()
    ptype = rng.choice(["credit_card", "boleto", "voucher", "debit_card"], n, p=[.74, .19, .05, .02])
    tot = orders.order_id.map(totals).to_numpy()
    inst = np.where(ptype == "credit_card", np.clip(rng.poisson(tot / 60), 1, 10), 1)
    payments = pd.DataFrame({
        "order_id": orders.order_id, "payment_sequential": 1, "payment_type": ptype,
        "payment_installments": inst.astype(int), "payment_value": np.round(tot, 2)})

    # ---------------- reviews (quality depends on delivery lateness) ----------------
    first_cat = (it.drop_duplicates("order_id").set_index("order_id").product_id
                 .map(products.set_index("product_id").product_category_name))
    pen = {c[0]: c[4] for c in CATEGORIES}
    o = orders.copy()
    o["pen"] = o.order_id.map(first_cat).map(pen).fillna(0.02)
    has_review = (o.status.isin(["delivered", "canceled"])) & (rng.random(n) < 0.97)
    o = o[has_review].copy()
    dl = o.days_late.to_numpy()
    probs = np.where(dl[:, None] <= 0, [[.04, .02, .07, .20, .67]],
             np.where(dl[:, None] <= 3, [[.15, .10, .20, .25, .30]],
             np.where(dl[:, None] <= 7, [[.35, .20, .20, .15, .10]], [[.55, .20, .12, .08, .05]])))
    u = rng.random(len(o))[:, None]
    score = (u > np.cumsum(probs, axis=1)).sum(axis=1) + 1
    score = np.clip(score, 1, 5)
    hit = rng.random(len(o)) < o.pen.to_numpy()
    score = np.where(hit, np.maximum(1, score - 2), score)
    base_dt = o.delivered.fillna(o.purchase + pd.Timedelta(days=10))
    created = (base_dt + pd.to_timedelta(rng.integers(0, 3, len(o)), "D")).dt.normalize()
    answered = created + pd.to_timedelta(rng.integers(3600, 4 * 86400, len(o)), "s")
    reviews = pd.DataFrame({
        "review_id": _hex_ids(rng, len(o)), "order_id": o.order_id.to_numpy(), "review_score": score,
        "review_comment_title": np.nan, "review_comment_message": np.nan,
        "review_creation_date": created.to_numpy(), "review_answer_timestamp": answered.to_numpy()})
    dup = reviews.sample(frac=0.012, random_state=seed).copy()  # orders reviewed twice (real quirk)
    dup["review_id"] = _hex_ids(rng, len(dup))
    dup["review_score"] = rng.integers(1, 6, len(dup))
    dup["review_answer_timestamp"] = pd.to_datetime(dup.review_answer_timestamp) + pd.Timedelta(days=3)
    reviews = pd.concat([reviews, dup], ignore_index=True)

    # ---------------- write CSVs in real Olist format ----------------
    fmt = "%Y-%m-%d %H:%M:%S"
    out_orders = pd.DataFrame({
        "order_id": orders.order_id, "customer_id": orders.customer_id, "order_status": orders.status,
        "order_purchase_timestamp": orders.purchase.dt.strftime(fmt),
        "order_approved_at": orders.approved.dt.strftime(fmt),
        "order_delivered_carrier_date": orders.carrier.dt.strftime(fmt),
        "order_delivered_customer_date": orders.delivered.dt.strftime(fmt),
        "order_estimated_delivery_date": orders.estimated.dt.strftime(fmt)})
    order_items = order_items.assign(shipping_limit_date=pd.to_datetime(order_items.shipping_limit_date).dt.strftime(fmt))
    reviews["review_creation_date"] = pd.to_datetime(reviews.review_creation_date).dt.strftime(fmt)
    reviews["review_answer_timestamp"] = pd.to_datetime(reviews.review_answer_timestamp).dt.strftime(fmt)

    out_orders.to_csv(out / "olist_orders_dataset.csv", index=False)
    customers.to_csv(out / "olist_customers_dataset.csv", index=False)
    order_items.to_csv(out / "olist_order_items_dataset.csv", index=False)
    payments.to_csv(out / "olist_order_payments_dataset.csv", index=False)
    reviews.to_csv(out / "olist_order_reviews_dataset.csv", index=False)
    products.to_csv(out / "olist_products_dataset.csv", index=False)
    sellers.to_csv(out / "olist_sellers_dataset.csv", index=False)
    translation.to_csv(out / "product_category_name_translation.csv", index=False)
    (out / "README_SYNTHETIC.txt").write_text("FAKE sample data generated by src/make_sample_data.py. Do not publish findings from it.")
    return out


if __name__ == "__main__":
    print("Wrote sample data to", generate("data/sample"))
