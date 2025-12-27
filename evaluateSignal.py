from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.volatility import BollingerBands
from log import log
from loadModel import load_model
from saveState import save_state
from chart import update_chart
from drawPerformanceChart import draw_performance_chart


def evaluate_signal(self, df):
    print("evaluate_signal")
    df = df.copy()

    # === Feature Engineering ===
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

    # === Additional Features ===
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["volume_spike"] = (df["volume"] > df["volume"].rolling(
        20).mean() * 1.5).astype(int)
    df["body"] = abs(df["close"] - df["open"])
    df["upper_shadow"] = df["high"] - df[["close", "open"]].max(axis=1)
    df["lower_shadow"] = df[["close", "open"]].min(axis=1) - df["low"]
    df["bullish_engulfing"] = (
        (df["close"] > df["open"]) &
        (df["close"].shift(1) < df["open"].shift(1))
    ).astype(int)

    df.dropna(inplace=True)

    # === Load ML Model ===
    if self.ml_model is None:
        self.ml_model = load_model(self)
    if self.ml_model is None:
        self.root.after(0, lambda: log(
            self, "⚠️ ML model still not loaded after attempt."))
        return

    # === Define Features ===
    feature_cols = [
        "ema5", "ema9", "ema21", "ema50",
        "bollinger_mavg", "bollinger_hband", "bollinger_lband",
        "rsi", "macd", "macd_signal", "adx",
        "price_change", "volume_change",
        "vwap", "volume_spike",
        "body", "upper_shadow", "lower_shadow",
        "bullish_engulfing"
    ]

    # === Make Predictions ===
    df["prediction_prob"] = self.ml_model.predict_proba(df[feature_cols])[:, 1]
    df["prediction"] = (df["prediction_prob"] > 0.5).astype(int)
    df["signal"] = (df["prediction_prob"] > 0.6).astype(int)
    df["actual"] = (df["close"].shift(-5) > df["close"]).astype(int)
    df.dropna(inplace=True)

    print(df[["open", "high", "low", "close", "prediction",
          "actual", "prediction_prob", "signal"]].tail(5))

    
    save_state(self)
    

    return df
