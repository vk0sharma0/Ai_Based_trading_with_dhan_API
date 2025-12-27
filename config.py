

from configure_frame_gui import get_payload 
import json

# === Payload from GUI ===

# === Extracted Fields ===
CLIENT_ID = ""
ACCESS_TOKEN = ""
sec_id = ""
exchseg = ""
ins = ""
ints = ""
oid = False
fromd = ""
tod = ""


from datetime import datetime

def safe_parse_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            return None  # or raise your own custom error

def load_payload():
    payload = get_payload()
    print(payload)

    global sec_id, exchseg, ins, ints, oid, fromd, tod

    sec_id = int(payload.get("securityId"))
    exchseg = payload.get("exchangeSegment")
    ins = payload.get("instrument")
    ints = int(payload.get("interval"))
    oid = payload.get("oi") in ("True", "true", True)

    fromd = safe_parse_datetime(payload.get("fromDate"))
    tod = safe_parse_datetime(payload.get("toDate"))

    return sec_id, exchseg, ins, ints, oid, fromd, tod



class auth:
    def __init__(self):
        try:
            with open("keys.json", "r") as f:
                keys = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("❌ 'keys.json' file not found.")
        except json.JSONDecodeError:
            raise ValueError("❌ Could not parse 'keys.json'. Please check the formatting.")

        self.CLIENT_ID = keys.get("client_id", "")
        self.ACCESS_TOKEN = keys.get("access_token", "")

        if not self.CLIENT_ID or not self.ACCESS_TOKEN:
            raise ValueError("❌ Missing Client ID or Access Token in 'keys.json'")


class InstrumentType:
    def __init__(self):
        self.equity = "EQUITY"
        self.futcom = "FUTCOM"
        self.futcur = "FUTCUR"
        self.futidx = "FUTIDX"
        self.futstk = "FUTSTK"
        self.index = "INDEX"


class ExchangeSegments:
    def __init__(self):
        self.nseeq = "NSE_EQ"
        self.nsefno = "NSE_FNO"
        self.nsecur = "NSE_CURRENCY"
        self.bseeq = "BSE_EQ"
        self.mcxcom = "MCX_COMM"
        self.index = "IDX_I"


# === Example Usage ===
# auth = Auth()
# print(auth.CLIENT_ID)
# load_payload(payload)
# print(sec_id, exchseg, ins, ints, oid, fromd, tod)


# Request Headers

# HEADERS = {
#     "Accept": "application/json",
#     "Content-Type": "application/json",
#     "access-token": ACCESS_TOKEN
# }
