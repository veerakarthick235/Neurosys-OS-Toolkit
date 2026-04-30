"""
NeuroSys OS Toolkit - Resource Predictor
Predicts future CPU and memory usage using simple linear regression.
"""

import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.models.schemas import ResourcePrediction
from app.services.system_monitor import system_monitor


class ResourcePredictor:
    def __init__(self):
        self.prediction_window = 10

    def _linear_regression(self, values: List[float]) -> tuple:
        n = len(values)
        if n < 2:
            return 0.0, values[0] if values else 0.0
        x = np.arange(n, dtype=float)
        y = np.array(values, dtype=float)
        x_mean, y_mean = np.mean(x), np.mean(y)
        num = np.sum((x - x_mean) * (y - y_mean))
        den = np.sum((x - x_mean) ** 2)
        if den == 0:
            return 0.0, y_mean
        slope = num / den
        return float(slope), float(y_mean - slope * x_mean)

    def _confidence(self, values, slope, intercept):
        if len(values) < 3:
            return 0.5
        x = np.arange(len(values), dtype=float)
        y = np.array(values, dtype=float)
        ss_res = np.sum((y - (slope * x + intercept)) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return round(max(0.0, 1.0 - ss_res / ss_tot), 2) if ss_tot else 1.0

    def predict(self, metric: str = "cpu") -> ResourcePrediction:
        history = system_monitor.get_history()
        values = history.cpu_values if metric == "cpu" else history.memory_values
        label = "CPU Usage %" if metric == "cpu" else "Memory Usage %"

        if len(values) < 3:
            return ResourcePrediction(metric=label, current_value=values[-1] if values else 0.0,
                predicted_values=[], prediction_timestamps=[], trend="stable", confidence=0.0)

        slope, intercept = self._linear_regression(values)
        conf = self._confidence(values, slope, intercept)
        trend = "stable" if abs(slope) < 0.1 else ("increasing" if slope > 0 else "decreasing")
        now = datetime.now(timezone.utc)
        n = len(values)
        preds, times = [], []
        for i in range(1, self.prediction_window + 1):
            p = max(0.0, min(100.0, slope * (n + i) + intercept))
            preds.append(round(p, 2))
            times.append((now + timedelta(seconds=i)).isoformat())

        pred_max = max(preds)
        alert = None
        if metric == "cpu" and pred_max > 90:
            alert = f"CPU predicted to reach {pred_max:.1f}%"
        elif metric == "memory" and pred_max > 85:
            alert = f"Memory predicted to reach {pred_max:.1f}%"

        return ResourcePrediction(metric=label, current_value=round(values[-1], 2),
            predicted_values=preds, prediction_timestamps=times, trend=trend, alert=alert, confidence=conf)

    def predict_all(self) -> List[ResourcePrediction]:
        return [self.predict("cpu"), self.predict("memory")]

resource_predictor = ResourcePredictor()
