import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#completed

def draw_performance_chart(self, pnl_list):
        print("draw_performance_chart.py")
        for widget in self.performance_tab.winfo_children():
            widget.destroy()
        fig, ax = plt.subplots(figsize=(10, 5))
        cum_pnl = np.cumsum(pnl_list)
        ax.plot(cum_pnl, label="Cumulative PnL", color="lime")
        ax.set_title("Performance Curve")
        ax.set_ylabel("₹")
        ax.set_xlabel("Trades")
        ax.grid(True)
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.performance_tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
