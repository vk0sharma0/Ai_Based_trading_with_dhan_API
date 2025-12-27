
from log import log
import os
import joblib


def load_model(self):
    print("load model")
    if os.path.exists(self.MODEL_PATH):
        self.ml_model = joblib.load(self.MODEL_PATH)
        log(self, "✅ Loaded saved ML model.")
    else:
        log(self, "⚠️ No saved model found.")


###### completed ######
