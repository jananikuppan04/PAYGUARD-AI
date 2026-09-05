import json
import os
import joblib
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from train import config

def verify_model(model_name):
    print(f"Verifying {model_name}...")
    saved_models_dir = config.SAVED_MODELS_DIR
    reports_dir = config.REPORTS_DIR
    
    def get_id(name): return name.lower().replace(" ", "")
    mid = get_id(model_name)
    
    # Files to check
    model_files = [
        saved_models_dir / f"{mid}_model.pkl",
        saved_models_dir / f"{mid}.pkl",
        saved_models_dir / f"{mid}.pt",
        saved_models_dir / "xgboost_model.pkl" if model_name == "XGBoost" else None
    ]
    
    metrics_files = [
        saved_models_dir / f"{model_name}_metrics.json",
        saved_models_dir / f"{mid}_metrics.json",
        saved_models_dir / "metrics.json" if model_name == "XGBoost" else None,
        saved_models_dir / f"{mid.replace('forest', 'forest')}_metrics.json"
    ]
    
    report_files = [
        saved_models_dir / f"{model_name}_report.txt",
        saved_models_dir / f"{mid}_report.txt",
        reports_dir / "classification_report.txt" if model_name == "XGBoost" else None
    ]
    
    model_path = next((p for p in model_files if p and p.exists()), None)
    metrics_path = next((p for p in metrics_files if p and p.exists()), None)
    report_path = next((p for p in report_files if p and p.exists()), None)
    
    # Check evaluation plots
    if model_name == "XGBoost":
        plot_dir = reports_dir
    else:
        plot_dir = reports_dir / model_name
        if not plot_dir.exists():
            plot_dir = reports_dir / model_name.replace(" ", "")
            
    plot_exists = False
    if plot_dir.exists() and plot_dir.is_dir():
        plots = list(plot_dir.glob("*.png"))
        plot_exists = len(plots) > 0
        
    load_success = False
    load_error = None
    
    if model_path:
        try:
            if str(model_path).endswith('.pt'):
                import torch
                # Just verify the file can be loaded
                model = torch.load(model_path)
                load_success = True
            else:
                model = joblib.load(model_path)
                load_success = True
        except Exception as e:
            load_error = str(e)
            
    return {
        "model_file_exists": bool(model_path),
        "metrics_file_exists": bool(metrics_path),
        "report_file_exists": bool(report_path),
        "evaluation_plots_exist": plot_exists,
        "load_successful": load_success,
        "load_error": load_error
    }

def main():
    print("=== Running Training Verification ===")
    
    model_keys = [
        "XGBoost", "LightGBM", "Random Forest", "Autoencoder", 
        "Isolation Forest", "QSVC", "VQC", "Ensemble"
    ]
    
    verification_results = {}
    all_passed = True
    
    for model in model_keys:
        result = verify_model(model)
        verification_results[model] = result
        
        passed = result["model_file_exists"] and result["metrics_file_exists"] and result["load_successful"]
        if not passed:
            all_passed = False
            
    # Save verification report
    report_path = config.REPORTS_DIR / "training_verification.json"
    with open(report_path, "w") as f:
        json.dump(verification_results, f, indent=4)
        
    print(f"Verification complete. All Passed: {all_passed}")
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
