import pandas as pd

def calculate_position_size(account_balance: float,risk_percent: float, sl_distance: float, contract_size = 1.0) -> float:
    risk_amount = account_balance*risk_percent

    if sl_distance <= 0 or pd.isna(sl_distance) : return 0.0

    raw_lot = risk_amount/(sl_distance*contract_size)
    lot_size = round(raw_lot,2)

    if lot_size <  0.01:
        lot_size = 0.01
    elif lot_size > 100.0:
        lot_size = 100.0

    return lot_size

# if __name__ == "__main__":
#   balance = 300.0  # พอร์ต $300
#   risk = 0.03  # เสี่ยง 3% ($9)
#   sl_dist = 600.0  # ระยะ Stop Loss $300 (เช่น BTC)
#   contract = 1.0  # 1 Lot = 1 BTC

#   lot = calculate_position_size(
#       account_balance=balance,
#       risk_percent=risk,
#       sl_distance=sl_dist,
#       contract_size=contract,
#   )

#   print(f"Account Balance: ${balance}")
#   print(f"Risk Amount: ${balance * risk}")
#   print(f"Calculated Lot Size: {lot} Lots")