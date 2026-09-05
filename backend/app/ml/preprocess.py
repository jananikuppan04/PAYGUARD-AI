import pandas as pd
import numpy as np
import logging
from typing import Tuple
from sklearn.preprocessing import LabelEncoder
import joblib
from imblearn.over_sampling import SMOTE
from . import config
from .data_loaders.load_paysim import load_paysim_data
from .data_loaders.generate_amlsim import generate_amlsim_data
from .data_loaders.generate_quantum_fraud import generate_quantum_fraud_data

logger = logging.getLogger(__name__)

def load_unified_data(sample_size: int = None) -> pd.DataFrame:
    """
    Loads and merges all three datasets (PaySim, AMLSim, QuantumSynthetic)
    into a unified DataFrame.
    """
    logger.info("Starting unified dataset loading...")
    
    # Load individual datasets
    paysim_df = load_paysim_data(sample_size=sample_size)
    
    amlsim_df = generate_amlsim_data(num_transactions=sample_size if sample_size else 50000)
    quantum_df = generate_quantum_fraud_data(num_transactions=sample_size if sample_size else 50000)
    
    # Merge datasets
    dfs = []
    if not paysim_df.empty: dfs.append(paysim_df)
    if not amlsim_df.empty: dfs.append(amlsim_df)
    if not quantum_df.empty: dfs.append(quantum_df)
    
    unified_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Unified dataset created with shape: {unified_df.shape}")
    logger.info(f"Source distribution:\n{unified_df['source_dataset'].value_counts()}")
    logger.info(f"Total fraud ratio: {unified_df['isFraud'].mean():.4f}")
    
    return unified_df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handles missing values, duplicates, and drops ignored columns."""
    logger.info("Cleaning data...")
    cols_to_drop = [col for col in config.IGNORE_COLUMNS if col in df.columns]
    
    # nameOrig and nameDest are needed for graph features, we will drop them LATER 
    # in the feature_engineering step after extracting graph features.
    # Therefore, we remove them from IGNORE_COLUMNS here if they exist.
    cols_to_drop = [c for c in cols_to_drop if c not in ["nameOrig", "nameDest", "source_dataset"]]
    
    df = df.drop(columns=cols_to_drop, errors="ignore")
    
    initial_len = len(df)
    df = df.drop_duplicates()
    logger.info(f"Dropped {initial_len - len(df)} duplicate rows.")
    
    initial_len = len(df)
    df = df.dropna()
    logger.info(f"Dropped {initial_len - len(df)} rows with missing values.")
    
    return df

def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Encodes categorical features using LabelEncoder."""
    logger.info("Encoding categorical features...")
    df_encoded = df.copy()
    
    if "type" in df_encoded.columns:
        le = LabelEncoder()
        df_encoded["type"] = le.fit_transform(df_encoded["type"])
        joblib.dump(le, config.LABEL_ENCODER_PATH)
        logger.info(f"Saved LabelEncoder to {config.LABEL_ENCODER_PATH}")
        
    return df_encoded

def apply_smote(X: pd.DataFrame, y: pd.Series, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series]:
    """Applies SMOTE to balance the dataset."""
    logger.info(f"Applying SMOTE. Original class distribution:\n{y.value_counts()}")
    smote = SMOTE(random_state=random_state)
    X_res, y_res = smote.fit_resample(X, y)
    logger.info(f"After SMOTE class distribution:\n{y_res.value_counts()}")
    return X_res, y_res
