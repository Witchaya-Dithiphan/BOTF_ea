import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import pandas as pd
from src.risk.position_sizer import calculate_position_size


def run_backtest(
    df: pd.DataFrame,
    initial_balance: float = 300.0,
    risk_percent: float = 0.03,
    tp_ratio: float = 2.0,
    contract_size: float = 1.0,
) -> dict:

    balance = initial_balance
    position = None  # "BUY", "SELL", หรือ None
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    current_lot = 0.0

    trades_history = []

    for row in df.itertuples():
        if position == "BUY":
            if row.low <= sl_price:
                pnl = (sl_price - entry_price) * current_lot * contract_size
                balance += pnl
                trades_history.append(
                    {
                        "type": "BUY",
                        "result": "SL",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": sl_price,
                        "balance": balance,
                    }
                )
                position = None
            elif row.high >= tp_price:
                pnl = (tp_price - entry_price) * current_lot * contract_size
                balance += pnl
                trades_history.append(
                    {
                        "type": "BUY",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    }
                )
                position = None

        elif position == "SELL":
            if row.high + row.spread_usd>= sl_price:
                pnl = (entry_price - sl_price) * current_lot * contract_size
                balance += pnl
                trades_history.append(
                    {
                        "type": "SELL",
                        "result": "SL",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": sl_price,
                        "balance": balance,
                    }
                )
                position = None

            elif row.low + row.spread_usd<= tp_price:
                pnl = (entry_price - tp_price) * current_lot * contract_size
                balance += pnl
                trades_history.append(
                    {
                        "type": "SELL",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    }
                )
                position = None

        elif position is None:
            if row.entry_signal == 1:
                lot = calculate_position_size(
                    account_balance=balance,
                    risk_percent=risk_percent,
                    sl_distance=row.sl_distance,
                    contract_size=contract_size,
                )

                if lot > 0:
                    entry_price = row.next_open + row.next_spread_usd
                    sl_price = entry_price - row.sl_distance
                    tp_price = entry_price + (row.sl_distance * tp_ratio)
                    current_lot = lot
                    position = "BUY"

            elif row.entry_signal == -1:
                lot = calculate_position_size(
                    account_balance=balance,
                    risk_percent=risk_percent,
                    sl_distance=row.sl_distance,
                    contract_size=contract_size,
                )

                if lot > 0:
                    entry_price = row.next_open
                    sl_price = entry_price + row.sl_distance
                    tp_price = entry_price - (row.sl_distance * tp_ratio)
                    current_lot = lot
                    position = "SELL"

    return {
        "initial_balance": initial_balance,
        "final_balance": balance,
        "total_trades": len(trades_history),
        "trades": trades_history,
    }