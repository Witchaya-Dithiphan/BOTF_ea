import sys
from pathlib import Path

# ดึง Root Directory (BOTF_ea) เข้า sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))


from src.risk.position_sizer import calculate_position_size
import pandas as pd

def run_backtest(df: pd.DataFrame, initial_balance: float = 300.0, risk_percent: float = 0.03, tp_ratio: float = 2.0, contract_size: float=1.0) -> dict:

    balance = initial_balance
    position = None # BUY 1, SELL -1, None 0
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    current_lot = 0.0

    trades_history = []

    for index,row in df.iterrows():
        if position is not None:
            if position == "BUY":
                if row['high'] >= tp_price:
                    pnl = (tp_price-entry_price)*current_lot*contract_size
                    balance += pnl
                    trades_history.append({
                        "type": "BUY",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    })
                    position = None
                elif row['low'] <= sl_price:
                    pnl = (sl_price-entry_price)*current_lot*contract_size
                    balance += pnl
                    trades_history.append({
                        "type": "BUY",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    })
                    position = None
            elif position == "SELL":
                if row['low'] <= tp_price:
                    pnl = (entry_price-tp_price)*current_lot*contract_size
                    balance += pnl
                    trades_history.append({
                        "type": "BUY",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    })
                    position = None
                elif row['high'] >= sl_price:
                    pnl = (entry_price-sl_price)*current_lot*contract_size
                    balance += pnl
                    trades_history.append({
                        "type": "BUY",
                        "result": "TP",
                        "pnl": pnl,
                        "entry": entry_price,
                        "exit": tp_price,
                        "balance": balance,
                    })
                    position = None
                    
        else:
            if row['entry_signal'] == 1:
                entry_price = row['close']
                sl_price = entry_price - row['sl_distance']
                tp_price = entry_price + (row['sl_distance']*tp_ratio)
                current_lot = calculate_position_size(account_balance=balance,risk_percent=risk_percent,sl_distance=row['sl_distance'],contract_size=contract_size,)
                position = "BUY"
            elif row['entry_signal'] == -1:
                entry_price = row['close']
                sl_price = entry_price + row['sl_distance']
                tp_price = entry_price - (row['sl_distance']*tp_ratio)
                current_lot = calculate_position_size(account_balance=balance,risk_percent=risk_percent,sl_distance=row['sl_distance'],contract_size=contract_size,)
                position = "SELL"


    return {
        'initial_balance': initial_balance,
        'final_balance': balance,
        'total_trades': len(trades_history),
        'trades': trades_history,
    }