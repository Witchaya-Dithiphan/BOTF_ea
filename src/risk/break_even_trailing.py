def trailing_sl(
    position_type: str,
    entry_price: float,
    current_sl: float,
    current_high: float,
    current_low: float,
    initial_sl_distance: float,
    be_trigger_r: float,
) -> float:
    new_sl = current_sl

    if position_type == "BUY":
        profit_dist = current_high-entry_price

        if profit_dist >= initial_sl_distance*be_trigger_r:
            if new_sl < entry_price:
                new_sl = entry_price-(initial_sl_distance*0.5)

    elif position_type == "SELL":
        profit_dist = entry_price - current_low

        if profit_dist >= (initial_sl_distance * be_trigger_r):
            if new_sl > entry_price:
                new_sl = entry_price+(initial_sl_distance*0.5)
    return new_sl