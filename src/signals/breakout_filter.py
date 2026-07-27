import pandas as pd
import ta

def breakout_signal(df: pd.DataFrame, window: int = 20, window_dev: float = 2) -> pd.DataFrame:
    data = df.copy()
    bb = ta.volatility.BollingerBands(data['close'], window=window, window_dev=window_dev)
    
    data['bb_high'] = bb.bollinger_hband()
    data['bb_low'] = bb.bollinger_lband()
    data['breakout_signal'] = 0

    data.loc[data['close'] > data['bb_high'], 'breakout_signal'] = 1
    data.loc[data['close'] < data['bb_low'], 'breakout_signal'] = -1

    return data