import gradio as gr
import pandas as pd
import numpy as np
import requests
from io import StringIO
import matplotlib.pyplot as plt
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

# Function to fetch and resample stock data from SharePoint
def fetch_stock_data(ticker, granularity):
    # Ensure ticker is available in the dictionary
    if ticker not in url_dict:
        raise ValueError("Ticker not available. Please choose one from the list.")
        
    url = url_dict[ticker]
    
    # Append parameter to force direct download if needed
    if "download=1" not in url:
        url = url + "&download=1" if "?" in url else url + "?download=1"
    
    # Fetch the CSV data
    response = requests.get(url)
    response.raise_for_status()
    data = StringIO(response.text)
    df = pd.read_csv(data)
    
    # Ensure 'Date' column is parsed as datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Resample the 1m data to the selected granularity
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

# Function to make predictions
def predict_stock_price(ticker, granularity, days_to_predict):
    try:
        df = fetch_stock_data(ticker, granularity)
    except Exception as e:
        return f"Error fetching data: {str(e)}"
    
    if df.empty:
        return "Error: No data found for the selected ticker."
    
    # Convert dates to numerical format (days since the first date)
    df["Days"] = (df["Date"] - df["Date"].min()).dt.days
    X = df["Days"].values.reshape(-1, 1)
    y = df["Close"].values

    # Train a Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Make future predictions
    future_days = np.array(range(df["Days"].max() + 1, df["Days"].max() + 1 + days_to_predict)).reshape(-1, 1)
    future_prices = model.predict(future_days)

    # Plot actual and predicted prices
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], y, label="Actual Prices", marker="o")
    future_dates = [df["Date"].max() + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    plt.plot(future_dates, future_prices, label="Predicted Prices", linestyle="dashed", marker="x")
    
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title(f"{ticker} Stock Price Prediction")
    plt.legend()
    plt.grid()

    # Save the plot and return its path
    plt.savefig("prediction_plot.png")
    plt.close()
    return "prediction_plot.png"

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# 📈 Stock Market Prediction App")
    gr.Markdown("Select a stock ticker, time granularity, and prediction range, then click Run.")
    
    # Dropdown now only shows tickers available in the url_dict
    ticker = gr.Dropdown(choices=list(url_dict.keys()), label="Select Stock Ticker")
    granularity = gr.Radio(["Daily", "Weekly", "Monthly"], label="Select Time Granularity")
    days_to_predict = gr.Slider(1, 60, step=1, label="Select Number of Days to Predict", value=7)
    
    run_button = gr.Button("Run Prediction")
    output_plot = gr.Image(label="Stock Price Prediction")

    run_button.click(predict_stock_price, inputs=[ticker, granularity, days_to_predict], outputs=output_plot)

if __name__ == "__main__":
    demo.launch(debug=True, share=True)
