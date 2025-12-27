import pandas as pd
from evaluateSignal import evaluate_signal
from datetime import datetime

def update_data(self, timestamp, price):
    print("update_data")
    self.root.after(0,lambda:self.price_label.config(text=f"Price: ₹{price:.2f}"))
    
    # Append live tick
    self.data.loc[len(self.data)] = [timestamp, price]

    # Retain only last 2 minutes of data
    cutoff = timestamp - pd.Timedelta(minutes=2)
    self.data = self.data[self.data['timestamp'] >= cutoff.timestamp()]

    # Convert to DataFrame for OHLC
    df = self.data.copy()
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("datetime", inplace=True)

    ohlc = df["price"].resample("1Min").ohlc()
    ohlc["volume"] = df["price"].resample("1Min").count()
    ohlc.dropna(inplace=True)

    # Keep only finalized 1-minute candles
    last_minute = datetime.now().replace(second=0, microsecond=0) - pd.Timedelta(minutes=1)
    new_candles = ohlc[ohlc.index <= last_minute]
    new_candles = new_candles[~new_candles.index.isin(self.ohlc_data.index)]

    if not new_candles.empty:
        self.ohlc_data = pd.concat([self.ohlc_data, new_candles])
        df_with_signals = evaluate_signal(self, self.ohlc_data)
        self.ohlc_data = df_with_signals  # ✅ Store enriched data
