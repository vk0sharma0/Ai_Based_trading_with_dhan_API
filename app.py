import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk, scrolledtext
import threading
import pandas as pd
import webbrowser
import server  # our Flask app (server.py)
from log import log
from loadModel import load_model
from exportDataToCSV import export_data_to_csv
from refreshChart import refresh_chart
from loadState import load_state
from tkinter import messagebox
import webview
import time

class TradingApp:

    def __init__(self, root):
        print("app.py")
        self.root = root
        self.root.title("NIFTY50 AI Trader")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1e1e1e")
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.stop_threads = False
        self.ws = None
        self.chart_data_controll=False
        self.signal_history = []
        self.real_signal_history = []
        self.ml_model = None
        self.virtual_balance = 100000.0
        self.real_virtual_balance = 100000.0
        self.position = None
        self.real_position = None
        self.entry_price = 0
        self.real_entry_price = 0
        self.MODEL_PATH = "model.pkl"
        self.STATE_PATH = "saved_state.pkl"
        self.pnl_list = []
        self.real_pnl_list = []
        self.data = pd.DataFrame(columns=["timestamp", "price"])
        self.ohlc_data = pd.DataFrame(
            columns=["datetime", "open", "high", "low", "close", "volume"])

        self._drag_button = None
        self._drag_start_x = None
        self._drag_start_y = None

        self.tabs = ttk.Notebook(root)
        from configure_frame_gui import PayloadConfigTab
        self.payload_tab = PayloadConfigTab(self.tabs, self)
        self.main_tab = tk.Frame(self.tabs, bg="#1e1e1e")
        self.performance_tab = tk.Frame(self.tabs, bg="#1e1e1e")
        self.chart_tab = tk.Frame(self.tabs, bg="#1e1e1e")
        self.feature_imp = tk.Frame(self.tabs, bg="#1e1e1e")
        self.tabs.add(self.main_tab, text="📊 Live View")
        self.tabs.add(self.performance_tab, text="📈 Performance")
        self.tabs.add(self.chart_tab, text="📈 chart")
        self.tabs.add(self.feature_imp, text="🔍 Feature Importance")
        self.tabs.pack(fill="both", expand=True)

        title = tk.Label(self.main_tab, text="NIFTY50 AI Signal Generator", font=("Helvetica", 20), bg="#1e1e1e", fg="cyan")
        title.pack(pady=10)

        self.signal_label = tk.Label(self.main_tab, text="Signal: WAITING", font=("Helvetica", 16), bg="#1e1e1e", fg="white")
        self.signal_label.pack(pady=5)

        self.price_label = tk.Label(self.main_tab, text="Price: ₹--", font=("Helvetica", 14), bg="#1e1e1e", fg="lightgray")
        self.price_label.pack(pady=5)

        self.prediction_label = tk.Label(self.main_tab, text="Prediction: --", font=("Helvetica", 14), bg="#1e1e1e", fg="yellow")
        self.prediction_label.pack(pady=5)

        self.balance_label = tk.Label(self.main_tab, text=f"Virtual Balance: ₹{self.virtual_balance:.2f}", font=("Helvetica", 14), bg="#1e1e1e", fg="lime")
        self.balance_label.pack(pady=5)

        self.log_box = scrolledtext.ScrolledText(self.main_tab, width=130, height=10, bg="#121212", fg="white")
        self.log_box.pack(padx=10, pady=10)

        self.chart_mode = tk.StringVar(value="none")

        mode_frame = tk.Frame(self.chart_tab, bg="#1e1e1e")
        mode_frame.pack(pady=5)

        tk.Label(mode_frame, text="Chart Mode:", fg="white", bg="#1e1e1e").pack(side="left")
        tk.Radiobutton(mode_frame, text="Live", variable=self.chart_mode, value="live", fg="cyan", bg="#1e1e1e", selectcolor="#1e1e1e", command=lambda: refresh_chart(self)).pack(side="left")
        tk.Radiobutton(mode_frame, text="Backtest", variable=self.chart_mode, value="backtest", fg="cyan", bg="#1e1e1e", selectcolor="#1e1e1e", command=lambda: refresh_chart(self)).pack(side="left")

        self.chart_frame = tk.Frame(self.chart_tab)
        self.chart_frame.pack(fill="both", expand=True)

        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load ML Model", command=lambda: load_model(self))
        file_menu.add_command(label="Export Data to CSV", command=lambda: export_data_to_csv(self))
        menu.add_cascade(label="Model", menu=file_menu)

        backtest_menu = tk.Menu(menu, tearoff=0)
        from backTest import run_backtest
        backtest_menu.add_command(label="Run Backtest", command=lambda: run_backtest(self))
        menu.add_cascade(label="Backtest", menu=backtest_menu)
        
        self.start_flask_server()
        self.wait_for_ohlc_ready()

    def wait_for_ohlc_ready(self):
        def check():
            while self.ohlc_data.empty:
                time.sleep(1)
            server.set_data_source(self)
            webbrowser.open("http://127.0.0.1:5000")
        threading.Thread(target=check, daemon=True).start()

    def start_flask_server(self):
        threading.Thread(target=lambda: server.app.run(port=5000), daemon=True).start()

    
    def on_close(self):
        print("Closing app...")
        self.stop_threads = True
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                print(f"Error closing ws: {e}")
        self.root.destroy()

    def on_scroll(self, event):
        if event.inaxes != self.chart_ax:
            return

        xdata = event.xdata
        xmin, xmax = self.chart_ax.get_xlim()

        scale = 1.2 if event.button == 'down' else 0.8
        new_xmin = xdata - (xdata - xmin) * scale
        new_xmax = xdata + (xmax - xdata) * scale

        self.chart_ax.set_xlim(new_xmin, new_xmax)
        self.chart_canvas.draw()

    def on_press(self, event):
        if event.inaxes != self.chart_ax:
            return
        self._drag_start_x = event.xdata
        self._drag_start_y = event.ydata
        self._drag_button = event.button

        if event.button == 2:
            self.chart_ax.relim()
            self.chart_ax.autoscale_view(True, True, True)
            self.chart_canvas.draw()

    def on_release(self, event):
        if event.button == self._drag_button:
            self._drag_button = None
            self._drag_start_x = None
            self._drag_start_y = None

    def on_drag(self, event):
        if event.inaxes != self.chart_ax or self._drag_button is None:
            return

        if event.xdata is None or event.ydata is None:
            return

        if self._drag_button == 1:
            dx = self._drag_start_x - event.xdata
            dy = self._drag_start_y - event.ydata
            xmin, xmax = self.chart_ax.get_xlim()
            ymin, ymax = self.chart_ax.get_ylim()
            self.chart_ax.set_xlim(xmin + dx, xmax + dx)
            self.chart_ax.set_ylim(ymin + dy, ymax + dy)

        elif self._drag_button == 3:
            dy = self._drag_start_y - event.ydata
            zoom_scale = 1.1 ** dy
            ymin, ymax = self.chart_ax.get_ylim()
            ymid = (ymin + ymax) / 2
            new_ymin = ymid - (ymid - ymin) * zoom_scale
            new_ymax = ymid + (ymax - ymid) * zoom_scale
            self.chart_ax.set_ylim(new_ymin, new_ymax)
            self._drag_start_y = event.ydata

        self.chart_canvas.draw()
