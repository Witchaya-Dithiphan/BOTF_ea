import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import config as cfg
from src.execution.backtest_engine import run_backtest
from src.core.strategy_engine import generate_signals  


def main():

    h1_path = Path("data/btcusd_h1.csv")
    m1_path = Path("data/btcusd_m1.csv")
    if not (h1_path.exists() or m1_path.exists()):
        print(f"Error: Not found data in path: {data_path}")
        return

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

    trades = result['trades']
    total_trades = result['total_trades']
    final_balance = result['final_balance']
    ambiguous_count = result['ambiguous_count']
    net_pnl = final_balance - initial_balance
    return_pct = (net_pnl / initial_balance) * 100

    win_trades = [t for t in trades if t['result'] == 'TP']
    win_count = len(win_trades)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0

    print("\n" + "=" * 40)
    print("BACKTEST SUMMARY REPORT")
    print("=" * 40)
    print(f"Initial Balance : ${initial_balance:,.2f}")
    print(f"Final Balance   : ${final_balance:,.2f}")
    print(f"Net Profit/Loss : ${net_pnl:,.2f} ({return_pct:+.2f}%)")
    print(f"Total Trades    : {total_trades} trades")
    print(f"Win Rate        : {win_rate:.2f}% ({win_count}/{total_trades})")
    print(f"Ambiguous_count        : {ambiguous_count}")
    print("=" * 40)

    trades_df = pd.DataFrame(result['trades'])

    print("\n--- Breakdown by Result ---")
    print(trades_df.groupby(['type', 'result'])['pnl'].agg(['count', 'sum', 'mean']))

if __name__ == "__main__":
  main()