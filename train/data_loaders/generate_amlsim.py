import pandas as pd
import numpy as np
import logging
import os
from train import config

logger = logging.getLogger(__name__)

def generate_amlsim_data(num_transactions: int = 50000) -> pd.DataFrame:
    """
    Generates a synthetic dataset mimicking IBM AMLSim output.
    AMLSim typically produces accounts.csv, transactions.csv, etc.
    We mock these and combine them into a dataframe matching the PaySim schema
    to allow unified processing.
    """
    logger.info(f"Generating synthetic AMLSim data ({num_transactions} transactions)...")
    np.random.seed(42)
    
    # Generate Account IDs
    num_accounts = num_transactions // 10
    accounts = [f"A{i:06d}" for i in range(num_accounts)]
    
    # Generate basic transactions
    step = np.random.randint(1, 744, size=num_transactions)
    types = np.random.choice(["TRANSFER", "CASH_OUT", "CASH_IN", "PAYMENT"], size=num_transactions, p=[0.4, 0.4, 0.1, 0.1])
    amount = np.random.exponential(scale=5000, size=num_transactions)
    
    nameOrig = np.random.choice(accounts, size=num_transactions)
    nameDest = np.random.choice(accounts, size=num_transactions)
    
    oldbalanceOrg = np.random.uniform(0, 100000, size=num_transactions)
    newbalanceOrig = np.where(types == "CASH_IN", oldbalanceOrg + amount, np.maximum(0, oldbalanceOrg - amount))
    
    oldbalanceDest = np.random.uniform(0, 100000, size=num_transactions)
    newbalanceDest = np.where(np.isin(types, ["TRANSFER", "CASH_OUT", "PAYMENT"]), oldbalanceDest + amount, np.maximum(0, oldbalanceDest - amount))
    
    # Inject AML-specific Fraud Patterns (e.g. large transfers, rapid movement)
    # Fraud cases
    isFraud = np.zeros(num_transactions, dtype=int)
    
    # Pattern 1: Large transfer > 50000 and zero old balance dest
    fraud_idx1 = np.where((types == "TRANSFER") & (amount > 50000) & (oldbalanceDest < 100))[0]
    if len(fraud_idx1) > 0:
        fraud_sampled = np.random.choice(fraud_idx1, size=int(len(fraud_idx1) * 0.1), replace=False)
        isFraud[fraud_sampled] = 1
        
    # Pattern 2: Circular transactions (mocked by high frequency in same step)
    fraud_idx2 = np.random.choice(np.arange(num_transactions), size=int(num_transactions * 0.01), replace=False)
    isFraud[fraud_idx2] = 1
    amount[fraud_idx2] = amount[fraud_idx2] * 5 # Inflate amount
    
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
        "isFlaggedFraud": np.where(amount > 200000, 1, 0),
        "source_dataset": "AMLSim"
    })
    
    # Save simulated mock files
    aml_dir = config.DATA_DIR / "amlsim_mock"
    os.makedirs(aml_dir, exist_ok=True)
    df.to_csv(aml_dir / "transactions.csv", index=False)
    
    logger.info(f"Generated AMLSim data: shape {df.shape}, fraud count {isFraud.sum()}")
    return df

if __name__ == "__main__":
    generate_amlsim_data()
