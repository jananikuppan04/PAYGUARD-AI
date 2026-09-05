import json
import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from train import config

def calculate_overall_score(metrics):
    """
    Calculates weighted overall score emphasizing ROC-AUC, F1, and Recall.
    Also calculates a penalty based on Prediction Time, Training Time, and Memory Usage as tie-breakers.
    """
    # Defaults
    roc_auc = metrics.get("ROC_AUC", 0.0)
    f1 = metrics.get("F1_Score", 0.0)
    recall = metrics.get("Recall", 0.0)
    pr_auc = metrics.get("PR_AUC", 0.0)
    mcc = metrics.get("MCC", 0.0)
    bal_acc = metrics.get("Balanced_Accuracy", 0.0)
    
    # Highest weights: ROC-AUC, F1, Recall
    score = (0.35 * roc_auc) + (0.25 * f1) + (0.25 * recall) + (0.05 * pr_auc) + (0.05 * mcc) + (0.05 * bal_acc)
    
    # Tie-breaker penalties (small values)
    # Time in seconds, Memory in MB
    train_time = metrics.get("Training_Time", 0.0)
    pred_time = metrics.get("Prediction_Time", 0.0)
    mem_usage = metrics.get("Memory_Usage_MB", 0.0)
    
    # Normalise roughly (just an approximation for penalty)
    # 1 hour training = 3600s, 1s prediction = 1s, 1GB memory = 1024MB
    penalty = (train_time / 3600.0 * 0.0001) + (pred_time / 10.0 * 0.0001) + (mem_usage / 1024.0 * 0.0001)
    
    return score - penalty

def main():
    print("=== Generating Model Comparison Reports ===")
    
    saved_models_dir = config.SAVED_MODELS_DIR
    reports_dir = config.REPORTS_DIR
    
    model_keys = [
        "XGBoost", "LightGBM", "Random Forest", "Autoencoder", 
        "Isolation Forest", "QSVC", "VQC", "Ensemble"
    ]
    
    # To match model_training_visualizer ID logic
    def get_id(name): return name.lower().replace(" ", "")
    
    comparison_data = []
    
    for model_name in model_keys:
        mid = get_id(model_name)
        metrics_paths = [
            saved_models_dir / f"{model_name}_metrics.json",
            saved_models_dir / f"{mid}_metrics.json",
            saved_models_dir / "metrics.json" if model_name == "XGBoost" else None,
            saved_models_dir / f"{mid.replace('forest', 'forest')}_metrics.json"
        ]
        
        metrics = {}
        found = False
        for p in metrics_paths:
            if p and p.exists():
                with open(p, 'r') as f:
                    metrics = json.load(f)
                found = True
                break
                
        if found:
            overall_score = calculate_overall_score(metrics)
            
            # Determine status and model size
            model_files = [
                saved_models_dir / f"{mid}_model.pkl",
                saved_models_dir / f"{mid}.pkl",
                saved_models_dir / f"{mid}.pt",
                saved_models_dir / "xgboost_model.pkl" if model_name == "XGBoost" else None
            ]
            
            model_size = 0.0
            status = "Completed"
            for mf in model_files:
                if mf and mf.exists():
                    model_size = round(os.path.getsize(mf) / (1024 * 1024), 3)
                    break
            
            # Extract basic metadata
            train_time = metrics.get("Training_Time", 0.0)
            pred_time = metrics.get("Prediction_Time", 0.0)
            
            row = {
                "Model": model_name,
                "Status": status,
                "Overall_Score": overall_score,
                "Accuracy": metrics.get("Accuracy"),
                "Precision": metrics.get("Precision"),
                "Recall": metrics.get("Recall"),
                "F1_Score": metrics.get("F1_Score"),
                "ROC_AUC": metrics.get("ROC_AUC"),
                "PR_AUC": metrics.get("PR_AUC"),
                "Balanced_Accuracy": metrics.get("Balanced_Accuracy"),
                "MCC": metrics.get("MCC"),
                "Prediction_Time_s": pred_time,
                "Training_Time_s": train_time,
                "Memory_Usage_MB": model_size or metrics.get("Memory_Usage_MB", 0.0),
                "Training_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Dataset_Size": 500000 if model_name not in ["QSVC", "VQC"] else config.QUANTUM_SAMPLE_SIZE
            }
            comparison_data.append(row)
        else:
            print(f"Metrics not found for {model_name}")
            row = {
                "Model": model_name,
                "Status": "Pending",
                "Overall_Score": 0.0,
                "Accuracy": None,
                "Precision": None,
                "Recall": None,
                "F1_Score": None,
                "ROC_AUC": None,
                "PR_AUC": None,
                "Balanced_Accuracy": None,
                "MCC": None,
                "Prediction_Time_s": None,
                "Training_Time_s": None,
                "Memory_Usage_MB": None,
                "Training_Date": None,
                "Dataset_Size": None
            }
            comparison_data.append(row)
            
    df = pd.DataFrame(comparison_data)
    
    # Rank models that are completed
    completed_mask = df["Status"] == "Completed"
    if completed_mask.any():
        df.loc[completed_mask, "Rank"] = df.loc[completed_mask, "Overall_Score"].rank(ascending=False, method="min").astype(int)
    else:
        df["Rank"] = None
        
    df = df.sort_values(by="Rank", ascending=True, na_position="last").reset_index(drop=True)
    
    # Export overall ranking specific formats
    ranking_df = df[["Rank", "Model", "Overall_Score", "ROC_AUC", "F1_Score", "Recall", "Status"]]
    
    # Save CSVs
    df.to_csv(reports_dir / "comparison.csv", index=False)
    ranking_df.to_csv(reports_dir / "overall_ranking.csv", index=False)
    print("Saved comparison.csv and overall_ranking.csv")
    
    # Save JSONs
    # Convert dataframe to records for JSON
    json_data = df.to_dict(orient="records")
    with open(reports_dir / "comparison.json", "w") as f:
        json.dump(json_data, f, indent=4)
        
    ranking_json = ranking_df.to_dict(orient="records")
    with open(reports_dir / "overall_ranking.json", "w") as f:
        json.dump(ranking_json, f, indent=4)
        
    print("Saved comparison.json and overall_ranking.json")
    print("=== Model Comparison Generation Complete ===")

if __name__ == "__main__":
    main()
