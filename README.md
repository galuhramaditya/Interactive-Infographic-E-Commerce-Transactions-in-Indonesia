# Interactive Infographic: E-Commerce Transactions in Indonesia (2024)

This project presents an interactive infographic for exploring e-commerce transaction data in Indonesia during 2024. The visualization enables users to examine temporal trends, compare categories, and explore transactional behavior through interactive visual techniques.

## Dataset Description

The dataset represents e-commerce transaction records collected over a one-year period (January–December 2024). Each record corresponds to a single transaction and includes temporal, categorical, and numerical attributes commonly found in real-world transactional systems.

### Attributes

- date: transaction date
- region: customer region (Jakarta, West Java, Central Java, East Java, Bali, Sumatra)
- channel: acquisition channel (Organic, Ads, Affiliate, Referral)
- product: product tier (Basic, Standard, Premium)
- orders: number of items in the transaction
- revenue: total transaction value
- aov: average order value (revenue per order)

The dataset is structured to reflect realistic business patterns, including seasonal fluctuations, regional differences, and varying performance across sales channels and product tiers.

## Visualization Goals

The infographic is designed to support exploratory data analysis by allowing users to:

- Observe overall transaction trends over time
- Compare performance across regions, channels, and product tiers
- Identify periods of unusually high or low activity
- Switch between different quantitative measures (orders, revenue, AOV)
- Focus on specific time intervals for detailed inspection

## Interactive Features

- Dynamic filtering by date range, region, sales channel, and product tier
- Selection of quantitative measures (orders, revenue, average order value)
- Zooming and panning on time-based visualizations
- Brushing and linked views between overview and detail charts
- Details-on-demand via tooltips and a detailed data table

## Visualization Structure

- Key performance indicators (KPIs) summarizing transaction volume and value
- Overview chart showing aggregated trends over time
- Detail chart focusing on user-selected time intervals
- Data table listing transaction records matching the active filters

## Running the Application

### Local Execution

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Static HTML Execution

```bash
python -m http.server 8000
```

Open:

```
http://localhost:8000/index.html
```

## Notes

The application is delivered as a static HTML page and runs entirely in the browser without requiring a backend server. All interactions are handled client-side. The dataset and visualization are intended for analytical and educational use.
