import pandas as pd

def calculate_position_size(account_balance: float,risk_percent: float, sl_distance: float, contract_size = 1.0) -> float:
    risk_amount = account_balance*risk_percent

    if sl_distance <= 0 or pd.isna(sl_distance) : return 0.0

    raw_lot = risk_amount/(sl_distance*contract_size)
    lot_size = int(raw_lot * 100) / 100.0

    if lot_size <  0.01:
        lot_size = 0.0
    elif lot_size > 100.0:
        lot_size = 100.0

    return lot_size