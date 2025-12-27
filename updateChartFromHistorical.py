import pandas as pd
from log import log
from ta.trend import EMAIndicator
import mplfinance as mpf
import matplotlib.dates as mdates

# competed


def update_chart_from_historical(self, df):
    print("update_chart_from_historical")
    if df.empty:
        log(self, "⚠️ Empty historical data.")
        return

    df_ = df.copy()
    if not isinstance(df_.index, pd.DatetimeIndex):
        df_.index = pd.to_datetime(df_.index)
    df_.index.name = 'Date'

    self.chart_ax.clear()

    df_["ema9"] = EMAIndicator(df_["close"], window=9).ema_indicator()
    df_["ema21"] = EMAIndicator(df_["close"], window=21).ema_indicator()

    mpf.plot(
        df_,
        type='candle',
        style='yahoo',
        ax=self.chart_ax,
        volume=False,
        addplot=[
            mpf.make_addplot(df_["ema9"], color='blue', ax=self.chart_ax),
            mpf.make_addplot(
                df_["ema21"], color='orange', ax=self.chart_ax)
        ],
        show_nontrading=False
    )

    for dt, sig in self.signal_history:
        if dt in df_.index:
            ypos = df_.loc[dt, 'close']
            color = 'green' if sig == 'BUY' else 'red'
            self.chart_ax.annotate(
                sig,
                xy=(mdates.date2num(dt), ypos),
                xytext=(mdates.date2num(dt), ypos + 50),
                arrowprops=dict(facecolor=color, shrink=0.05),
                color=color,
                fontsize=8
            )

    self.chart_ax.set_title("Backtest NIFTY50 Chart")
    self.chart_ax.grid(True)
    self.chart_fig.tight_layout()
    self.chart_canvas.draw()
