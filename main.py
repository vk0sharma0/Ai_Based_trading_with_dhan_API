import tkinter as tk
from tkinter import messagebox
import json
import os
import atexit
import matplotlib.pyplot as plt

# ✅ Prevent GUI crash cleanup error at exit
atexit.unregister(plt.close)
# ✅ Do NOT import your app before credentials are validated
# from app import TradingApp  ← move this AFTER validation

def prompt_for_keys():
    """Show popup to collect and save client_id and access_token"""
    if not os.path.exists("keys.json"):
        messagebox.showwarning("warning","please provide client id and access token to get started ")
    # popup = tk.Toplevel(parent)
    # popup.title("Enter Client Credentials")
    # popup.geometry("400x200")
    # popup.configure(bg="#1e1e1e")
    
   
#     popup.grab_set()  # ⛔ Prevent access to main window

#     # Fields
#     tk.Label(popup, text="Client ID", bg="#1e1e1e", fg="white").pack(pady=(20, 5))
#     client_var = tk.StringVar()
#     tk.Entry(popup, textvariable=client_var).pack()

#     tk.Label(popup, text="Access Token", bg="#1e1e1e", fg="white").pack(pady=(10, 5))
#     token_var = tk.StringVar()
#     tk.Entry(popup, textvariable=token_var, show="*").pack()

#     def save_keys():
#         cid = client_var.get().strip()
#         tok = token_var.get().strip()
#         if not cid or not tok:
#             messagebox.showerror("❌ Error", "Both fields are required.", parent=popup)
#             return
#         with open("keys.json", "w") as f:
#             json.dump({"client_id": cid, "access_token": tok}, f, indent=4)
#         popup.destroy()

#     tk.Button(popup, text="Save and Continue", command=save_keys, bg="#007acc", fg="white").pack(pady=20)
#     #popup.wait_window()  # ⏳ Wait until popup closes


# def load_keys(root):
#     """Ensure client_id and access_token are loaded from keys.json"""
#     if not os.path.exists("keys.json"):
#         prompt_for_keys(root)

#     # while True:
#     #     try:
#     #         with open("keys.json", "r") as f:
#     #             keys = json.load(f)
#     #         if not keys.get("client_id") or not keys.get("access_token"):
#     #             raise ValueError("Missing fields")
#     #         return keys
#     #     except Exception as e:
#     #         messagebox.showerror("❌ Error", f"Invalid or missing keys.json.\n\n{e}", parent=root)
#     #         prompt_for_keys(root)


# === APP ENTRY POINT ===
if __name__ == '__main__':
    print("🔑 Launching Trading App...")

    root = tk.Tk()
    #root.withdraw()  # 👈 Hide main window until keys are valid

    #root.deiconify()  # ✅ Now show main app
    from app import TradingApp  # ⏩ Import your app now

    app = TradingApp(root)
    keys = prompt_for_keys()  # ⛔ Blocks until client_id and token are correct
    root.mainloop()
