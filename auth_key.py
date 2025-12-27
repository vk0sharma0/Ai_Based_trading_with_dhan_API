import struct
import time
import random
from datetime import datetime
from log import log
import pandas as pd
from updatedata import update_data

def start_websocket(self):
    # === Generate a fake binary ticker packet using little-endian ===

    def generate_binary_tick(security_id=12345, exchange_segment=1):
        tick_type = 1        # Response code (1 byte)
        msg_len = 8          # Message length (2 bytes)
        exch_seg = exchange_segment  # (1 byte)
        ltp = round(random.uniform(23900, 24100), 2)
        ltt = int(time.time())  # 4-byte timestamp

        # Pack using little-endian: <B H B I f I
        packed = struct.pack("<BHBIfI", tick_type, msg_len,
                             exch_seg, security_id, ltp, ltt)

        return packed


# === Simulate binary ticks continuously ===

    def simulate_binary_ticks(callback, interval=1.0):
        print("📡 Binary tick simulation started. Press Ctrl+C to stop.")
        try:
            while True:
                raw = generate_binary_tick()
                callback(raw)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("🛑 Binary simulation stopped.")


# === Parser for the little-endian binary packet ===

    def on_data(message):
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
            
    simulate_binary_ticks(on_data, interval=1.0)
    




