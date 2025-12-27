import json
import struct
import time
import threading
import websocket
from datetime import datetime
from log import log
from updatedata import update_data
from config import auth
import pandas as pd
################################################working websocket real data

def start_websocket(self):
    print("start_websocket")
    CLIENT_ID = auth().CLIENT_ID
    ACCESS_TOKEN = auth().ACCESS_TOKEN
    WS_URL = f"wss://api-feed.dhan.co?version=2&token={ACCESS_TOKEN}&clientId={CLIENT_ID}&authType=2"

    def on_open(ws):
        sub_msg = {
            "RequestCode": 15,
            "InstrumentCount": 1,
            "InstrumentList": [
                {
                    "ExchangeSegment": "NSE_EQ",
                    "SecurityId": "1333"
                }
            ]
        }
        ws.send(json.dumps(sub_msg))
        log(self, "✅ WebSocket connected and subscribed.")
        print("✅ Subscribed to instruments.")

    def on_data(ws, message, data_type, continue_flag):
        try:
            if len(message) < 16:
                log(self, "⚠️ Incomplete data packet received.")
                return

            # Unpack all at once
            response_code, msg_len, exch_seg, security_id, ltp, ltt = struct.unpack(
                "<B H B I f I", message[:16])

            # Convert timestamp
            print(ltt)
            timestamp = pd.to_datetime(ltt, unit='s', utc=True).tz_convert(
                "Asia/Kolkata").tz_localize(None)

            log(self, f"📈 SecID: {security_id}, ₹{ltp:.2f} @ {timestamp}")
            print(f"📈 SecID: {security_id}, ₹{ltp:.2f} @ {timestamp}")
            update_data(self, timestamp, ltp)

        except Exception as e:
            log(self, f"❌ Error in on_data: {e}")
            print(f"❌ Error in on_data: {e}")

    def on_error(ws, error):
        log(self, f"⚠️ WebSocket error: {error}")
        print(f"⚠️ WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        log(self, "❌ WebSocket closed. Reconnecting in 5s...")
        print("❌ WebSocket closed. Reconnecting in 5s...")
        time.sleep(5)
        threading.Thread(target=lambda: start_websocket(
            self), daemon=True).start()

    websocket.enableTrace(False)  # Enable for debug logging
    self.ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_data=on_data,
        on_error=on_error,
        on_close=on_close
    )
    self.ws.run_forever()
