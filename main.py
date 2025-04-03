from data.data_handling import fetch_stock_data, add_lags


ticker = "TSLA"
granularity = "Daily"

df = fetch_stock_data(ticker, granularity)
df.head()

