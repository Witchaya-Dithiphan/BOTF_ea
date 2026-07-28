import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.execution.backtest_engine import run_backtest
from src.core.strategy_engine import generate_signals  
from src.risk.volatility_calc import calculate_volatility


def main():

    data_path = Path("data/btcusd_h1_3years.csv")
    if not data_path.exists():
        print(f"Error: Not found data in path: {data_path}")
        return

    df = pd.read_csv(data_path)

    df = calculate_volatility(df)
    df = generate_signals(df)

    initial_balance = 300.0
    result = run_backtest(
        df=df,
        initial_balance=initial_balance,
        risk_percent=0.03,
        tp_ratio=2.0,
        contract_size=1.0,
    )

    trades = result['trades']
    total_trades = result['total_trades']
    final_balance = result['final_balance']
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
    print("=" * 40)

    trades_df = pd.DataFrame(result['trades'])

    print("\n--- Breakdown by Result ---")
    print(trades_df.groupby(['type', 'result'])['pnl'].agg(['count', 'sum', 'mean']))

    # print("\n--- First 10 Trades ---")
    # print(
    #     trades_df[
    #         ['type', 'result', 'entry', 'exit', 'pnl', 'balance']
    #     ].head(30)
    # )

if __name__ == "__main__":
  main()