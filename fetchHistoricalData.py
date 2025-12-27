from dhanhq import dhanhq
from datetime import datetime
import pandas as pd
from log import log
from config import auth, load_payload

######### completed########


client_id = auth().CLIENT_ID
access_token = auth().ACCESS_TOKEN


dhan = dhanhq(client_id, access_token)

# security_id = "1333"
# exchange_segment = "NSE_EQ"
# instrument_type = "EQUITY"
# interval = 5
# from_date = f"{(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')}"
# to_date = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def fetch_historical_data(self):
    print("fetch_historical_data")
    sec_id, exchseg, ins, ints, oid, fromd, tod = load_payload()

    try:
        # Ensure datetime format as string
        from_date_str = fromd.strftime("%Y-%m-%d %H:%M:%S") if isinstance(fromd, datetime) else str(fromd)
        to_date_str = tod.strftime("%Y-%m-%d %H:%M:%S") if isinstance(tod, datetime) else str(tod)

        # Call Dhan API
        response = dhan.intraday_minute_data(
            sec_id, exchseg, ins, from_date_str, to_date_str, ints)

        block = response.get("data", None)

        if not block or "timestamp" not in block:
            raise ValueError("📭 No historical data returned or format incorrect.")
        dt_series = pd.to_datetime(block["timestamp"], unit='s')
        dt_series = dt_series.tz_localize("UTC").tz_convert("Asia/Kolkata").tz_localize(None)
        df = pd.DataFrame({
            "datetime": dt_series,
            "open": block["open"],
            "high": block["high"],
            "low": block["low"],
            "close": block["close"],
            "volume": block.get("volume", [0]*len(block["open"]))
        })
        
        df.set_index("datetime", inplace=True)
        print(" historical data ✅ Parsed DataFrame:")
        print(df)
        print(from_date_str)
        print(to_date_str)

        log(self, "✅ Parsed DataFrame:")
        self.ohlc_data = df.copy()

        from trainModelFromHistory import train_model_from_historical
        train_model_from_historical(self, df)

        return df

    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        log(self, f"❌ Error fetching historical data: {e}")
        return pd.DataFrame()
