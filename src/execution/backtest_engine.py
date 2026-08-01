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
    df_h1: pd.DataFrame,
    df_m1: pd.DataFrame,
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
    
        
    df_h1['timestamp'] = pd.to_datetime(df_h1['timestamp'])

    df_m1['timestamp'] = pd.to_datetime(df_m1['timestamp'])
    df_m1_indexed = df_m1.set_index('timestamp').sort_index()

    for h1_row in df_h1.itertuples():
        if position is not None:

            h1_start = h1_row.timestamp
            h1_end = h1_start + pd.Timedelta(hours=1)
            m1_bars = df_m1_indexed.loc[h1_start : h1_end-pd.Timedelta(minutes=1)]

            for m1_row in m1_bars.itertuples():

                if position == "BUY":
                    
                    # เช็กว่าแท่งนี้แตะทั้ง SL และ TP หรือไม่
                    hit_sl = m1_row.low <= sl_price
                    hit_tp = m1_row.high >= tp_price

                    # กรณีชนทั้งคู่ในแท่งเดียว ให้ถือว่าโดน SL ก่อน (Conservative Backtest)
                    if hit_sl and hit_tp:
                        hit_tp = False
                        ambiguous_count+=1

                    if hit_sl:
                        slippage = h1_row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR)
                        pnl = (sl_price - entry_price - slippage) * current_lot * contract_size
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
                        break
                    elif hit_tp:
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
                        break

                elif position == "SELL":
                    
                    # Ask Price = Bid Price + Spread
                    ask_high = m1_row.high + m1_row.spread_usd
                    ask_low = m1_row.low + m1_row.spread_usd

                    # เช็กว่าแท่งนี้แตะทั้ง SL และ TP หรือไม่
                    hit_sl = ask_high >= sl_price
                    hit_tp = ask_low <= tp_price

                    # กรณีชนทั้งคู่ในแท่งเดียว ให้ถือว่าโดน SL ก่อน (Conservative Backtest)
                    if hit_sl and hit_tp:
                        hit_tp = False
                        ambiguous_count+=1
                
                    if hit_sl:
                        slippage = h1_row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR)
                        pnl = (entry_price - sl_price + slippage) * current_lot * contract_size
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
                        break

                    elif hit_tp:
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
                        break

        elif position is None and h1_row.entry_signal != 0:

            next_m1_time = h1_row.timestamp + pd.Timedelta(hours=1)

            if next_m1_time in df_m1_indexed.index:
                next_m1 = df_m1_indexed.loc[next_m1_time]

                if isinstance(next_m1, pd.DataFrame):
                    next_m1 = next_m1.iloc[0]

                slippage = h1_row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR)

                if h1_row.entry_signal == 1:
                    lot = calculate_position_size(
                        account_balance=balance,
                        risk_percent=risk_percent,
                        sl_distance=h1_row.sl_distance,
                        contract_size=contract_size,
                    )

                    if lot > 0:
                        entry_price = next_m1['open'] + next_m1['spread_usd'] + slippage
                        sl_price = entry_price - h1_row.sl_distance
                        tp_price = entry_price + (h1_row.sl_distance * tp_ratio)
                        current_lot = lot
                        position = "BUY"

                elif h1_row.entry_signal == -1:
                    lot = calculate_position_size(
                        account_balance=balance,
                        risk_percent=risk_percent,
                        sl_distance=h1_row.sl_distance,
                        contract_size=contract_size,
                    )

                    if lot > 0:
                        entry_price = next_m1['open'] - slippage
                        sl_price = entry_price + h1_row.sl_distance
                        tp_price = entry_price - (h1_row.sl_distance * tp_ratio)
                        current_lot = lot
                        position = "SELL"

    return {
        "initial_balance": initial_balance,
        "final_balance": balance,
        "total_trades": len(trades_history),
        "trades": trades_history,
        "ambiguous_count": ambiguous_count
    }