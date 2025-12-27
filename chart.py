from ta.trend import EMAIndicator
import pandas as pd
from log import log
import mplfinance as mpf
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D


def update_chart(self, df):
    print("updatechart.py")
    if df.empty:
        log(self, "⚠️ Empty data passed to chart.")
        return

    df_ = df.copy()

    # === Ensure datetime index ===
    df_.index = pd.to_datetime(df_.index)
    df_.sort_index(inplace=True)
    df_.dropna(subset=["open", "high", "low", "close"], inplace=True)

    # === Indicators ===
    df_["ema9"] = EMAIndicator(df_["close"], window=9).ema_indicator()
    df_["ema21"] = EMAIndicator(df_["close"], window=21).ema_indicator()
    df_.dropna(inplace=True)

    # === Zoom-in view ===
    N = 100
    recent = df_.iloc[-N:] if len(df_) >= N else df_

    low = recent["low"].min()
    high = recent["high"].max()
    margin = (high - low) * 0.1 if high != low else 1
    ylim = (low - margin, high + margin)

    # === Overlays ===
    add_plots = [
        mpf.make_addplot(df_["ema9"], color='blue'),
        mpf.make_addplot(df_["ema21"], color='orange'),
    ]

    # === Buy Signals ===
    if "signal" in df_.columns:
        buy_mask = df_["signal"] == 1
        buy_marker = pd.Series(index=df_.index, dtype=float)
        buy_marker[buy_mask] = df_.loc[buy_mask, "low"] * 0.98

        add_plots.append(
            mpf.make_addplot(
                buy_marker,
                type='scatter',
                markersize=100,
                marker='^',
                color='lime'
            )
        )

    # === Prediction Confidence Panel ===
    use_confidence_panel = False
    if "prediction_prob" in df_.columns:
        add_plots.append(
            mpf.make_addplot(
                df_["prediction_prob"],
                panel=1,
                color='dodgerblue',
                secondary_y=False
            )
        )
        use_confidence_panel = True

    # === Custom TradingView-like Style ===
    my_style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        rc={
            "axes.grid": True,
            "grid.color": "#333",
            "axes.edgecolor": "#999",
            "axes.labelcolor": "#ccc",
            "xtick.color": "#999",
            "ytick.color": "#999",
            "figure.facecolor": "#1e1e1e",
            "axes.facecolor": "#1e1e1e",
        },
        marketcolors=mpf.make_marketcolors(
            up='lime',
            down='red',
            edge='inherit',
            wick='white',
            volume='inherit'
        )
    )

    # === Plot ===
    if use_confidence_panel:
        fig, axlist = mpf.plot(
            df_,
            type='candle',
            style=my_style,
            volume=False,
            returnfig=True,
            addplot=add_plots,
            panel_ratios=(3, 1),
            show_nontrading=False,
        )
    else:
        fig, axlist = mpf.plot(
            df_,
            type='candle',
            style=my_style,
            volume=False,
            returnfig=True,
            addplot=add_plots,
            show_nontrading=False,
        )

    main_ax = axlist[0]

    # === Crosshair (lines that follow mouse) ===
    vline = Line2D([0, 0], [0, 1], color='white', linestyle='--', lw=0.8)
    hline = Line2D([0, 1], [0, 0], color='white', linestyle='--', lw=0.8)
    main_ax.add_line(vline)
    main_ax.add_line(hline)
    self.crosshair_lines = (vline, hline)

    def on_mouse_move(event):
        if event.inaxes == main_ax:
            vline.set_xdata([event.xdata, event.xdata])
            hline.set_ydata([event.ydata, event.ydata])
            self.chart_canvas.draw()

    # === Annotate signal history (BUY/SELL arrows) ===
    for dt, sig in getattr(self, 'signal_history', []):
        if dt in df_.index:
            ypos = df_.loc[dt, 'close']
            color = 'green' if sig == 'BUY' else 'red'
            main_ax.annotate(
                sig,
                xy=(mdates.date2num(dt), ypos),
                xytext=(mdates.date2num(dt), ypos + 30),
                arrowprops=dict(facecolor=color, shrink=0.05),
                color=color,
                fontsize=8
            )

    # === Clear previous chart and embed in GUI ===
    for widget in self.chart_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Hook interactive events
    canvas.mpl_connect("scroll_event", self.on_scroll)
    canvas.mpl_connect("button_press_event", self.on_press)
    canvas.mpl_connect("button_release_event", self.on_release)
    canvas.mpl_connect("motion_notify_event", self.on_drag)
    canvas.mpl_connect("motion_notify_event", on_mouse_move)

    # Store refs
    self.chart_canvas = canvas
    self.chart_fig = fig
    self.chart_ax = main_ax
