FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY Backend/app/ ./app/

# Copy ML model
COPY ml/model.pkl ./ml/model.pkl

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
