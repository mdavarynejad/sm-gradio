import gradio as gr
import pandas as pd
#import yfinance as yf
import numpy as np
#import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

from gradio_client import Client

# Function to fetch stock data
def fetch_stock_data(ticker, granularity):
    period = "2y"  # Fetch last 2 years of data
    interval_map = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
    df = yf.download(ticker, period=period, interval=interval_map[granularity])
    df.reset_index(inplace=True)
    return df

# Function to make predictions
def predict_stock_price(ticker, granularity, days_to_predict):
    df = fetch_stock_data(ticker, granularity)
    
    if df.empty:
        return "Error: No data found for the selected ticker."
    
    df["Days"] = (df["Date"] - df["Date"].min()).dt.days  # Convert dates to numerical format
    X = df["Days"].values.reshape(-1, 1)
    y = df["Close"].values

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Make future predictions
    future_days = np.array(range(df["Days"].max() + 1, df["Days"].max() + 1 + days_to_predict)).reshape(-1, 1)
    future_prices = model.predict(future_days)

    # Create a plot
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], y, label="Actual Prices", marker="o")
    future_dates = [df["Date"].max() + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    plt.plot(future_dates, future_prices, label="Predicted Prices", linestyle="dashed", marker="x")
    
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title(f"{ticker} Stock Price Prediction")
    plt.legend()
    plt.grid()

    # Save plot
    plt.savefig("prediction_plot.png")
    plt.close()

    return "prediction_plot.png"

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# 📈 Stock Market Prediction App")
    gr.Markdown("Select a stock ticker, time granularity, and prediction range, then click Run.")
    
    ticker = gr.Textbox(label="Enter Stock Ticker (e.g., AAPL, TSLA, GOOG)")
    granularity = gr.Radio(["Daily", "Weekly", "Monthly"], label="Select Time Granularity")
    days_to_predict = gr.Slider(1, 60, step=1, label="Select Number of Days to Predict", value=7)
    
    run_button = gr.Button("Run Prediction")
    output_plot = gr.Image(label="Stock Price Prediction")

    run_button.click(predict_stock_price, inputs=[ticker, granularity, days_to_predict], outputs=output_plot)

# Run the app
if __name__ == "__main__":
    demo.launch(debug=True, share = True)
