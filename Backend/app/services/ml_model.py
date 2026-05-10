import pickle
import numpy as np
from datetime import datetime
from collections import deque
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "..", "ml", "model.pkl")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Rolling window of recent CPU readings (last 12 = ~1 hour at 5min intervals)
recent_readings = deque(maxlen=12)

def predict_anomaly(cpu_percent: float, timestamp: datetime) -> bool:
    recent_readings.append(cpu_percent)

    values = list(recent_readings)
    rolling_mean = float(np.mean(values))
    rolling_std = float(np.std(values)) if len(values) > 1 else 0.0
    rolling_max = float(np.max(values))
    diff = float(cpu_percent - values[-2]) if len(values) > 1 else 0.0

    hour = timestamp.hour
    day_of_week = timestamp.weekday()

    features = np.array([[
        cpu_percent,
        rolling_mean,
        rolling_std,
        diff,
        rolling_max,
        hour,
        day_of_week
    ]])

    prediction = model.predict(features)
    return prediction[0] == -1