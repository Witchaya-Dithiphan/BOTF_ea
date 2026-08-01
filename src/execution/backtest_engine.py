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
    active_trade = None  # ใช้เก็บข้อมูลเทรดปัจจุบันแทนตัวแปรแยกย่อย
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
                    mfe_val = (m1_row.high - entry_price) * current_lot * contract_size
                    mae_val = (m1_row.low - entry_price) * current_lot * contract_size

                    active_trade["MFE"] = max(active_trade["MFE"],mfe_val)
                    active_trade["MAE"] = min(active_trade["MAE"], mae_val)

                    hit_sl = m1_row.low <= sl_price
                    hit_tp = m1_row.high >= tp_price

                elif position == "SELL":
                    ask_high = m1_row.high + m1_row.spread_usd
                    ask_low = m1_row.low + m1_row.spread_usd

                    mfe_val = (entry_price - ask_low) * current_lot * contract_size
                    mae_val = (entry_price - ask_high) * current_lot * contract_size

                    active_trade["MFE"] = max(active_trade["MFE"],mfe_val)
                    active_trade["MAE"] = min(active_trade["MAE"],mae_val)

                    hit_sl = ask_high >= sl_price
                    hit_tp = ask_low <= tp_price

                if hit_sl and hit_tp:
                    hit_tp = False
                    ambiguous_count += 1

                if hit_sl or hit_tp:
                    exit_time = m1_row.Index
                    result = "SL" if hit_sl else "TP"
                    exit_price = sl_price if hit_sl else tp_price
                    
                    if position == "BUY":
                        
                        if hit_sl:
                            slippage = h1_row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR)
                            pnl = (exit_price - entry_price - slippage) * current_lot * contract_size
                            exit_price -= slippage
                        else:
                            pnl = (exit_price - entry_price) * current_lot * contract_size
                    else:
                        
                        if hit_sl:
                            slippage = h1_row.atr*random.uniform(cfg.SLIPPAGE_MIN_FACTOR,cfg.SLIPPAGE_MAX_FACTOR)
                            pnl = (entry_price - exit_price - slippage) * current_lot * contract_size
                            exit_price += slippage
                        else:
                            pnl = (entry_price - exit_price) * current_lot * contract_size

                    balance += pnl
                    pnl_percent = (pnl/(balance-pnl) * 100) if balance - pnl > 0 else 0.0

                    risk_amount = active_trade["sl_distance"] * current_lot * contract_size
                    r_multiple = (pnl/risk_amount) if risk_amount > 0 else 0.0

                    active_trade.update({
                        "exit_time": exit_time,
                        "exit_price": exit_price,
                        "result": result,
                        "pnl": pnl,
                        "pnl_percent": round(pnl_percent,4),
                        "r_multiple": round(r_multiple,4),
                        "balance": balance,
                        "MAE": round(active_trade["MAE"],2),
                        "MFE": round(active_trade["MFE"],2),
                    })

                    trades_history.append(active_trade)
                    position = None
                    active_trade = None
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
                        position = "BUY"
                        active_trade = {
                            "entry_time": next_m1.name,
                            "type": "BUY",
                            "lot_size": lot,
                            "entry_price": entry_price,
                            "sl_price": sl_price,
                            "tp_price": tp_price,
                            "sl_distance": h1_row.sl_distance,
                            "atr": h1_row.atr,
                            "spread": next_m1['spread_usd'],
                            "MAE": 0.0,
                            "MFE": 0.0,
                            "exit_time": None,
                            "exit_price": 0.0,
                            "result": "",
                            "pnl": 0.0,
                            "pnl_percent": 0.0,
                            "r_multiple": 0.0,
                            "balance": balance
                        }
                        current_lot = lot

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
                        position = "SELL"
                        active_trade = {
                            "entry_time": next_m1.name,
                            "type": "SELL",
                            "lot_size": lot,
                            "entry_price": entry_price,
                            "sl_price":  sl_price,
                            "tp_price": tp_price,
                            "sl_distance": h1_row.sl_distance,
                            "atr": h1_row.atr,
                            "spread": next_m1['spread_usd'],
                            "MAE": 0.0,
                            "MFE": 0.0,
                            "exit_time": None,
                            "exit_price": 0.0,
                            "result": "",
                            "pnl": 0.0,
                            "pnl_percent": 0.0,
                            "r_multiple": 0.0,
                            "balance": balance
                        }
                        current_lot = lot

    if position is not None:
        last_m1 = df_m1_indexed.iloc[-1]
        exit_price = last_m1['open'] if position == "BUY" else last_m1['open'] - last_m1['spread_usd']
        pnl = (exit_price - entry_price) * current_lot * contract_size if position == "BUY" \
            else (entry_price - exit_price) * current_lot * contract_size
        balance += pnl
        pnl_percent = (pnl/(balance-pnl) * 100) if balance - pnl > 0 else 0.0

        risk_amount = active_trade["sl_distance"] * current_lot * contract_size
        r_multiple = (pnl/risk_amount) if risk_amount > 0 else 0.0
        active_trade.update({
            "exit_time": last_m1.name, 
            "exit_price": exit_price,
            "result": "EOD_CLOSE", 
            "pnl": pnl,
            "pnl_percent": round(pnl_percent,4),
            "r_multiple": round(r_multiple,4),
            "balance": balance,
            "MAE": round(active_trade["MAE"],2),
            "MFE": round(active_trade["MFE"],2),
        })
        trades_history.append(active_trade)
    trades = pd.DataFrame(trades_history)

    return {
        "trades": trades,
        "ambiguous_count": ambiguous_count
    }