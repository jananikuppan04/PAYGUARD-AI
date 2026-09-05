import logging
import sys
import os
import time
import subprocess
from train import config

# Setup logging for the master pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MASTER PIPELINE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "master_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_path: str, model_name: str) -> bool:
    """Runs a training script as a subprocess and logs its execution."""
    logger.info(f"=== Starting Training for {model_name} ===")
    start_time = time.time()
    
    try:
        # We use sys.executable to ensure we run with the same Python environment
        result = subprocess.run([sys.executable, "-m", script_path], 
                                capture_output=True, text=True, check=True)
        
        duration = time.time() - start_time
        logger.info(f"=== {model_name} completed successfully in {duration:.2f}s ===")
        # Write output to a specific model log
        with open(config.LOGS_DIR / f"{model_name}_subprocess.log", "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"!!! Training FAILED for {model_name} !!!")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Error output:\n{e.stderr}")
        with open(config.LOGS_DIR / f"{model_name}_subprocess_ERROR.log", "w") as f:
            f.write(e.stdout)
            f.write("\n--- STDERR ---\n")
            f.write(e.stderr)
        return False

def main():
    logger.info("Initializing Quantum Bank AI Unified Training Pipeline...")
    
    # Ensure all required directories exist
    for d in [config.DATA_DIR, config.MODELS_DIR, config.SAVED_MODELS_DIR, config.REPORTS_DIR, config.LOGS_DIR]:
        os.makedirs(d, exist_ok=True)
        
    models_to_train = [
        ("Random Forest", "train.train_randomforest"),
        ("XGBoost", "train.train_xgboost"),
        ("LightGBM", "train.train_lightgbm"),
        ("Isolation Forest", "train.train_isolationforest"),
        ("Autoencoder", "train.train_autoencoder"),
        ("QSVC", "train.train_qsvc"),
        ("VQC", "train.train_vqc"),
        ("Stacking Ensemble", "train.train_ensemble")
    ]
    
    failed_models = []
    
    for model_name, script_module in models_to_train:
        success = False
        retries = 1
        attempt = 0
        
        while attempt <= retries and not success:
            logger.info(f"Execution attempt {attempt + 1} of {retries + 1} for {model_name}")
            success = run_script(script_module, model_name)
            
            if not success:
                logger.warning(f"Attempt {attempt + 1} failed for {model_name}.")
                attempt += 1
                if attempt <= retries:
                    logger.info("Retrying in 5 seconds...")
                    time.sleep(5)
        
        if not success:
            logger.error(f"All attempts failed for {model_name}. Skipping to next model.")
            failed_models.append(model_name)
    
    logger.info("=== Master Pipeline Execution Summary ===")
    if not failed_models:
        logger.info("All models trained successfully!")
    else:
        logger.warning(f"The following models failed to train: {', '.join(failed_models)}")
        
    # Generate final comparison (this script should already exist and work on the outputs)
    logger.info("Generating final comparison report...")
    subprocess.run([sys.executable, "-m", "train.generate_comparison"])

if __name__ == "__main__":
    main()
