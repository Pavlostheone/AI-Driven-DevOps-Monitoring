from fastapi import APIRouter
from app.schemas.metric_schema import MetricInput, PredictionOutput
from app.services.ml_model import predict_anomaly

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(metric: MetricInput):
    is_anomaly = predict_anomaly(metric.cpu_percent, metric.timestamp)

    return PredictionOutput(
        timestamp=metric.timestamp,
        cpu_percent=metric.cpu_percent,
        anomaly=is_anomaly,
        message="ANOMALY DETECTED" if is_anomaly else "Normal"
    )
