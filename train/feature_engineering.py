import pandas as pd
import numpy as np
import logging
import networkx as nx
from . import config

logger = logging.getLogger(__name__)

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Creates new engineered features for fraud detection."""
    logger.info("Starting comprehensive feature engineering...")
    df_fe = df.copy()
    
    # 1. Financial Features
    if all(col in df_fe.columns for col in ["oldbalanceOrg", "newbalanceOrig"]):
        df_fe["balanceDiffOrig"] = df_fe["oldbalanceOrg"] - df_fe["newbalanceOrig"]
        df_fe["origBalanceChange"] = np.where(df_fe["balanceDiffOrig"] != 0, 1, 0)
        
    if all(col in df_fe.columns for col in ["oldbalanceDest", "newbalanceDest"]):
        df_fe["balanceDiffDest"] = df_fe["oldbalanceDest"] - df_fe["newbalanceDest"]
        df_fe["destBalanceChange"] = np.where(df_fe["balanceDiffDest"] != 0, 1, 0)
        
    if all(col in df_fe.columns for col in ["amount", "oldbalanceOrg"]):
        df_fe["amountToOrigBalance"] = df_fe["amount"] / (df_fe["oldbalanceOrg"] + 1e-6)
        
    if all(col in df_fe.columns for col in ["amount", "oldbalanceDest"]):
        df_fe["amountToDestBalance"] = df_fe["amount"] / (df_fe["oldbalanceDest"] + 1e-6)
        
    if "oldbalanceOrg" in df_fe.columns:
        df_fe["isOrigBalanceZero"] = np.where(df_fe["oldbalanceOrg"] == 0, 1, 0)
        
    if "oldbalanceDest" in df_fe.columns:
        df_fe["isDestBalanceZero"] = np.where(df_fe["oldbalanceDest"] == 0, 1, 0)
        
    # 2. Behavioral Features
    if "step" in df_fe.columns:
        # Assuming step maps to 1 hour of time
        df_fe["transactionHour"] = df_fe["step"] % 24
        df_fe["transactionDay"] = (df_fe["step"] // 24) % 7
        
        # High risk time: 1 AM to 5 AM
        df_fe["isHighRiskTime"] = np.where((df_fe["transactionHour"] >= 1) & (df_fe["transactionHour"] <= 5), 1, 0)
        
    # 3. Graph Features (NetworkX)
    if all(col in df_fe.columns for col in ["nameOrig", "nameDest"]):
        logger.info("Building transaction graph for network features...")
        G = nx.from_pandas_edgelist(df_fe, source='nameOrig', target='nameDest', edge_attr='amount', create_using=nx.DiGraph())
        
        logger.info("Calculating Degree Centrality...")
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())
        
        df_fe["origOutDegree"] = df_fe["nameOrig"].map(out_degree).fillna(0)
        df_fe["destInDegree"] = df_fe["nameDest"].map(in_degree).fillna(0)
        
        # Calculate PageRank on a sample if graph is too large, or on full if small enough
        # PageRank is expensive, we'll cap iterations
        logger.info("Calculating PageRank...")
        try:
            pr = nx.pagerank(G, alpha=0.85, max_iter=20, tol=1e-3)
            df_fe["origPageRank"] = df_fe["nameOrig"].map(pr).fillna(0)
            df_fe["destPageRank"] = df_fe["nameDest"].map(pr).fillna(0)
        except nx.PowerIterationFailedConvergence:
            logger.warning("PageRank failed to converge. Filling with 0.")
            df_fe["origPageRank"] = 0.0
            df_fe["destPageRank"] = 0.0

    # 4. Risk & Quantum Features (Placeholders derived from existing stats)
    # Mocking a "historical fraud score" by averaging past fraud flags if available, 
    # but since this is stateless, we use an engineered proxy
    df_fe["historicalRiskScore"] = df_fe["amountToOrigBalance"] * df_fe["isHighRiskTime"]
    
    # Drop columns that shouldn't be used by ML models
    cols_to_drop = ["nameOrig", "nameDest", "source_dataset"]
    cols_to_drop = [c for c in cols_to_drop if c in df_fe.columns]
    if cols_to_drop:
        df_fe = df_fe.drop(columns=cols_to_drop)

    logger.info(f"Feature engineering completed. New shape: {df_fe.shape}")
    return df_fe

def normalize_features(df: pd.DataFrame, columns_to_normalize: list = None) -> pd.DataFrame:
    """Normalizes numerical columns using Min-Max scaling."""
    logger.info("Normalizing numerical features...")
    df_norm = df.copy()
    
    if columns_to_normalize is None:
        columns_to_normalize = df_norm.select_dtypes(include=[np.number]).columns.tolist()
        if config.TARGET_COLUMN in columns_to_normalize:
            columns_to_normalize.remove(config.TARGET_COLUMN)
            
    for col in columns_to_normalize:
        if col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            if max_val > min_val:
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 0.0
                
    return df_norm
