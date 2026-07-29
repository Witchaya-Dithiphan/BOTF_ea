import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import config as cfg

def is_valid_session(time_stamp, spread_usd) -> bool:
    if not cfg.ENABLE_TIME_FILTER:
        return True

    hour = time_stamp.hour
    weekday = time_stamp.weekday()

    if hour < cfg.TRADING_START_HOUR or hour >= cfg.TRADING_END_HOUR:
        return False
    
    if weekday == 4 and hour > 20:
        return False

    if weekday >= 5:
        return False

    if spread_usd > cfg.MAX_ALLOWED_SPREAD:
        return False

    return True