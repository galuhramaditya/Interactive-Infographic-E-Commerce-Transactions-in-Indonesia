import math
import streamlit as st
from datetime import date, timedelta, datetime
from collections import defaultdict

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Interactive Infographic (Streamlit + Vega-Lite)", layout="wide")

st.title("📌 Interactive Infographic: E-Commerce Transactions in Indonesia (2024)")
st.caption(
    "This visualization explores transactional patterns across regions, sales channels, "
    "and product tiers over time. Users can interactively filter, compare, and drill down "
    "into order volume, revenue, and average order value."
)

# ----------------------------
# DATA (self-contained)
# ----------------------------
@st.cache_data
def make_data(seed: int = 42):
    import random
    random.seed(seed)

    start = date(2024, 1, 1)
    days  = 365

    regions  = ["Jakarta", "West Java", "Central Java", "East Java", "Bali", "Sumatra"]
    channels = ["Organic", "Ads", "Affiliate", "Referral"]
    products = ["Basic", "Standard", "Premium"]

    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        # seasonality-ish signal
        seasonal = 1.0 + 0.25 * (1 + math.sin(2 * math.pi * i / 365))
        weekend  = 1.15 if d.weekday() >= 5 else 1.0

        for _ in range(random.randint(12, 30)):  # daily transactions
            region  = random.choice(regions)
            channel = random.choice(channels)
            product = random.choices(products, weights=[0.55, 0.32, 0.13], k=1)[0]

            base_orders = random.randint(1, 3)
            # product price bands
            if product == "Basic":
                price = random.randint(30_000, 70_000)
            elif product == "Standard":
                price = random.randint(70_000, 150_000)
            else:
                price = random.randint(150_000, 350_000)

            # channel uplift
            ch_uplift  = {"Organic": 1.0, "Ads": 1.25, "Affiliate": 1.10, "Referral": 1.05}[channel]
            reg_uplift = {"Jakarta": 1.15, "West Java": 1.05, "Central Java": 0.95, "East Java": 1.00, "Bali": 0.90, "Sumatra": 0.92}[region]

            orders  = max(1, int(round(base_orders * seasonal * weekend * ch_uplift * reg_uplift)))
            revenue = orders * price

            rows.append(
                {
                    "date"   : d.isoformat(),
                    "region" : region,
                    "channel": channel,
                    "product": product,
                    "orders" : orders,
                    "revenue": revenue,
                    "aov"    : revenue / orders,
                }
            )
    return rows

data = make_data()

# ----------------------------
# FILTERS (dynamic query filters)
# ----------------------------
with st.sidebar:
    st.header("Filters")

    all_dates = [r["date"] for r in data]
    min_d     = date.fromisoformat(min(all_dates))
    max_d     = date.fromisoformat(max(all_dates))

    d0, d1 = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    regions  = sorted({r["region"] for r in data})
    channels = sorted({r["channel"] for r in data})
    products = sorted({r["product"] for r in data})

    sel_regions  = st.multiselect("Region", regions, default=regions)
    sel_channels = st.multiselect("Channel", channels, default=channels)
    sel_products = st.multiselect("Product tier", products, default=products)

    st.divider()
    measure     = st.selectbox("Measure", ["orders", "revenue", "aov"], index=1)
    granularity = st.selectbox("Time grain", ["day", "week", "month"], index=1)

# filter rows
def in_range(iso_d: str) -> bool:
    dd = date.fromisoformat(iso_d)
    return d0 <= dd <= d1

filtered = [
    r for r in data
    if in_range(r["date"])
    and r["region"] in sel_regions
    and r["channel"] in sel_channels
    and r["product"] in sel_products
]

# ----------------------------
# AGGREGATION (no pandas required)
# ----------------------------
def bucket_date(iso_d: str, grain: str) -> str:
    dd = date.fromisoformat(iso_d)
    if grain == "day":
        return dd.isoformat()
    if grain == "week":
        # ISO week bucket: YYYY-Www
        y, w, _ = dd.isocalendar()
        return f"{y}-W{w:02d}"
    # month
    return f"{dd.year}-{dd.month:02d}"

def aggregate(rows, grain: str, by: str, measure: str):
    """
    Returns list[dict] with keys: time, group, value
    measure:
      - orders: sum
      - revenue: sum
      - aov: weighted average by orders
    """
    acc = defaultdict(lambda: {"orders": 0, "revenue": 0})
    for r in rows:
        t   = bucket_date(r["date"], grain)
        g   = r[by]
        key = (t, g)

        acc[key]["orders"]  += int(r["orders"])
        acc[key]["revenue"] += int(r["revenue"])

    out = []
    for (t, g), v in acc.items():
        if measure == "orders":
            val = v["orders"]
        elif measure == "revenue":
            val = v["revenue"]
        else:  # aov
            val = (v["revenue"] / v["orders"]) if v["orders"] else 0
        out.append({"time": t, "group": g, "value": float(val), "orders": v["orders"], "revenue": v["revenue"]})

    # sort time (best-effort)
    def time_key(x):
        s = x["time"]
        if "W" in s:
            y, w = s.split("-W")
            return (int(y), int(w), 0)
        if len(s) == 10:  # YYYY-MM-DD
            y, m, d = s.split("-")
            return (int(y), int(m), int(d))
        y, m = s.split("-")
        return (int(y), int(m), 0)

    out.sort(key=lambda x: (time_key(x), x["group"]))
    return out

