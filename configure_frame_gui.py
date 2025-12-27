from tkinter import messagebox
import json
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import os


class Payload:
    def __init__(self):
        self.securityId = ""
        self.exchangeSegment = ""
        self.instrument = ""
        self.interval = ""
        self.oi = False
        self.fromDate = None
        self.toDate = None

    def load_from_form(self, field_dict):
        self.securityId = field_dict.get("securityId", "")
        self.exchangeSegment = field_dict.get("exchangeSegment", "")
        self.instrument = field_dict.get("instruments", "")
        self.interval = field_dict.get("interval", "")
        self.oi = field_dict.get("oi", "False").lower() == "true"

        try:
            from_date = field_dict.get("fromDate")
            to_date = field_dict.get("toDate")
            if isinstance(from_date, tuple) and isinstance(to_date, tuple):
                from_str = f"{from_date[0].get()} {from_date[1].get()}:{from_date[2].get()}"
                to_str = f"{to_date[0].get()} {to_date[1].get()}:{to_date[2].get()}"
                self.fromDate = datetime.strptime(from_str, "%Y-%m-%d %H:%M")
                self.toDate = datetime.strptime(to_str, "%Y-%m-%d %H:%M")
            else:
                self.fromDate = datetime.strptime(str(from_date), "%Y-%m-%d")
                self.toDate = datetime.strptime(str(to_date), "%Y-%m-%d")
        except Exception as e:
            print("⚠️ Date parse error:", e)
            self.fromDate = None
            self.toDate = None

    def to_json(self):
        return {
            "securityId": self.securityId,
            "exchangeSegment": self.exchangeSegment,
            "instrument": self.instrument,
            "interval": self.interval.split("m")[0],
            "oi": self.oi,
            "fromDate": self.fromDate.strftime("%Y-%m-%d %H:%M") if self.fromDate else None,
            "toDate": self.toDate.strftime("%Y-%m-%d %H:%M") if self.toDate else None
        }



pyload = None


