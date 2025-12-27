from log import log
import pandas as pd


def export_data_to_csv(self):
    print("export_data_to_csv")
    if not self.ohlc_data.empty:
        self.ohlc_data.to_csv("historical_data.csv")
        log(self, "✅ Exported historical data to historical_data.csv")
    if self.signal_history:
        pd.DataFrame(self.signal_history, columns=["datetime", "signal"]).to_csv(
            "signals.csv", index=False)
        log(self, "✅ Exported signal history to signals.csv")
