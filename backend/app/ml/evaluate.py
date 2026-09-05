import json
from pathlib import Path
from app.ml.train import train_and_evaluate

def main():
    assets_dir = Path(__file__).resolve().parent / "assets"
    metrics_path = assets_dir / "metrics.json"

    if not metrics_path.exists():
        print("[ML Evaluate] No metrics found. Running train_and_evaluate()...")
        metrics = train_and_evaluate()
    else:
        with open(metrics_path, "r") as f:
            metrics = json.load(f)

    print("==========================================")
    print("      STOCKOUT MODEL EVALUATION           ")
    print("==========================================")
    print(f"Accuracy         : {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision        : {metrics['precision'] * 100:.2f}%")
    print(f"Recall           : {metrics['recall'] * 100:.2f}%")
    print(f"F1-Score         : {metrics['f1_score'] * 100:.2f}%")
    print(f"Test Set Size    : {metrics['test_samples']} samples")
    print(f"Confusion Matrix : ")
    print(f"   [[TN: {metrics['confusion_matrix'][0][0]}, FP: {metrics['confusion_matrix'][0][1]}],")
    print(f"    [FN: {metrics['confusion_matrix'][1][0]}, TP: {metrics['confusion_matrix'][1][1]}]]")
    print("==========================================")

if __name__ == "__main__":
    main()
