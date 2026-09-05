import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def generate_synthetic_dataset(n_samples: int = 1500, random_state: int = 42):
    np.random.seed(random_state)
    
    # Feature 1: current_stock (0 to 60)
    current_stock = np.random.randint(0, 60, size=n_samples)
    
    # Feature 2: daily_sales_average (2.0 to 30.0)
    daily_sales_average = np.random.uniform(2.0, 30.0, size=n_samples)
    
    # Feature 3: recent_sales (0 to 35)
    recent_sales = np.random.normal(daily_sales_average, 3.0).clip(0, 50)
    
    # Feature 4: day_of_week (0: Mon to 6: Sun)
    day_of_week = np.random.randint(0, 7, size=n_samples)
    
    # Feature 5: store_reliability (0.7 to 1.0)
    store_reliability = np.random.uniform(0.70, 0.99, size=n_samples)
    
    # Feature 6: sales_trend (recent_sales / daily_sales_average)
    sales_trend = recent_sales / (daily_sales_average + 1e-5)

    # Target label: Will stockout happen in next 24h? (1 = Stockout Risk, 0 = Safe)
    # Stockout risk is high if current_stock < 1.2 * daily_sales_average * (sales_trend)
    expected_demand_24h = daily_sales_average * sales_trend * np.where(day_of_week >= 5, 1.2, 1.0)
    
    # Stockout probability with noise
    prob = 1.0 / (1.0 + np.exp((current_stock - expected_demand_24h) / 3.0))
    # Unreliable stores increase stockout risk due to logistically delayed restocking
    prob = np.clip(prob + (1.0 - store_reliability) * 0.3, 0.0, 1.0)
    
    y = (prob > 0.45).astype(int)

    df = pd.DataFrame({
        "current_stock": current_stock,
        "daily_sales_average": daily_sales_average,
        "recent_sales": recent_sales,
        "day_of_week": day_of_week,
        "store_reliability": store_reliability,
        "sales_trend": sales_trend,
        "stockout_24h": y
    })
    return df

def train_and_evaluate():
    df = generate_synthetic_dataset()
    X = df[["current_stock", "daily_sales_average", "recent_sales", "day_of_week", "store_reliability", "sales_trend"]]
    y = df["stockout_24h"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "test_samples": len(y_test)
    }

    assets_dir = Path(__file__).resolve().parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, assets_dir / "stockout_model.pkl")
    with open(assets_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"[ML Train] Saved model to {assets_dir / 'stockout_model.pkl'}")
    print(f"[ML Train] Metrics on held-out test set: {metrics}")
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
