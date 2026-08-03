import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import pandas as pd
import config as cfg
import math

file_path = "results/backtest_trades.csv"
df = pd.read_csv(file_path)

initial_balance = cfg.INITIAL_BALANCE
final_balance = df['balance'].iloc[-1]
net_profit = final_balance - initial_balance
total_return = net_profit  / initial_balance

df['entry_time'] = pd.to_datetime(df['entry_time'])
df['exit_time'] = pd.to_datetime(df['exit_time'])
total_days = (df['exit_time'].max() - df['exit_time'].min()).days
yearly_return = ((final_balance / initial_balance) ** (365 / total_days) - 1)

total_trades = len(df)
win_trades = df[df['result'] == "TP"]
win_rate = len(win_trades) / total_trades if total_trades > 0 else 0

Expectancy_usd = df['pnl'].mean()
Expectancy_r = df['r_multiple'].mean()


print(f"Initial Balance: {initial_balance}")
print(f"Final Balance: {final_balance}")
print(f"Total Return: {total_return:.2%} , (+ {total_return * initial_balance:.2f} USD)")
print(f"Yearly Return: {yearly_return:.2%}")
print(f"Win Rate: {win_rate:.2%} ({len(win_trades)}/{total_trades})")
print(f"Expectancy (USD): {Expectancy_usd:.2f} USD per trade")
print(f"Expectancy (R): {Expectancy_r:.2f} R per trade")



