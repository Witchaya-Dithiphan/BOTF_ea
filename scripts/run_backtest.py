import sys
from pathlib import Path

# ดึง Root Directory (BOTF_ea) เข้า sys.path เพื่อให้ import จาก src ได้
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.execution.backtest_engine import run_backtest
from src.core.strategy_engine import generate_signals  # ปรับชื่อตามฟังก์ชันของคุณ
from src.risk.volatility_calc import calculate_volatility  # ปรับชื่อตามฟังก์ชันของคุณ


def main():
    print("🚀 Starting Backtest System...\n")

    # 1. โหลดข้อมูลราคา
    data_path = Path("data/btcusd_h1_2years.csv")
    if not data_path.exists():
        print(f"❌ Error: ไม่พบไฟล์ข้อมูลที่ {data_path}")
        return

    print(f"📖 Loading data from: {data_path}")
    df = pd.read_csv(data_path)

    # 2. คำนวณ Signal และ Volatility
    print("⚙️ Generating strategy signals & volatility parameters...")
    df = calculate_volatility(df)
    df = generate_signals(df)

    # 3. รัน Backtest
    print("🔄 Running Backtest Engine...")
    initial_balance = 3000.0
    result = run_backtest(
        df=df,
        initial_balance=initial_balance,
        risk_percent=0.03,  # เสี่ยงไม้ละ 3%
        tp_ratio=2.0,  # RR 1:2
        contract_size=1.0,
    )

    # 4. ประมวลผลและแสดงรายงาน (Report)
    trades = result['trades']
    total_trades = result['total_trades']
    final_balance = result['final_balance']
    net_pnl = final_balance - initial_balance
    return_pct = (net_pnl / initial_balance) * 100

    # คำนวณ Win Rate
    win_trades = [t for t in trades if t['result'] == 'TP']
    win_count = len(win_trades)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0

    print("\n" + "=" * 40)
    print("📊 BACKTEST SUMMARY REPORT")
    print("=" * 40)
    print(f"Initial Balance : ${initial_balance:,.2f}")
    print(f"Final Balance   : ${final_balance:,.2f}")
    print(f"Net Profit/Loss : ${net_pnl:,.2f} ({return_pct:+.2f}%)")
    print(f"Total Trades    : {total_trades} trades")
    print(f"Win Rate        : {win_rate:.2f}% ({win_count}/{total_trades})")
    print("=" * 40)

    trades_df = pd.DataFrame(result['trades'])

    # ดูสรุปแยกฝั่ง BUY / SELL และ TP / SL
    print("\n--- Breakdown by Result ---")
    print(trades_df.groupby(['type', 'result'])['pnl'].agg(['count', 'sum', 'mean']))

    print("\n--- First 10 Trades ---")
    print(
        trades_df[
            ['type', 'result', 'entry', 'exit', 'pnl', 'balance']
        ].head(10)
    )

if __name__ == "__main__":
  main()