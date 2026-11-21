"""Model training, validation, and evaluation pipeline."""

import math
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from rent_agent.config import SAMPLE_DATA_PATH, MODEL_CHECKPOINT_PATH
from rent_agent.models.data_generator import generate_dataset
from rent_agent.models.ml_engine import RentPredictorModel


def evaluate_predictions(actuals: List[float], predictions: List[float]) -> Dict[str, float]:
    """Calculate regression metrics: MAE, RMSE, MAPE, R2."""
    n = len(actuals)
    if n == 0:
        return {}

    mae = sum(abs(a - p) for a, p in zip(actuals, predictions)) / n
    mse = sum((a - p) ** 2 for a, p in zip(actuals, predictions)) / n
    rmse = math.sqrt(mse)
    mape = (sum(abs((a - p) / a) for a, p in zip(actuals, predictions)) / n) * 100

    mean_actual = sum(actuals) / n
    ss_tot = sum((a - mean_actual) ** 2 for a in actuals)
    ss_res = sum((a - p) ** 2 for a, p in zip(actuals, predictions))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return {
        "MAE ($)": round(mae, 2),
        "RMSE ($)": round(rmse, 2),
        "MAPE (%)": round(mape, 2),
        "R2 Score": round(r2, 4),
        "Samples Evaluated": n,
    }


def train_and_calibrate(dataset_path: Path = SAMPLE_DATA_PATH) -> Tuple[RentPredictorModel, Dict[str, float]]:
    """Train/calibrate the rent predictor on dataset and evaluate performance."""
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}. Generating realistic listings...")
        generate_dataset(num_samples=2500, output_path=dataset_path)

    with open(dataset_path, "r", encoding="utf-8") as f:
        listings = json.load(f)

    # Split train/test (80/20)
    split_idx = int(len(listings) * 0.8)
    train_set = listings[:split_idx]
    test_set = listings[split_idx:]

    model = RentPredictorModel()

    # Evaluate on test set
    actuals = [float(item["monthly_rent"]) for item in test_set]
    predictions = [float(model.predict(item)["predicted_monthly_rent"]) for item in test_set]

    metrics = evaluate_predictions(actuals, predictions)
    model.save_weights(MODEL_CHECKPOINT_PATH)

    return model, metrics


if __name__ == "__main__":
    print("Training and evaluating Rent Prediction Model...")
    model, metrics = train_and_calibrate()
    print("\n--- Model Evaluation Results ---")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    print(f"\nModel weights saved to {MODEL_CHECKPOINT_PATH}")
