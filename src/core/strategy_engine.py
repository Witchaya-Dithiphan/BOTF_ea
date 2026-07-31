import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import config as cfg

from src.signals.breakout_filter import breakout_signal
from src.signals.trend_filter import trend_signal
from src.signals.volume_filter import volume_signal
import pandas as pd

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data = breakout_signal(data,cfg.BB_WINDOW,cfg.BB_WINDOW_DEV)
    data = trend_signal(data,cfg.EMA_PERIOD)
    data = volume_signal(data,cfg.VOLUME_PERIOD)

    data['entry_signal'] = 0

    data.loc[(data['breakout_signal'] == 1) 
    & (data['trend_signal'] == 1) 
    & (data['volume_signal'] == 1), 
    'entry_signal'] = 1

    data.loc[(data['breakout_signal'] == -1) 
    & (data['trend_signal'] == -1) 
    & (data['volume_signal'] == 1), 
    'entry_signal'] = -1

    data = data.dropna().reset_index(drop=True)

    return data