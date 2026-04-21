# app/ml.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_next_7_days(df: pd.DataFrame) -> list:
    """
    Predicts next 7 closing prices using Linear Regression
    on the last 60 days of data.
    """
    df = df.tail(60).copy()
    df = df.dropna(subset=["Close"])

    # Feature: numerical day index
    df["day_index"] = np.arange(len(df))

    X = df[["day_index"]].values
    y = df["Close"].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 7 days
    last_index = df["day_index"].iloc[-1]
    future_indices = np.arange(last_index + 1, last_index + 8).reshape(-1, 1)
    predictions = model.predict(future_indices)

    # Generate future dates (skip weekends)
    last_date = pd.to_datetime(df["Date"].iloc[-1])
    future_dates = []
    d = last_date
    while len(future_dates) < 7:
        d += pd.Timedelta(days=1)
        if d.weekday() < 5:  # Mon–Fri only
            future_dates.append(d.strftime("%Y-%m-%d"))

    return [
        {"Date": date, "Predicted_Close": round(float(price), 2)}
        for date, price in zip(future_dates, predictions)
    ]