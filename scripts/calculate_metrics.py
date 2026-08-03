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
win_trades = len(df[df['result'] == "TP"])
loss_trades = total_trades - win_trades
win_rate = win_trades / total_trades if total_trades > 0 else 0

Expectancy_usd = df['pnl'].mean()
Expectancy_r = df['r_multiple'].mean()
gross_profits = df[df['pnl'] > 0]['pnl'].sum()
gross_losses = abs(df[df['pnl'] < 0]['pnl'].sum())
profit_factor = gross_profits / gross_losses
avg_win = gross_profits/win_trades
avg_loss = gross_losses/loss_trades
avg_r = df['r_multiple'].mean()
winloss_ratio = avg_win / avg_loss

df['peak'] = df['balance'].cummax()
df['drawdown_usd'] = df['peak'] - df['balance']
df['drawdown_pct'] = (df['drawdown_usd'] / df['peak'])*100
max_drawdown = df['drawdown_pct'].max()
 

print(f"Initial Balance: {initial_balance}")
print(f"Final Balance: {final_balance}")
print(f"Net Profit: {total_return:.2%} , (+ {net_profit:.2f} USD)")
print(f"Yearly Return: {yearly_return:.2%}")
print(f"Expectancy (USD): {Expectancy_usd:.2f} USD per trade")
print(f"Expectancy (R): {Expectancy_r:.4f} R per trade")

print(f"Win Rate: {win_rate:.2%} ({win_trades}/{total_trades})")
print(f"Profit Factor: {profit_factor:.4f}")
print(f"Average Win: {avg_win} ({win_trades}) , Average Loss: {avg_loss} ({loss_trades})")
print(f"Win/Loss Ratio: {winloss_ratio:.2f}")
print(f"Average R-Multiple: {avg_r:.4f}")

print(f"Max Drawdown: {max_drawdown}")