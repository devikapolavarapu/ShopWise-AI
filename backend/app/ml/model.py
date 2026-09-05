import os
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
from app.ml.train import train_and_evaluate

class InventoryPredictionModel:
    def __init__ (self):
        self.model = None
        self.load_model()

    def load_model(self):
        assets_dir = Path(__file__).resolve().parent / "assets"
        model_path = assets_dir / "stockout_model.pkl"
        if not model_path.exists():
            print("[ML Model] Model artifact not found. Training new model...")
            train_and_evaluate()

        try:
            self.model = joblib.load(model_path)
            print("[ML Model] Stockout Prediction RandomForest model loaded successfully.")
        except Exception as e:
            print(f"[ML Model] Error loading model: {e}")
            self.model = None

    def predict_availability(
        self,
        current_stock: int,
        daily_sales_average: float,
        recent_sales: float = None,
        day_of_week: int = 2,
        store_reliability: float = 0.95
    ) -> Tuple[float, float]:
        """
        Returns:
            availability_confidence: float (0.0 to 1.0) -> probability of item being available
            stockout_risk_24h: float (0.0 to 1.0) -> predicted risk of running out in next 24h
        """
        if recent_sales is None:
            recent_sales = daily_sales_average

        sales_trend = recent_sales / (daily_sales_average + 1e-5)

        if self.model is not None:
            X = pd.DataFrame([{
                "current_stock": current_stock,
                "daily_sales_average": daily_sales_average,
                "recent_sales": recent_sales,
                "day_of_week": day_of_week,
                "store_reliability": store_reliability,
                "sales_trend": sales_trend
            }])
            # Probabilities: [prob_safe, prob_stockout]
            probs = self.model.predict_proba(X)[0]
            stockout_risk = float(probs[1]) if len(probs) > 1 else float(probs[0])
            availability_confidence = round(1.0 - stockout_risk, 2)
            return availability_confidence, round(stockout_risk, 2)

        # Fallback heuristic calculation if model fails
        ratio = current_stock / (daily_sales_average + 1e-5)
        stockout_risk = float(max(0.0, min(1.0, 1.0 - ratio / 1.5)))
        availability_confidence = round(1.0 - stockout_risk, 2)
        return availability_confidence, round(stockout_risk, 2)

# Singleton instance
predictor = InventoryPredictionModel()
