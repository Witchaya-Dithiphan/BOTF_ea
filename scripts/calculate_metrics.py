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
max_drawdown_usd = df['drawdown_usd'].max()
df['drawdown_pct'] = (df['drawdown_usd'] / df['peak'])*100
max_drawdown = df['drawdown_pct'].max()
df['is_win'] = df['pnl'] > 0
streak_groups = (df['is_win'] != df['is_win'].shift()).cumsum()
streaks = df.groupby(streak_groups)['is_win'].agg(is_win_status='first', streak_length='size')
max_consecutive_wins = streaks[streaks['is_win_status'] == True]['streak_length'].max()
max_consecutive_losses = streaks[streaks['is_win_status'] == False]['streak_length'].max()
recovery_factor = net_profit / max_drawdown_usd if max_drawdown_usd > 0 else 0

avg_mae = df['MAE'].mean()
avg_mfe = df['MFE'].mean() 
profit_efficiency = avg_mfe / abs(avg_mae)


df['spread_cost'] = df['spread'] * df['lot_size'] * cfg.CONTRACT_SIZE
avg_spread = df['spread_cost'].mean()
cost = df['spread_cost'].sum()

# 1. แปลงกำไรขาดทุนแต่ละไม้ให้อยู่ในรูปอัตราผลตอบแทนเทียบกับเงินตั้งต้น
trade_returns = df['pnl'] / initial_balance
avg_trade_return = trade_returns.mean()
std_trade_return = trade_returns.std()
# 4. เข้าสูตรคำนวณ (ป้องกันกรณีหารด้วย 0)
trade_sharpe = avg_trade_return / std_trade_return if std_trade_return > 0 else 0
negative_returns = trade_returns[trade_returns < 0]
downside_std = negative_returns.std() if not negative_returns.empty else 0
trade_sortino = avg_trade_return / downside_std if downside_std > 0 else 0
df['trade_duration'] = (df['exit_time'] - df['entry_time']) 
avg_trade_duration = df['trade_duration'].dt.total_seconds().mean() / 3600 


print(f"Initial Balance: {initial_balance}")
print(f"Final Balance: {final_balance:.2f}")
print(f"Net Profit: {total_return:.2%} , (+ {net_profit:.2f} USD)")
print(f"Yearly Return: {yearly_return:.2%}")
print(f"Expectancy (USD): {Expectancy_usd:.2f} USD per trade")
print(f"Expectancy (R): {Expectancy_r:.4f} R per trade")

print(f"Win Rate: {win_rate:.2%} ({win_trades}/{total_trades} trades)")
print(f"Profit Factor: {profit_factor:.4f}")
print(f"Average Win: {avg_win:.2f} ({win_trades}) , Average Loss: {avg_loss:.2f} ({loss_trades})")
print(f"Win/Loss Ratio: {winloss_ratio:.2f}")
print(f"Average R-Multiple: {avg_r:.4f}")

print(f"Max Drawdown: {max_drawdown:.2f}")
print(f"Max consecutive wins: {max_consecutive_wins}")
print(f"Max consecutive losses: {max_consecutive_losses}")
print(f"Recovery factor: {recovery_factor:.2f}")

print(f"Average MAE: {avg_mae:.2f}")
print(f"Average MFE: {avg_mfe:.2f}")
print(f"Profit Efficiency: {profit_efficiency:.4f}")

print(f"Average spread impact: {avg_spread:.2f}")
print(f"Total Cost of Spread: {cost}")

print(f"Sharpe Ratio: {trade_sharpe:.4f}")
print(f"Sortino Ratio: {trade_sortino:.4f}")
print(f"Average Duration: {avg_trade_duration} hours")