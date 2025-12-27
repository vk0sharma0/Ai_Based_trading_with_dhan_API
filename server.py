from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)
trading_app = None  # this will be injected from your Tkinter app


def set_data_source(app_ref):
    global trading_app
    trading_app = app_ref


from flask import render_template

@app.route("/")
def index():
    return render_template("chart.html")



@app.route("/data")
def data():
    try:
        df = trading_app.ohlc_data.copy()

        if df.empty:
            return jsonify([])

        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()

        if "datetime" not in df.columns:
            return jsonify([])

        df["time"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Fill missing columns if needed
        for col in ["ema9", "ema21", "signal", "prediction_prob"]:
            if col not in df.columns:
                df[col] = None

        return jsonify(df[["time", "open", "high", "low", "close", "ema9", "ema21", "signal", "prediction_prob"]].to_dict(orient="records"))
    except Exception as e:
        print("❌ /data error:", e)
        return jsonify({"error": str(e)}), 500
