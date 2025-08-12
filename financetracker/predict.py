from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def predict_next_month_spending(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")
    monthly_spen = df.groupby("Month")["Amount"].sum().reset_index()
    monthly_spen["Month_num"] = np.arange(len(monthly_spen))  # lunile ca numere 0,1,2...

    if len(monthly_spen) < 3:
        return None  # prea puține date pentru model

    X = monthly_spen[["Luna_num"]]
    y = monthly_spen["Suma"]

    model = LinearRegression()
    model.fit(X, y)

    next_month = np.array([[monthly_spen["Luna_num"].max() + 1]])
    pred = model.predict(next_month)[0]

    return pred