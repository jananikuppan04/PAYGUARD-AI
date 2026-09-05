import json
import logging
import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
    balanced_accuracy_score,
    matthews_corrcoef
)
import numpy as np
from pathlib import Path
from . import config

logger = logging.getLogger(__name__)

def evaluate_model(model, X_test, y_test, model_name: str = None, training_time: float = None) -> dict:
    """Evaluates the model and computes all required metrics."""
    logger.info("Evaluating model...")
    
    start_pred = time.time()
    y_pred = model.predict(X_test)
    pred_time = time.time() - start_pred
    
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test)
        y_prob = probs[:, 1] if len(probs.shape) > 1 and probs.shape[1] > 1 else probs
    elif hasattr(model, "decision_function"):
        y_prob = model.decision_function(X_test)
        # Scale to 0-1 if necessary (e.g., for Isolation Forest)
        y_prob = (y_prob - y_prob.min()) / (y_prob.max() - y_prob.min() + 1e-10)
    else:
        y_prob = y_pred
    
    metrics = {
        "Accuracy": float(accuracy_score(y_test, y_pred)),
        "Precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "Recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "F1_Score": float(f1_score(y_test, y_pred, zero_division=0)),
        "ROC_AUC": float(roc_auc_score(y_test, y_prob)),
        "PR_AUC": float(average_precision_score(y_test, y_prob)),
        "Balanced_Accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "MCC": float(matthews_corrcoef(y_test, y_pred)),
        "Prediction_Time": float(pred_time)
    }
    
    if training_time is not None:
        metrics["Training_Time"] = float(training_time)
        
    # Setup paths
    metrics_path = config.METRICS_PATH
    report_path = config.CLASSIFICATION_REPORT_PATH
    cm_path = config.CONFUSION_MATRIX_PATH
    roc_path = config.ROC_CURVE_PATH
    pr_path = config.PR_CURVE_PATH
    feat_path = config.FEATURE_IMPORTANCE_PATH

    if model_name:
        # Update metrics and report paths
        metrics_path = config.SAVED_MODELS_DIR / f"{model_name}_metrics.json"
        report_path = config.SAVED_MODELS_DIR / f"{model_name}_report.txt"
        
        # Setup specific report directory
        if model_name.lower() == "xgboost":
            report_dir = config.REPORTS_DIR
        else:
            report_dir = config.REPORTS_DIR / model_name.lower()
            os.makedirs(report_dir, exist_ok=True)
            
        cm_path = report_dir / "confusion_matrix.png"
        roc_path = report_dir / "roc_curve.png"
        pr_path = report_dir / "precision_recall_curve.png"
        feat_path = report_dir / "feature_importance.png"
        
        # Estimate memory usage if model is already saved
        model_files = [
            config.SAVED_MODELS_DIR / f"{model_name}_model.pkl",
            config.SAVED_MODELS_DIR / f"{model_name}.pkl",
            config.SAVED_MODELS_DIR / f"{model_name}.pt"
        ]
        for mf in model_files:
            if mf.exists():
                metrics["Memory_Usage_MB"] = round(os.path.getsize(mf) / (1024 * 1024), 3)
                break
    
    # Save metrics to JSON
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    logger.info(f"Saved metrics to {metrics_path}")
    
    # Classification Report
    report = classification_report(y_test, y_pred, zero_division=0)
    with open(report_path, "w") as f:
        f.write(report)
    logger.info(f"Saved classification report to {report_path}")
    
    # Plots
    plot_confusion_matrix(confusion_matrix(y_test, y_pred), cm_path)
    plot_roc_curve(y_test, y_prob, roc_path)
    plot_pr_curve(y_test, y_prob, pr_path)
    
    # Feature Importance (only if model supports it)
    if hasattr(model, "feature_importances_") and hasattr(X_test, "columns"):
        plot_feature_importance(model, X_test.columns, feat_path)
    
    return metrics

def plot_confusion_matrix(cm: np.ndarray, path: Path = config.CONFUSION_MATRIX_PATH):
    """Plots and saves the confusion matrix."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved confusion matrix to {path}")

def plot_roc_curve(y_test, y_prob, path: Path = config.ROC_CURVE_PATH):
    """Plots and saves the ROC curve."""
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved ROC curve to {path}")

def plot_pr_curve(y_test, y_prob, path: Path = config.PR_CURVE_PATH):
    """Plots and saves the Precision-Recall curve."""
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved PR curve to {path}")

def plot_feature_importance(model, feature_names, path: Path = config.FEATURE_IMPORTANCE_PATH):
    """Plots and saves the feature importance."""
    importance = model.feature_importances_
    sorted_idx = np.argsort(importance)
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(sorted_idx)), importance[sorted_idx], align='center')
    plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved feature importance to {path}")