# choose grouping dimension for the legend
group_dim = st.radio("Group by", ["region", "channel", "product"], horizontal=True)

series = aggregate(filtered, granularity, by=group_dim, measure=measure)

# ----------------------------
# KPI CARDS (infographic feel)
# ----------------------------
total_orders  = sum(r["orders"] for r in filtered)
total_revenue = sum(r["revenue"] for r in filtered)
aov           = (total_revenue / total_orders) if total_orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows (transactions)", f"{len(filtered):,}")
c2.metric("Total orders", f"{total_orders:,}")
c3.metric("Total revenue", f"Rp {total_revenue:,.0f}".replace(",", "."))
c4.metric("AOV", f"Rp {aov:,.0f}".replace(",", "."))

# ----------------------------
# NARRATIVE HIGHLIGHT
# ----------------------------
st.subheader("Context")
st.write(
    "The overview highlights temporal fluctuations in e-commerce activity throughout 2024. "
    "Distinct seasonal patterns and differences between regions, channels, and product tiers "
    "can be observed by narrowing the time window and comparing grouped trends."
)


# ----------------------------
# VEGA-LITE (Zoom/Pan + Brushing + Tooltips + Linked Views)
# ----------------------------
y_title = {
    "orders": "Orders (sum)",
    "revenue": "Revenue (sum)",
    "aov": "Average Order Value (weighted)",
}[measure]

# We'll keep time as nominal because week/month buckets are strings.
# For day grain, we still treat it as nominal to keep the code dependency-free.
# Vega-Lite will still render the x-axis properly as ordered strings.
spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "vconcat": [
        {
            "title" : "Overall Trend Over Time",
            "data"  : {"values": series},
            "width" : "container",
            "height": 230,
            "mark"  : {"type": "line", "point": True},
            "params": [
                # Zoom/Pan
                {
                    "name"  : "zoom",
                    "select": {"type": "interval", "encodings": ["x"]},
                    "bind"  : "scales",
                },
                # Brushing (selection range)
                {
                    "name"  : "brush",
                    "select": {"type": "interval", "encodings": ["x"]},
                },
            ],
            "encoding": {
                "x"      : {"field": "time", "type": "ordinal", "title": "Time"},
                "y"      : {"field": "value", "type": "quantitative", "title": y_title},
                "color"  : {"field": "group", "type": "nominal", "title": group_dim},
                "tooltip": [
                    {"field": "time", "type": "nominal", "title": "Time"},
                    {"field": "group", "type": "nominal", "title": "Group"},
                    {"field": "value", "type": "quantitative", "title": y_title, "format": ",.2f"},
                    {"field": "orders", "type": "quantitative", "title": "Orders", "format": ",d"},
                    {"field": "revenue", "type": "quantitative", "title": "Revenue", "format": ",d"},
                ],
            },
        },
        {
            "title"    : "Detailed View for Selected Period",
            "data"     : {"values": series},
            "width"    : "container",
            "height"   : 230,
            "transform": [{"filter": {"param": "brush"}}],
            "mark"     : {"type": "line", "point": True},
            "encoding" : {
                "x"      : {"field": "time", "type": "ordinal", "title": "Time"},
                "y"      : {"field": "value", "type": "quantitative", "title": y_title},
                "color"  : {"field": "group", "type": "nominal", "title": group_dim},
                "tooltip": [
                    {"field": "time", "type": "nominal", "title": "Time"},
                    {"field": "group", "type": "nominal", "title": "Group"},
                    {"field": "value", "type": "quantitative", "title": y_title, "format": ",.2f"},
                    {"field": "orders", "type": "quantitative", "title": "Orders", "format": ",d"},
                    {"field": "revenue", "type": "quantitative", "title": "Revenue", "format": ",d"},
                ],
            },
        },
    ],
}

st.vega_lite_chart(spec, width="stretch")

# ----------------------------
# DETAILS TABLE (details-on-demand beyond tooltips)
# ----------------------------
st.subheader("Details table (top 200 rows after filters)")
st.dataframe(sorted(filtered, key=lambda r: r["date"], reverse=True)[:200], width="stretch")
