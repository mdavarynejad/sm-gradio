# data_handling.py

import pandas as pd
import numpy as np
import requests
from io import StringIO
from datetime import timedelta

def get_url_dict():
    """
    Dictionary containing tickers mapped to their raw data URLs.
    """
    url_dict = {
        "APPL": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EUjD8nLdpt1FmcNq1kQckBAB9gfHTn2Y_hl1zGOo5ecrYQ?e=AEmTL8",
        "AMZN": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ERqUB631cFlEilFPtvFw5MkBlq_bVvc4xa27svDLWGlU3A?e=nHbTKw",
        "FANG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/EejmVAFQLv5PqJGuFXcvgVYBGswiq_oQJ4LhzslJbLAoAA?e=SN9BLa",
        "GOOG": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/ET6y-MR3SidHjGGmm8DQMn4BtpSO-GnAokJ8GI4LsghZDw?e=st6IyB",
        "TSLA": "https://edubuas-my.sharepoint.com/:x:/g/personal/davarynejad_m_buas_nl/Ecv4R01Cn75Koj7y8UFjxHMBazIVliolR9rioUwyT03vcw?e=uq2TSF"
    }
    return url_dict

def fetch_stock_data(ticker, granularity):
    """
    Fetches stock data for the given ticker and resamples it to the specified
    granularity ('Daily', 'Weekly', 'Monthly').
    """
    url_dict = get_url_dict()
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
        freq = {
            'Daily': 'D',
            'Weekly': 'W',
            'Monthly': 'M'
        }[granularity]
        print("The set level of Granularity is: {}.".format(freq))
        df = df.resample(freq).last().dropna().reset_index()
    return df

def add_lags(df, num_lags, lag_gap):
    """
    Adds lag columns (e.g. 'Lag_1', 'Lag_2', ...) to the dataframe.
    """
    for i in range(1, num_lags + 1):
        df[f"Lag_{i}"] = df["Close"].shift(i * lag_gap)
    df.dropna(inplace=True)
    return df
