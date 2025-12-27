import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.volatility import BollingerBands
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from fetchHistoricalData import fetch_historical_data
from log import log
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# competed
z = ""


def train_model_from_historical():
    print("train_model_from_historical")
    filepath="data/historical_OHLC.csv"
    df = pd.read_csv(filepath, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    print(f"✅ Loaded {len(df)} rows.")

    # === Feature Engineering ===
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
    macd_ind = MACD(df["close"])
    df["macd"] = macd_ind.macd()
    df["macd_signal"] = macd_ind.macd_signal()
    df["adx"] = ADXIndicator(df["high"], df["low"], df["close"]).adx()
    df["price_change"] = df["close"].pct_change()
    df["volume_change"] = df["volume"].pct_change()

    # === New Features ===
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

    # === Smarter Target: Will price be higher in 5 candles? ===
    df["target"] = (df["close"].shift(-5) > df["close"]).astype(int)
    df.dropna(inplace=True)

    # === Define Features and Labels ===
    feature_cols = [
        "ema5", "ema9", "ema21", "ema50",
        "bollinger_mavg", "bollinger_hband", "bollinger_lband",
        "rsi", "macd", "macd_signal", "adx",
        "price_change", "volume_change",
        "vwap", "volume_spike",
        "body", "upper_shadow", "lower_shadow",
        "bullish_engulfing"
    ]

    X = df[feature_cols]
    global z
    z = df.copy()
    y = df["target"]

    # === Balance Classes with Upsampling ===
    combined = pd.concat([X, y], axis=1)
    majority = combined[combined.target == 0]
    minority = combined[combined.target == 1]
    minority_upsampled = minority
    if not minority.empty:
        minority_upsampled = minority.sample(
            len(majority), replace=True, random_state=42)
    balanced = pd.concat([majority, minority_upsampled])
    X = balanced.drop("target", axis=1)
    y = balanced["target"]

    # === Train Model ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False)

    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(n_estimators=300, learning_rate=0.05,
                              max_depth=4, use_label_encoder=False, eval_metric='logloss', random_state=42)
        model_name = "XGBoost"
    except ImportError:
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(
            n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)
        model_name = "GradientBoosting"

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    # === Save Model ===
    joblib.dump(model, "ml/model.pkl")
   # global ml_model
    self.ml_model = model

    log(self, f"✅ {model_name} model trained | Accuracy: {acc*100:.2f}%")
    add_feature_tab(self)
    # Start WebSocket thread
    from startWebSocket import start_websocket
    import threading
    threading.Thread(target=lambda: start_websocket(self), daemon=True).start()


def add_feature_tab(self):
    try:
        imp = pd.Series(self.ml_model.feature_importances_, index=[
            "ema5", "ema9", "ema21", "ema50",
            "bollinger_mavg", "bollinger_hband", "bollinger_lband",
            "rsi", "macd", "macd_signal", "adx",
            "price_change", "volume_change",
            "vwap", "volume_spike",
            "body", "upper_shadow", "lower_shadow",
            "bullish_engulfing"
        ])

        fig, ax = plt.subplots(figsize=(10, 5))
        imp.sort_values().plot(kind='barh', color='skyblue', ax=ax)
        ax.set_title("📈 Importance of indicators during training of AI")
        ax.grid(True)
        fig.tight_layout()

        for widget in self.feature_imp.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.feature_imp)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        log(self, f"⚠️ Feature importance plot failed: {e}")
