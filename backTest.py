


def run_backtest(self):
    from log import log
    from ta.momentum import RSIIndicator
    from ta.trend import EMAIndicator, MACD, ADXIndicator
    from ta.volatility import BollingerBands
    from drawPerformanceChart import draw_performance_chart
    from chart import update_chart
    from loadModel import load_model
    from log import log

    print("runbacktest.py")
    self.root.after(0,lambda:log(self, "🧪 Starting backtest..."))
    from fetchHistoricalData import fetch_historical_data
    df = self.ohlc_data
    if df.empty:
        self.root.after(0,lambda:log(self, "⚠️ No historical data available."))
        return

    self.signal_history.clear()
    self.virtual_balance = 100000.0
    self.position = None
    self.entry_price = 0

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
    df["volume_spike"] = (df["volume"] > df["volume"].rolling(20).mean() * 1.5).astype(int)
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
        self.root.after(0,lambda:log(self, "⚠️ ML model still not loaded after attempt."))
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

    print(df[["open","high","low", "close", "prediction", "actual", "prediction_prob", "signal"]].tail(5))

    # === Update chart with signals and confidence ===
    self.root.after(0,lambda:update_chart(self, df))
    
    # === Optional: Show scrollable prediction accuracy chart ===
    self.root.after(0, lambda: show_scrollable_prediction_plot(df))

    # === Optional: Backtesting (uncomment to enable) ===
    self.root.after(0,lambda:simulate_backtest(self, df))


# === Optional scrollable prediction plot ===
def show_scrollable_prediction_plot(df):
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    import tkinter as tk
    from tkinter import ttk
    from sklearn.metrics import accuracy_score

    accuracy = accuracy_score(df["actual"], df["prediction"]) * 100

    win = tk.Toplevel()
    win.title("Prediction vs Actual - Scrollable Chart")
    win.geometry("1200x600")
    frame = ttk.Frame(win)
    frame.pack(fill=tk.BOTH, expand=True)

    fig, ax = plt.subplots(figsize=(20, 4))
    ax.step(df.index, df["prediction"], where='mid', label="Prediction", color="blue", alpha=0.7)
    ax.step(df.index, df["actual"], where='mid', label="Actual", color="orange", alpha=0.7)
    wrong = df[df["prediction"] != df["actual"]]
    ax.plot(wrong.index, wrong["prediction"], "ro", markersize=4, label="Wrong Prediction")
    ax.set_title(f"Model Predictions vs Actual (1=Up) | Accuracy: {accuracy:.2f}%")
    ax.set_xlabel("Index")
    ax.set_ylabel("Direction")
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    canvas.draw()


# === Optional backtesting (commented by default) ===
def simulate_backtest(self, df):
    pnl_total = 0.0
    trades = 0
    correct_preds = 0
    total_preds = 0
    self.real_signal_history = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        pred = row["prediction"]
        actual = row["actual"]
        dt = row.name
        signal = "BUY" if pred == 1 else "SELL"
        price = row["close"]

        total_preds += 1
        if pred == actual:
            correct_preds += 1

        self.real_signal_history.append((dt, signal))

        if signal == "BUY" and self.real_position is None:
            self.real_position = "LONG"
            self.real_entry_price = price
            trades += 1
        elif signal == "SELL" and self.real_position == "LONG":
            pnl = price - self.real_entry_price
            pnl_total += pnl
            self.real_virtual_balance += pnl
            self.real_entry_price = 0
            self.real_position = None

    accuracy = (correct_preds / total_preds) * 100 if total_preds else 0
    self.root.after(0,lambda:self.balance_label.config(text=f"Virtual Balance: ₹{self.real_virtual_balance:.2f}"))
    from drawPerformanceChart import draw_performance_chart
    from log import log
    self.root.after(0,lambda:log(self,
        f"✅ Backtest complete | Trades: {trades} | PnL: ₹{pnl_total:.2f} | Accuracy: {accuracy:.2f}% | Correct: {correct_preds}, Wrong: {total_preds - correct_preds}"))
    self.real_pnl_list.append(pnl_total)
    draw_performance_chart(self, self.pnl_list)

    
