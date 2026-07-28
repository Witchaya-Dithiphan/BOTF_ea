import pandas as pd
import ta 

def calculate_volatility(df: pd.DataFrame, atr_period: int = 14, atr_multiple: float=2.1) -> pd.DataFrame:
    data = df.copy() 

    data['atr'] = ta.volatility.average_true_range(high=data['high'], low=data['low'], close=data['close'], window=atr_period, fillna=False,)
    data['sl_distance'] = data['atr'] * atr_multiple
    return data