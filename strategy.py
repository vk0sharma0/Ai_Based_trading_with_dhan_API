# strategy/trainer.py

import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import ADXIndicator
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

MODEL_PATH = "model.pkl"


def engineer_features(self,df):
    df = df.copy()
    df["ema5"] = EMAIndicator(df["close"], window=5).ema_indicator()
    df["ema9"] = EMAIndicator(df["close"], window=9).ema_indicator()
    df["ema21"] = EMAIndicator(df["close"], window=21).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()

    boll = BollingerBands(close=df["close"])
    df["bollinger_mavg"] = boll.bollinger_mavg()
    df["bollinger_hband"] = boll.bollinger_hband()
    df["bollinger_lband"] = boll.bollinger_lband()

    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    macd = MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["adx"] = ADXIndicator(df["high"], df["low"], df["close"]).adx()
    df["price_change"] = df["close"].pct_change()
    df["volume_change"] = df["volume"].pct_change()

    df.dropna(inplace=True)
    return df


def generate_target(self,df, lookahead=5):
    df = df.copy()
    df["target"] = (df["close"].shift(-lookahead) > df["close"]).astype(int)
    df.dropna(inplace=True)
    return df


def train_model(df, log_func=None):
    df = engineer_features(df)
    df = generate_target(df)

    feature_cols = ["ema5", "ema9", "ema21", "ema50", "bollinger_mavg",
                    "bollinger_hband", "bollinger_lband", "rsi",
                    "macd", "macd_signal", "adx", "price_change", "volume_change"]

    X = df[feature_cols]
    y = df["target"]

    # Upsample to balance target classes
    combined = pd.concat([X, y], axis=1)
    majority = combined[combined.target == 0]
    minority = combined[combined.target == 1]
    if not minority.empty:
        minority_upsampled = minority.sample(len(majority), replace=True, random_state=42)
        balanced = pd.concat([majority, minority_upsampled])
        X = balanced.drop("target", axis=1)
        y = balanced["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, 
                              use_label_encoder=False, eval_metric='logloss', random_state=42)
        model_name = "XGBoost"
    except ImportError:
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)
        model_name = "GradientBoosting"

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    joblib.dump(model, self.MODEL_PATH)
    if log_func:
        log_func(f"✅ {model_name} model trained | Accuracy: {acc*100:.2f}%")

    return model
