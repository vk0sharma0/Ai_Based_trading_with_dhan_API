import struct
import time
import random
import pandas as pd
from log import log
from updatedata import update_data
# this is fake web sockit connection for testing for real copy and paste util code
x = 1980
y = 1981


def start_websocket(self):

    # === Generate a fake binary ticker packet using little-endian ===
    def generate_binary_tick(security_id=1333, exchange_segment=1):
        tick_type = 1         # 1 byte
        msg_len = 8           # 2 bytes
        exch_seg = exchange_segment  # 1 byte
        global x, y
        ltp = round(random.uniform(x, y), 2)  # float32
        
        ltt = int(time.time())  # 4 bytes

        # Pack as 16 bytes total
        packed = struct.pack("<B H B I f I", tick_type,
                             msg_len, exch_seg, security_id, ltp, ltt)
        return packed

    # === Parser ===
    def on_data(message):
        try:
            if len(message) < 16:
                self.root.after(0, lambda: log(
                    self, "⚠️ Incomplete data packet received."))
                return

            # Unpack all at once
            response_code, msg_len, exch_seg, security_id, ltp, ltt = struct.unpack(
                "<B H B I f I", message[:16])

            # Debug if timestamp looks wrong
            if ltt < 1000000000:  # before year ~2001
                print("⚠️ Suspicious timestamp:",
                      ltt, "| Raw:", message[:16])

            # Convert timestamp to localized datetime
            timestamp = pd.to_datetime(ltt, unit='s', utc=True).tz_convert(
                "Asia/Kolkata").tz_localize(None)

            
            print(f"📈 SecID: {security_id}, ₹{ltp:.2f} @ {timestamp}")
            update_data(self, timestamp, ltp)

        except Exception as e:
            self.root.after(0, lambda: log(
                self, f"❌ Error in on_data: {e}"))
            print(f" web socket error ❌ Error in on_data: {e}")

    # === Binary Tick Simulator ===
    def simulate_binary_ticks(callback, interval=1.0):
        print("📡 Binary tick simulation started. Press Ctrl+C to stop.")
        try:

            while not self.stop_threads:
                raw = generate_binary_tick()
                callback(raw)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("🛑 Binary simulation stopped.")

    simulate_binary_ticks(on_data, interval=1.0)
