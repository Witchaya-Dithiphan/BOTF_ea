import pandas as pd
import ta

def volume_signal(df: pd.DataFrame, volume_period: int=20) -> pd.DataFrame:
    data = df.copy()
    data['volume_sma'] = ta.trend.sma_indicator(data['volume'], window=volume_period, fillna=False)
    data['volume_signal'] = 0

    data.loc[data['volume'] > data['volume_sma'], 'volume_signal'] = 1

    return data