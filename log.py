from datetime import datetime
import tkinter as tk
    
    ####completed
def log(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_box.insert(tk.END, timestamp + " " + message + "\n")
        self.log_box.see(tk.END)
        return 