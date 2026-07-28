import pandas as pd
import ta

def trend_signal(df: pd.DataFrame, ema_period: int = 200) -> pd.DataFrame:
    data = df.copy()
    data['ema200'] = ta.trend.ema_indicator(data['close'], window=ema_period, fillna=False)
    data['trend_signal'] = 0

    data.loc[data['close'] > data['ema200'], 'trend_signal'] = 1
    data.loc[data['close'] < data['ema200'], 'trend_signal'] = -1

    return data