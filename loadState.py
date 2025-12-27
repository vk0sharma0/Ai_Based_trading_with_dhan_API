import joblib
import os
import panadas as pd
from log import log

# competed


def load_state(self):
    print("load state")
    # global data, ohlc_data, signal_history
    if os.path.exists(self.STATE_PATH):
        state = joblib.load(self.STATE_PATH)
        self.data = state.get("data", pd.DataFrame(
            columns=["timestamp", "price"]))
        self.ohlc_data = state.get("ohlc_data", pd.DataFrame(
            columns=["datetime", "open", "high", "low", "close", "volume"]))
        self.signal_history = state.get("signal_history", [])
        log(self, "✅ Loaded saved session state.")
