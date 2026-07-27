import os 
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd

if not mt5.initialize():
    print("initialize failed, error code =", mt5.last_error())
    mt5.shutdown()

symbol = "BTCUSDm"
symbol_info = mt5.symbol_info(symbol)

if not symbol_info.visible:
    mt5.symbol_info(symbol , True)

time_now = datetime.now()
time_start = time_now - timedelta(days=365*2)

rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, time_start, time_now)
mt5.shutdown()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume','spread']]
df.rename(columns={'time': 'timestamp','tick_volume': 'volume'}, inplace = True)

os.makedirs('data', exist_ok=True)
file_path = 'data/btcusd_h1_2years.csv'
df.to_csv(file_path, index=False)

print(f"Data fetched and saved to {file_path}")