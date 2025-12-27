import joblib


def save_state(self):
    print("save_state")
    # global data, ohlc_data, signal_history
    joblib.dump({
        "data": self.data,
        "ohlc_data": self.ohlc_data,
        "signal_history": self.signal_history
    }, self.STATE_PATH)
