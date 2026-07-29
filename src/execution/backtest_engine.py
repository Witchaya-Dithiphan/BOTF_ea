import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
import config as cfg
import random
random.seed(cfg.RANDOM_SEED)

if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import pandas as pd
from src.risk.position_sizer import calculate_position_size


def run_backtest(
    df: pd.DataFrame,
    initial_balance: float,
    risk_percent: float,
    tp_ratio: float,
    contract_size: float,
) -> dict:

    balance = initial_balance
    position = None  # "BUY", "SELL", หรือ None
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    current_lot = 0.0
    ambiguous_count = 0

    trades_history = []

    for row in df.itertuples():
        if position == "BUY":

            both_hit = (row.low <= sl_price) and (row.high >= tp_price)
            if both_hit:
                ambiguous_count += 1

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

            both_hit = (row.high + row.spread_usd >= sl_price) and (row.low + row.spread_usd <= tp_price)
            if both_hit:
                ambiguous_count += 1

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
                    entry_price = row.next_open + row.next_spread_usd + (row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR))
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
                    entry_price = row.next_open - (row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR))
                    sl_price = entry_price + row.sl_distance
                    tp_price = entry_price - (row.sl_distance * tp_ratio)
                    current_lot = lot
                    position = "SELL"

    return {
        "initial_balance": initial_balance,
        "final_balance": balance,
        "total_trades": len(trades_history),
        "trades": trades_history,
        "ambiguous_count": ambiguous_count
    }