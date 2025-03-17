import gradio as gr
import pandas as pd
import numpy as np
import requests
from io import StringIO
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import timedelta

# URL dictionary
url_dict = {
    "APPL": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EUjD8nLdpt1FmcNq1kQckBAB9gfHTn2Y_hl1zGOo5ecrYQ?e=AEmTL8",
    "AMZN": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ERqUB631cFlEilFPtvFw5MkBlq_bVvc4xa27svDLWGlU3A?e=nHbTKw",
    "FANG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EejmVAFQLv5PqJGuFXcvgVYBGswiq_oQJ4LhzslJbLAoAA?e=SN9BLa",
    "GOOG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ET6y-MR3SidHjGGmm8DQMn4BtpSO-GnAokJ8GI4LsghZDw?e=st6IyB",
    "TSLA": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/Ecv4R01Cn75Koj7y8UFjxHMBazIVliolR9rioUwyT03vcw?e=uq2TSF"
}

def fetch_stock_data(ticker, granularity):
    url = url_dict[ticker]
    if "download=1" not in url:
        url += "&download=1" if "?" in url else "?download=1"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    df.fillna(method='ffill', inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

    if granularity != "Minute":
        df.set_index('Date', inplace=True)
        freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}[granularity]
        df = df.resample(freq).last().dropna().reset_index()
    return df

def add_lags(df, num_lags, lag_gap):
    for i in range(1, num_lags + 1):
        df[f"Lag_{i}"] = df["Close"].shift(i * lag_gap)
    df.dropna(inplace=True)
    return df

def predict_stock_price(ticker, granularity, days, model_type, num_lags, lag_gap):
    df = fetch_stock_data(ticker, granularity)
    df = add_lags(df, num_lags, lag_gap)
    df["Days"] = (df["Date"] - df["Date"].min()).dt.days
    X = df[["Days"] + [f"Lag_{i}" for i in range(1, num_lags + 1)]].values
    y = df["Close"].values

    if model_type == "Linear Regression":
        model = LinearRegression()
        model.fit(X, y)
        equation = f"y = {model.intercept_:.2f} " + " + ".join(
        [f"{model.coef_[i]:.4f} * X{i}" for i in range(len(model.coef_))]
)


    elif model_type == "Polynomial Regression":
        degree = 3
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(X, y)
        equation = "Polynomial regression equation (complex form)"

    elif model_type == "Ridge Regression":
        model = Ridge(alpha=1.0)
        model.fit(X, y)
        equation = f"y = {model.coef_[0]:.4f}X + {model.intercept_:.2f}"

    elif model_type == "Random Forest Regression":
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)
        equation = "Random Forest: Complex model (no simple equation)"

    future_days = np.array(range(int(np.floor(df["Days"].max())) + 1, int(np.floor(df["Days"].max())) + int(days) + 1)).reshape(-1, 1)
    future_X = np.hstack([future_days] + [np.zeros((future_days.shape[0], num_lags))])
    future_prices = model.predict(future_X)
    future_dates = [df["Date"].max() + timedelta(days=int(i)) for i in range(1, int(days) + 1)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=y, name="Actual Prices"))
    fig.add_trace(go.Scatter(x=future_dates, y=future_prices, name="Predicted Prices", line=dict(dash="dot")))
    fig.update_layout(title=f"{ticker} Price Prediction ({model_type})", template="plotly_white")

    return fig, equation

with gr.Blocks() as demo:
    gr.Markdown("# 📈 Stock Market Prediction")
    ticker = gr.Dropdown(list(url_dict.keys()), label="Ticker")
    granularity = gr.Radio(["Daily", "Weekly", "Monthly"], label="Granularity", value="Daily")
    days = gr.Slider(1, 60, value=7, label="Days to Predict")
    model_type = gr.Dropdown(["Linear Regression", "Polynomial Regression", "Ridge Regression", "Random Forest Regression"], label="Model Type")
    num_lags = gr.Slider(0, 10, value=0, step=1, label="Number of Lags")
    lag_gap = gr.Slider(1, 30, value=1, step=1, label="Lag Gap (Days)")

    btn = gr.Button("Run Prediction")
    plot = gr.Plot()
    equation = gr.Textbox(label="Model Equation")

    btn.click(predict_stock_price, [ticker, granularity, days, model_type, num_lags, lag_gap], [plot, equation])

demo.launch(server_name="0.0.0.0", server_port=7860)