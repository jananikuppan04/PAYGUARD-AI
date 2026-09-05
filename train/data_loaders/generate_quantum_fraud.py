import pandas as pd
import numpy as np
import logging
import os
from train import config

logger = logging.getLogger(__name__)

def generate_quantum_fraud_data(num_transactions: int = 50000) -> pd.DataFrame:
    """
    Generates a synthetic dataset mimicking zero-day fraud scenarios 
    (quantum-resistant attack simulations, AI-generated fraud).
    """
    logger.info(f"Generating synthetic Quantum Fraud data ({num_transactions} transactions)...")
    np.random.seed(4242)
    
    # Generate Account IDs
    num_accounts = num_transactions // 10
    accounts = [f"Q{i:06d}" for i in range(num_accounts)]
    
    step = np.random.randint(1, 744, size=num_transactions)
    # Quantum fraud tends to involve rapid transfers or cash outs
    types = np.random.choice(["TRANSFER", "CASH_OUT", "PAYMENT"], size=num_transactions, p=[0.6, 0.3, 0.1])
    
    # Bimodal amount distribution
    amount = np.where(np.random.rand(num_transactions) > 0.8, 
                      np.random.normal(200000, 10000), 
                      np.random.exponential(1000, size=num_transactions))
    amount = np.maximum(amount, 10)
    
    nameOrig = np.random.choice(accounts, size=num_transactions)
    nameDest = np.random.choice(accounts, size=num_transactions)
    
    oldbalanceOrg = np.random.uniform(0, 500000, size=num_transactions)
    newbalanceOrig = np.maximum(0, oldbalanceOrg - amount)
    
    oldbalanceDest = np.random.uniform(0, 500000, size=num_transactions)
    newbalanceDest = oldbalanceDest + amount
    
    isFraud = np.zeros(num_transactions, dtype=int)
    
    # Pattern 1: Quantum AI behavior anomaly - rapid exact depletion
    fraud_idx1 = np.where((types == "TRANSFER") & (np.abs(oldbalanceOrg - amount) < 1.0))[0]
    if len(fraud_idx1) > 0:
        fraud_sampled = np.random.choice(fraud_idx1, size=int(len(fraud_idx1) * 0.8), replace=False)
        isFraud[fraud_sampled] = 1
        
    # Pattern 2: Multi-device login / impossible travel mock
    # Represented by sudden spike in transaction amount from historically low balance
    fraud_idx2 = np.where((oldbalanceOrg < 100) & (amount > 100000))[0]
    if len(fraud_idx2) > 0:
        isFraud[fraud_idx2] = 1
        
    df = pd.DataFrame({
        "step": step,
        "type": types,
        "amount": amount,
        "nameOrig": nameOrig,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "nameDest": nameDest,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
        "isFraud": isFraud,
        "isFlaggedFraud": 0,
        "source_dataset": "QuantumSynthetic"
    })
    
    logger.info(f"Generated Quantum Synthetic data: shape {df.shape}, fraud count {isFraud.sum()}")
    return df

if __name__ == "__main__":
    generate_quantum_fraud_data()