class PayloadConfigTab:
    def __init__(self, parent_notebook, app):
        self.pl = Payload()
        self.fields = {}
        self.auth_data = {}

        self.tab = tk.Frame(parent_notebook, bg="#1e1e1e")
        parent_notebook.add(self.tab, text="📦 Payload Config")

        self.auth_frame = tk.Frame(self.tab, bg="#1e1e1e", borderwidth=1)
        self.auth_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.payload_frame = tk.Frame(self.tab, bg="#1e1e1e")
        self.payload_frame.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.build_gui(app)

    def build_gui(self, app):
        tk.Label(self.auth_frame, text="CONFIGURATION", font=("Helvetica", 15),
                 fg="#ffffff", bg="#1e1e1e").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

        self.client_id = tk.Label(self.auth_frame, text="CLIENT ID", font=("Helvetica", 10),
                                  fg="#ffffff", bg="#1e1e1e").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        self.client_id_var = tk.StringVar()
        self.client_id_entry = tk.Entry(
            self.auth_frame, textvariable=self.client_id_var, bg="#414040", fg="#000000", font=("Helvetica", 10), state="readonly")
        self.client_id_entry.grid(
            row=2, column=1, pady=5, ipadx=50, ipady=5, sticky="ew")
        self.auth_data["client_id"] = self.client_id_var

        self.access_token = tk.Label(self.auth_frame, text="ACCESS TOKEN", font=("Helvetica", 10),
                                     fg="#ffffff", bg="#1e1e1e").grid(row=3, column=0, sticky="w", pady=5, padx=(0, 10))
        self.access_token_var = tk.StringVar()
        self.access_token_entry = tk.Entry(
            self.auth_frame, textvariable=self.access_token_var, bg="#414040", fg="#000000", font=("Helvetica", 10), state="readonly")
        self.access_token_entry.grid(
            row=3, column=1, pady=5, ipadx=50, ipady=5, sticky="ew")
        self.auth_data["access_token"] = self.access_token_var

        if os.path.exists("keys.json"):
            self.client_id_var.set("✅Key installed")
            self.access_token_var.set("✅Key installed")

        submit_btn_auth = tk.Button(self.auth_frame, text="📝 UPDATE", bg="#007acc", fg="white",
                                    font=("Helvetica", 10), command=lambda: self.save_auth(self, app))
        submit_btn_auth.grid(row=4, column=1, sticky="e", pady=20)
        edit_btn_auth = tk.Button(self.auth_frame, text="📝 EDIT", bg="#1e60ef", fg="white",
                                  font=("Helvetica", 10), command=lambda: self.edit_auth(app))
        edit_btn_auth.grid(row=4, column=1, sticky="w", pady=5)

        tk.Label(self.payload_frame, text="INSTRUMENT SELECTION", font=("Helvetica", 16),
                 fg="#ffffff", bg="#1e1e1e").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        self.add_entry("securityId", "Security ID:", row=1)
        self.add_dropdown("instruments", "Instrument:", row=2,
                          options=["INDEX", "FUTIDX", "OPTIDX", "EQUITY", "FUTSTK", "OPTSTK", "FUTCOM", "OPTFUT", "FUTCUR", "OPTCUR"])
        self.add_dropdown("exchangeSegment", "Exchange Segment:", row=3,
                          options=["NSE_EQ", "NSE_FNO", "BSE_EQ", "MCX_COMM", "IDX_I"])
        self.add_dropdown("interval", "Interval:", row=4,
                          options=["1minute", "5minute", "15minute", "1hour", "1day"])
        self.add_dropdown("oi", "OI:", row=5, options=["True", "False"])
        self.add_date("fromDate", "From Date:", row=6)
        self.add_date("toDate", "To Date:", row=7)

        submit_btn = tk.Button(self.payload_frame, text="📝 Submit", bg="#007acc", fg="white",
                               font=("Helvetica", 10), command=lambda: self.submit_payload(app))
        submit_btn.grid(row=10, column=1, sticky="e", pady=20)

    def edit_auth(self, app):

        self.client_id_entry.config(state="normal")
        self.access_token_entry.config(state="normal")
        self.client_id_var.set("")
        self.access_token_var.set("")
        return

    def save_auth(self, parent, app):
        auth_data = {attr: var.get() for attr, var in parent.auth_data.items()}

        if not auth_data.get("client_id") or not auth_data.get("access_token"):
            messagebox.showerror(
                "❌ Error", "Client ID and Access Token are required.")
            return

        def save_keys():

            keys = {
                "client_id": auth_data["client_id"],
                "access_token": auth_data["access_token"]
            }
            try:
                with open("keys.json", "w") as f:
                    json.dump(keys, f, indent=4)
                messagebox.showinfo("✅ Submitted", "Keys installed ✔️")
                self.client_id_var.set("✅ Key installed")
                self.access_token_var.set("✅ Key installed")
                self.client_id_entry.config(state="readonly")
                self.access_token_entry.config(state="readonly")
                self.popup.destroy()
            except Exception as e:
                messagebox.showerror(
                    "❌ Error", f"Failed to save keys.json: {e}")

        def on_cancel_btn():
            self.popup.destroy()
            self.client_id_var.set("✅Key installed")
            self.access_token_var.set("✅Key installed")

        self.popup = tk.Toplevel()
        self.popup.title("Update Keys?")
        self.popup.geometry("400x150")
        self.popup.configure(bg="#1e1e1e")
        self.popup.grab_set()

        tk.Label(self.popup, text="Are you sure you want to update keys?",
                 bg="#1e1e1e", fg="white", font=("Helvetica", 12)).pack(pady=10)

        tk.Button(self.popup, text="✅ Save and Continue", command=save_keys,
                  bg="#007acc", fg="white", font=("Helvetica", 10)).pack(pady=10)

        tk.Button(self.popup, text="❌ Cancel", command=on_cancel_btn,
                  bg="#444", fg="white", font=("Helvetica", 10)).pack()

    def add_entry(self, field, label, row):

        tk.Label(self.payload_frame, text=label, font=("Helvetica", 10),
                 fg="#ffffff", bg="#1e1e1e").grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        var = tk.StringVar()
        entry = tk.Entry(self.payload_frame, textvariable=var,
                         bg="#414040", fg="#ffffff", font=("Helvetica", 10))
        entry.grid(row=row, column=1, pady=5, ipadx=50, ipady=5, sticky="ew")
        self.fields[field] = var

    def add_dropdown(self, field, label, row, options):
        tk.Label(self.payload_frame, text=label, font=("Helvetica", 10),
                 fg="#ffffff", bg="#1e1e1e").grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        var = tk.StringVar()
        dropdown = ttk.Combobox(self.payload_frame, textvariable=var, values=options,
                                font=("Helvetica", 10))
        dropdown.grid(row=row, column=1, pady=5, ipady=3, sticky="ew")
        dropdown.current(0)
        self.fields[field] = var

    def add_date(self, field, label, row):
        tk.Label(self.payload_frame, text=label, font=("Helvetica", 10),
                 fg="#ffffff", bg="#1e1e1e").grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))

        # === Date Picker ===
        date_var = tk.StringVar()
        date_picker = DateEntry(self.payload_frame, textvariable=date_var, background='darkblue',
                                foreground='white', borderwidth=2, font=("Helvetica", 10), date_pattern='yyyy-mm-dd')
        date_picker.grid(row=row, column=1, pady=5, ipady=3, sticky="ew")

        # === Hour Picker ===
        hour_var = tk.StringVar(value="09")
        hour_picker = ttk.Combobox(self.payload_frame, textvariable=hour_var, width=3,
                                   values=[f"{i:02d}" for i in range(24)], font=("Helvetica", 10))
        hour_picker.grid(row=row, column=2, padx=(5, 0), pady=5)
        hour_picker.state(["readonly"])

        # === Minute Picker ===
        minute_var = tk.StringVar(value="15")
        minute_picker = ttk.Combobox(self.payload_frame, textvariable=minute_var, width=3,
                                     values=[f"{i:02d}" for i in range(60)], font=("Helvetica", 10))
        minute_picker.grid(row=row, column=3, padx=(2, 0), pady=5)
        minute_picker.state(["readonly"])

        # Store as a tuple
        self.fields[field] = (date_var, hour_var, minute_var)

    def submit_payload(self, app):
        field_data = {
            attr: (var[0], var[1], var[2]) if isinstance(
                var, tuple) else var.get()
            for attr, var in self.fields.items()

        }
        
        self.pl.load_from_form(field_data)  # Use your Payload class

        global pyload
        pyload = self.pl.to_json()  # Now correctly formatted

        print("📦 Payload Submitted:")
        print(pyload)
        from fetchHistoricalData import fetch_historical_data
        fetch_historical_data(app)
        


def get_payload():
    global pyload
    return pyload
