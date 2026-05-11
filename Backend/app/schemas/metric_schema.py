from pydantic import BaseModel
from datetime import datetime


class MetricInput(BaseModel):
    cpu_percent: float
    timestamp: datetime


class PredictionOutput(BaseModel):
    timestamp: datetime
    cpu_percent: float
    anomaly: bool
    message: str
