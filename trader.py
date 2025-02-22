import gradio as gr
import pandas as pd
import numpy as np
import requests
from io import StringIO
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# Dictionary with SharePoint URLs (data is 1m granularity)
url_dict = {
    "APPL": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EUjD8nLdpt1FmcNq1kQckBAB9gfHTn2Y_hl1zGOo5ecrYQ?e=AEmTL8",
    "AMZN": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ERqUB631cFlEilFPtvFw5MkBlq_bVvc4xa27svDLWGlU3A?e=nHbTKw",
    "FANG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EejmVAFQLv5PqJGuFXcvgVYBGswiq_oQJ4LhzslJbLAoAA?e=SN9BLa",
    "GOOG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ET6y-MR3SidHjGGmm8DQMn4BtpSO-GnAokJ8GI4LsghZDw?e=st6IyB",
    "TSLA": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/Ecv4R01Cn75Koj7y8UFjxHMBazIVliolR9rioUwyT03vcw?e=uq2TSF"
}

def fetch_stock_data(ticker, granularity):
    if ticker not in url_dict:
        raise ValueError("Ticker not available. Please choose one from the list.")
        
    url = url_dict[ticker]
    
    if "download=1" not in url:
        url = url + "&download=1" if "?" in url else url + "?download=1"
    
    response = requests.get(url)
    response.raise_for_status()
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df.fillna(method='ffill', inplace=True)
    
    df['Date'] = pd.to_datetime(df['Date'])
    
    if granularity in ["Daily", "Weekly", "Monthly"]:
        df.set_index('Date', inplace=True)
        if granularity == "Daily":
            df = df.resample('D').last().dropna()
        elif granularity == "Weekly":
            df = df.resample('W').last().dropna()
        elif granularity == "Monthly":
            df = df.resample('M').last().dropna()
        df.reset_index(inplace=True)
        
    return df

def predict_stock_price(ticker, granularity, days_to_predict):
    try:
        df = fetch_stock_data(ticker, granularity)
    except Exception as e:
        return f"Error fetching data: {str(e)}"
    
    if df.empty:
        return "Error: No data found for the selected ticker."
    
    # Prepare the data for the linear regression model
    df["Days"] = (df["Date"] - df["Date"].min()).dt.days
    X = df["Days"].values.reshape(-1, 1)
    y = df["Close"].values

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.array(range(df["Days"].max() + 1, df["Days"].max() + 1 + days_to_predict)).reshape(-1, 1)
    future_prices = model.predict(future_days)
    future_dates = [df["Date"].max() + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    
    # Create the interactive Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=y, mode="lines+markers", name="Actual Prices"))
    fig.add_trace(go.Scatter(x=future_dates, y=future_prices, mode="lines+markers",
                             name="Predicted Prices", line=dict(dash="dash")))
    
    fig.update_layout(
        title=f"{ticker} Stock Price Prediction",
        xaxis_title="Date",
        yaxis_title="Stock Price",
        template="plotly_white",
        legend_title="Legend"
    )
    
    return fig

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# 📈 Stock Market Prediction App")
    gr.Markdown("Select a stock ticker, time granularity, and prediction range, then click Run.")
    
    # Dropdown now only shows tickers available in the url_dict
    ticker = gr.Dropdown(choices=list(url_dict.keys()), label="Select Stock Ticker")
    granularity = gr.Radio(["Daily", "Weekly", "Monthly"], label="Select Time Granularity")
    days_to_predict = gr.Slider(1, 60, step=1, label="Select Number of Days to Predict", value=7)
    
    run_button = gr.Button("Run Prediction")
    output_plot = gr.Plot(label="Stock Price Prediction")

    run_button.click(predict_stock_price, inputs=[ticker, granularity, days_to_predict], outputs=output_plot)

if __name__ == "__main__":
    demo.launch(debug=True, share=True)
