def calculate_trade_levels(price):
    target = price * 1.03
    stop = price * 0.97
    return round(target, 2), round(stop, 2)