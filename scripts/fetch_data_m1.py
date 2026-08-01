import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.risk.volatility_calc import calculate_volatility

import os 
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import config as cfg

if not mt5.initialize():
    print("initialize failed, error code =", mt5.last_error())
    mt5.shutdown()

symbol = "BTCUSDm"
symbol_info = mt5.symbol_info(symbol)

if not symbol_info.visible:
    mt5.symbol_info(symbol , True)

time_start = datetime(2022, 7, 29, 22, 0)
time_end   = datetime(2026, 7, 29, 22, 0)

rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, time_start, time_end)
mt5.shutdown()

if rates is None or len(rates) == 0:
    print("Failed to fetch rates or empty data returned.")
else:
    df = pd.DataFrame(rates)

    df['time'] = pd.to_datetime(df['time'], unit='s') + pd.Timedelta(hours=7)

    df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume','spread']]
    df.rename(columns={'time': 'timestamp','tick_volume': 'volume'}, inplace = True)
    df['spread_usd'] = df['spread'] * 0.01

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Sort and indexed df_m1 for quick slicing
    df = df.sort_values('timestamp')
    df = calculate_volatility(df,cfg.ATR_PERIOD,cfg.SL_ATR_MULTIPLIER)
    df = df.dropna().reset_index(drop=True)


    os.makedirs('data', exist_ok=True)
    file_path = 'data/btcusd_m1.csv'
    df.to_csv(file_path, index=False)

    print(f"Data fetched and saved to {file_path}")

    # สมมติ df_m1 โหลดข้อมูลมาแล้ว
    df['timestamp'] = pd.to_datetime(df['timestamp']) # ปรับชื่อคอลัมน์ตามจริง
    m1_counts = df.groupby(df['timestamp'].dt.floor('h')).size()

    # กรองดูเฉพาะชั่วโมงที่มีแท่งน้อยกว่า 60
    weird_hours = m1_counts[m1_counts < 60]

    print("Hours with less than 60 M1 bars:")
    print(weird_hours)