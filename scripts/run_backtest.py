import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import os 
import pandas as pd
import config as cfg
from src.execution.backtest_engine import run_backtest
from src.core.strategy_engine import generate_signals  



h1_path = Path("data/btcusd_h1.csv")
m1_path = Path("data/btcusd_m1.csv")
if not (h1_path.exists() or m1_path.exists()):
    print(f"Error: Not found data in path: {data_path}")
    exit(1)

df_h1 = pd.read_csv(h1_path)
df_m1 = pd.read_csv(m1_path)

df_h1 = generate_signals(df_h1)

initial_balance = cfg.INITIAL_BALANCE
result = run_backtest(
    df_h1=df_h1,
    df_m1=df_m1,
    initial_balance=initial_balance,
    risk_percent=cfg.RISK_PERCENT,
    tp_ratio=cfg.TP_RATIO,
    contract_size=cfg.CONTRACT_SIZE,
)

trades_df = result['trades']

os.makedirs('results', exist_ok=True)
file_path = 'results/backtest_trades.csv'
trades_df.to_csv(file_path, index=False)