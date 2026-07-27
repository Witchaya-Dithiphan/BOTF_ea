import pandas as pd
import ta 

def calculate_volatility(df: pd.DataFrame, atr_period: int = 14, atr_multiple: float=1.0) -> pd.DataFrame:
    data = df.copy() 

    data['atr'] = ta.volatility.average_true_range(high=data['high'], low=data['low'], close=data['close'], window=atr_period)
    data['sl_distance'] = data['atr'] * atr_multiple
    return data