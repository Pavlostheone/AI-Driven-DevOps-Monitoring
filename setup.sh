#!/bin/bash

echo "=== DevOps AI Monitor — Setup ==="

# === Python dependencies ===
echo "Installing Python dependencies..."
pip install fastapi uvicorn scikit-learn pandas numpy

# === Update requirements.txt ===
echo "Saving dependencies to requirements.txt..."
pip freeze > requirements.txt

echo ""
echo "=== Setup complete ==="
echo "To train the model:    python ml/train_model.py"
echo "To evaluate the model: python ml/evaluate_model.py"
echo "To start the server:   uvicorn app.main:app --reload"