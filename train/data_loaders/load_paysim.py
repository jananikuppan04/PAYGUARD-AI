import pandas as pd
import logging
from train import config

logger = logging.getLogger(__name__)

def load_paysim_data(sample_size: int = None) -> pd.DataFrame:
    """
    Loads PaySim dataset and formats it for unified pipeline.
    """
    logger.info("Loading PaySim dataset...")
    try:
        df = pd.read_csv(config.DATA_PATH)
        logger.info(f"Loaded PaySim dataset. Original shape: {df.shape}")
        
        df["source_dataset"] = "PaySim"
        
        if sample_size and len(df) > sample_size:
            logger.info(f"Sampling PaySim to {sample_size} records...")
            # Stratify sample if possible
            df_fraud = df[df["isFraud"] == 1]
            df_legit = df[df["isFraud"] == 0]
            
            n_fraud = len(df_fraud)
            n_legit_to_sample = max(0, sample_size - n_fraud)
            
            if len(df_legit) > n_legit_to_sample:
                 df_legit = df_legit.sample(n=n_legit_to_sample, random_state=42)
                 
            df = pd.concat([df_fraud, df_legit]).sample(frac=1, random_state=42).reset_index(drop=True)
            logger.info(f"Sampled PaySim shape: {df.shape}")
            
        return df
    except Exception as e:
        logger.error(f"Error loading PaySim data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    load_paysim_data(50000)
